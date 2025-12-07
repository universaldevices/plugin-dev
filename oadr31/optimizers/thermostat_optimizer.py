from iox import IoXWrapper
from nucore import Node
from .base_optimizer import BaseOptimizer
from opt_config.ven_settings import GridState, VENSettings
    
class ThermostatOptimizer(BaseOptimizer):
    """
    Thermostat optimization algorithm for demand response across four grid states:
    Normal, Moderate, High, and Emergency (Special).
    
    The algorithm adjusts thermostat setpoints based on grid conditions while respecting
    user comfort preferences. If a customer manually changes setpoints during an active
    optimization state, the system opts out until the next day.
    """

    def __init__(self, ven_settings: VENSettings, node:Node, iox:IoXWrapper ):
        """
        Initialize the thermostat optimizer.
        
        Args:
            ven_settings: VENSettings instance containing configuration
            node: Node instance associated with this optimizer
            iox: IoXWrapper instance for interacting with IoX
        """
        super().__init__(ven_settings, node, iox)
        # Track last applied setpoints to detect user changes
        self.current_cool_sp = None
        self.current_heat_sp = None
        self.current_temp = None
        self.current_mode = None
        self.last_applied_cool_sp = None
        self.last_applied_heat_sp = None
        self.cool_prec=None
        self.heat_prec=None
        self.cool_uom=None
        self.heat_uom=None
        
    def _get_min_offset(self):
        return self.ven_settings.min_setpoint_offset

    def _get_max_offset(self):
        return self.ven_settings.max_setpoint_offset

    def _update_settings(self):
        self.cool_baseline = self.ven_settings.cooling_setpoint
        self.heat_baseline = self.ven_settings.heating_setpoint

    def _check_user_override(self, grid_state):
        """
        Check if the user has manually changed setpoints during an active optimization state.
        If detected, opt out of optimization until the next day.
        
        Args:
            current_cool_sp: Current cooling setpoint from thermostat
            current_heat_sp: Current heating setpoint from thermostat
            grid_state: Current grid state
            
        Returns:
            True if user override detected and opted out, False otherwise
        """
        # Only check for overrides during non-normal states
        if grid_state == GridState.NORMAL: 
            return False
        
        # If we haven't applied any setpoints yet, no override possible
        if self.last_applied_cool_sp is None and self.last_applied_heat_sp is None:
            return False
        
        # Check if current setpoints differ from what we last applied
        # Allow for small floating point differences
        cool_changed = False
        heat_changed = False
        if self.current_cool_sp is not None and self.last_applied_cool_sp is not None:
            cool_changed = abs(self.current_cool_sp - self.last_applied_cool_sp) != 0
        
        if self.current_heat_sp is not None and self.last_applied_heat_sp is not None:
            heat_changed = abs(self.current_heat_sp - self.last_applied_heat_sp) != 0 

        if cool_changed or heat_changed:
            if heat_changed:
                self.history.insert_device_history(
                self.history.insert(self.node.adress, "Heat Setpoint", grid_state=grid_state, requested_value=self.last_applied_heat_sp,
                                   current_value=self.current_heat_sp, opt_status="User Override"), opt_expires_at=self._get_opt_out_expiry().isoformat()) 
            if cool_changed:
                self.history.insert_device_history(
                self.history.insert(self.node.adress, "Cool Setpoint", grid_state=grid_state, requested_value=self.last_applied_cool_sp,
                                   current_value=self.current_cool_sp, opt_status="User Override"), opt_expires_at=self._get_opt_out_expiry().isoformat()) 
            return True
        
        return False
    
    def _adjust_setpoints(self, cool_value:float, heat_value:float): 
        """
        Generate command to set thermostat setpoints.
        
        Args:
            command: 'set_cool_setpoint' or 'set_heat_setpoint'
            value: New setpoint value
            
        Returns:
            Command dictionary to send to IoX
        """
        commands = []
        if cool_value is not None: 
            commands.append({
            'device_id': self.node.address,
            'command_id': 'CLISPC', 
            'command_params': [
                {'id': 'n/a', 'value': cool_value, 'uom': self.cool_uom, 'prec': self.cool_prec}
            ]
            })
        if heat_value is not None: 
            commands.append({
            'device_id': self.node.address,
            'command_id': 'CLISPH', 
            'command_params': [
                {'id': 'n/a', 'value': heat_value, 'uom': self.heat_uom, 'prec': self.heat_prec}
            ]
            })

        if len(commands) > 0:
            response = self.iox.send_commands(commands)
            if response is None or len(response) == 0:
                print ('ThermostatOptimizer: Failed to send setpoint adjustment commands to IoX.')
                return None, None
            if len(response) == 2:
                if response[0] is None or response[0].status_code != 200:
                    cool_value = None
                if response[1] is None or response[1].status_code != 200:
                    heat_value = None
            elif len(response) == 1:
                if response[0] is None or response[0].status_code != 200:
                    if commands[0]['command_id'] == 'CLISPC':
                        cool_value = None
                    elif commands[0]['command_id'] == 'CLISPH':
                        heat_value = None
            return cool_value, heat_value
        return None, None

    async def _optimize(self, grid_state):
        """
        Optimize thermostat setpoints based on current grid state and comfort baselines.
        We assume that the grid_state has changed.
       
        Algorithm:
        - Normal state: goes back to baseline setpoints 
        - Other states: 
          * Cooling: If current < cool_baseline + offset, adjust to cool_baseline + offset
          * Heating: If current > heat_baseline - offset, adjust to heat_baseline - offset
        
        Args:
            grid_state: Current grid state (0=Normal, 1=Moderate, 2=High, 3=Emergency)
            
        Performs:
            Tuple of (new_cool_sp, new_heat_sp, adjustment_made, message)
            - new_cool_sp: Optimized cooling setpoint
            - new_heat_sp: Optimized heating setpoint
            - adjustment_made: True if any adjustment was made
            - message: Description of what was done
        """
        # Get offset for current state
        offset = self.get_offset_for_state(grid_state)
        # Calculate target setpoints
        target_cool_sp = self.cool_baseline + offset
        target_heat_sp = self.heat_baseline - offset

        if self.last_applied_cool_sp is not None and self.last_applied_cool_sp == target_cool_sp:
            target_cool_sp = None
            print ('ThermostatOptimizer: target cooling setpoint unchanged from last applied value. Skipping optimization.')
        
        if self.last_applied_heat_sp is not None and self.last_applied_heat_sp == target_heat_sp:
            print ('ThermostatOptimizer: target heating setpoint unchanged from last applied value. Skipping optimization.')
            target_heat_sp = None

        #optimization but only if current grid state is greater than the last othewrwise 
        #set points never change which is an error
        # Heating optimization
        if grid_state >= self.last_grid_state:
            # If current heating setpoint is HIGHER than baseline - offset, lower it
            if self.current_heat_sp is not None and self.current_heat_sp < target_heat_sp:
                target_heat_sp = None
                self.history.insert(self._get_device_name(), "Heat Setpoint", grid_state=grid_state, requested_value=target_heat_sp,
                                   current_value=self.current_heat_sp, opt_status="No Adjustment Needed")
                print ('ThermostatOptimizer: current heating setpoint is already below target. No adjustment needed.')
            
            # Cooling optimization
            # If current cooling setpoint is LOWER than baseline + offset, raise it
            if self.current_cool_sp is not None and self.current_cool_sp > target_cool_sp:
                target_cool_sp = None
                self.history.insert(self._get_device_name(), "Cool Setpoint", grid_state=grid_state, requested_value=target_cool_sp,
                                   current_value=self.current_cool_sp, opt_status="No Adjustment Needed")
                print ('ThermostatOptimizer: current cooling setpoint is already above target. No adjustment needed.')

        # now adjust the thermostats
        new_cool_sp, new_heat_sp = self._adjust_setpoints(target_cool_sp, target_heat_sp)
        if new_cool_sp is not None:
            self.history.insert(self._get_device_name(), "Cool Setpoint", grid_state=grid_state, requested_value=new_cool_sp,
                                   current_value=self.current_cool_sp, opt_status="Optimized")
            self.last_applied_cool_sp = new_cool_sp
        if new_heat_sp is not None:
            self.history.insert(self._get_device_name(), "Heat Setpoint", grid_state=grid_state, requested_value=new_heat_sp,
                                   current_value=self.current_heat_sp, opt_status="Optimized")
            self.last_applied_heat_sp = new_heat_sp
        
        
    def _reset_opt_out(self):
        """
        Manually reset the opt-out status (e.g., for testing or user request).
        """
        self.last_applied_cool_sp = None
        self.last_applied_heat_sp = None

    async def _update_internal_state(self, property, value):
        """
        Args:
            property: property name from the event 
            value: the value for the property 
                'action': {
                    'value': str,
                    'uom': str or None,
                    'prec': str or None
                }
        """

        if property == 'CLISPC':
            self.cool_prec = value['prec']
            self.cool_uom = value['uom']
            value = self.value_to_float(value['value'], self.cool_prec)
            self.current_cool_sp = value
        elif property == 'CLISPH':
            self.heat_prec = value['prec']
            self.heat_uom = value['uom']
            value = self.value_to_float(value['value'], self.heat_prec)
            self.current_heat_sp = value    
        elif property == 'ST':
            self.current_temp = self.value_to_float(value['value'], value['prec'])
        elif property == 'CLIMD':
            self.current_mode = str(value['value'])
