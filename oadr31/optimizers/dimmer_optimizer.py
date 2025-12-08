from iox import IoXWrapper
from nucore import Node
from .base_optimizer import BaseOptimizer
from opt_config.ven_settings import GridState, VENSettings
    
class DimmerOptimizer(BaseOptimizer):
    """
    Dimmer optimization algorithm for demand response across four grid states:
    Normal, Moderate, High, and Emergency (Special).
    
    The algorithm adjusts dimmer settings based on grid conditions while respecting
    user comfort preferences. If a customer manually changes setpoints during an active
    optimization state, the system opts out until the next day.
    """

    def __init__(self, ven_settings: VENSettings, node:Node, iox:IoXWrapper ):
        """
        Initialize the dimmer optimizer.
        
        Args:
            ven_settings: VENSettings instance containing configuration
            node: Node instance associated with this optimizer
            iox: IoXWrapper instance for interacting with IoX
        """
        super().__init__(ven_settings, node, iox)
        # Track last applied dimmer settings to detect user changes
        self.last_applied_dimmer_level = None
        self.current_dimmer_level = None
        self.dimmer_prec = None
        self.dimmer_uom = None

    def _get_min_offset(self):
        return self.ven_settings.min_light_adjustment_offset
    
    def _get_max_offset(self):
        return self.ven_settings.max_light_adjustment_offset

    def _update_settings(self):
        self.light_level_baseline = self.ven_settings.light_level

    def _check_user_override (self, grid_state):
        """
        Check if the user has manually changed the dimmer level during an active optimization state.
        If detected, opt out of optimization until the next day.
        
        Args:
            grid_state: Current grid state
            
        Returns:
            True if user override detected and opted out, False otherwise
        """
        # If we haven't applied any setpoints yet, no override possible
        if self.last_applied_dimmer_level is None or self.current_dimmer_level is None: 
            return False
        
        # Check if current setpoints differ from what we last applied
        # Allow for small floating point differences
        level_changed = abs(self.current_dimmer_level - self.last_applied_dimmer_level) > 1
        
        if level_changed: 
            self.history.insert(self.node.address, "Dimmer Level", grid_state=grid_state, 
                                requested_value=self.last_applied_dimmer_level, current_value=self.current_dimmer_level, 
                                opt_status="User Override", opt_expires_at=self._get_opt_out_expiry().isoformat()) 
            return True
        
        return False
    
    def _adjust_level(self, level:float): 
        """
        Generate command to set the dimmer level 
        
        Args:
            command: 'set_dimmer_level'
            value: New Level value
            
        Returns:
            new_level if successful, None otherwise
        """
        commands = []
        if level is not None: 
            commands.append({
            'device_id': self.node.address,
            'command_id': 'DON', 
            'command_params': [
                {'id': 'n/a', 'value': int(level), 'uom': self.dimmer_uom, 'prec': self.dimmer_prec}
            ]
            })

        if len(commands) > 0: 
            response = self.iox.send_commands(commands)
            if response is None or len(response) == 0:
                print ('DimmerOptimizer: Failed to send setpoint adjustment commands to IoX.')
                return None
            if response[0] is None or response[0].status_code != 200:
                return None
        return level
                
    async def _optimize(self, grid_state):
        """
        Optimize dimmer level based on current grid state and comfort baselines.
        
        Algorithm:
        - Normal state: No changes
        - Other states: Adjust dimmer level away from baseline by offset    
        
        Args:
            grid_state: Current grid state (0=Normal, 1=Moderate, 2=High, 3=Emergency)
            
        """
        if self.current_dimmer_level == 0:
            return

        # Get offset for current state
        offset = self.get_offset_for_state(grid_state)
        # Calculate target setpoints
        target_level = self.light_level_baseline - offset

        if self.last_applied_dimmer_level is not None and self.last_applied_dimmer_level == target_level:
            target_level = None
            print ('DimmerOptimizer: target dimmer level unchanged from last applied value. Skipping optimization.')
        
        #optimization but only if current grid state is greater than the last othewrwise 
        #set points never change which is an error
        # Heating optimization
        if grid_state >= self.last_grid_state:
            # If current heating setpoint is HIGHER than baseline - offset, lower it
            if self.current_dimmer_level is not None and self.current_dimmer_level < target_level:
                target_level = None
                self.history.insert(self._get_device_name(), "Dimmer Level", grid_state=grid_state, requested_value=target_level,
                                   current_value=self.current_dimmer_level, opt_status="No Adjustment Needed")
                print ('DimmerOptimizer: current dimmer level is already below target. No adjustment needed.')
            
        # now adjust the dimmer level
        new_level = self._adjust_level(target_level)
        if new_level is not None:
            self.history.insert(self._get_device_name(), "Dimmer Level", grid_state=grid_state, requested_value=new_level,
                                   current_value=self.current_dimmer_level, opt_status="Optimized" if grid_state != GridState.NORMAL else "Reset to Baseline")
            self.last_applied_dimmer_level = new_level
    
    def _reset_opt_out(self):
        """
        Manually reset the opt-out status (e.g., for testing or user request).
        """
        self.last_applied_dimmer_level = None

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

        if property == 'ST':
            try:
                self.dimmer_prec = value['prec']
                self.dimmer_uom = value['uom']
                self.current_dimmer_level = float(value['value'])
            except Exception as e:
                print(f"DimmerOptimizer: Error updating internal state for property {property}: {e}")