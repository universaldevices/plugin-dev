from iox import IoXWrapper
from nucore import Node
from base_optimizer import BaseOptimizer
from ven_settings import VENSettings
    
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
        try:
            properties = node.properties
            if properties:
                for prop_id, prop in properties.items(): 
                    if prop_id == 'CLISPC':
                        self.current_cool_sp = self.value_to_float(prop.value, prop.prec)
                    elif prop_id == 'CLISPH':
                        self.current_heat_sp = self.value_to_float(prop.value, prop.prec)
                    elif prop_id == 'ST':
                        self.current_temp = self.value_to_float(prop.value, prop.prec)
                    elif prop_id == 'CLIMD':
                        self.current_mode = str(prop.value)
        except Exception as ex:
            print(f"ThermostatOptimizer init error: {ex}")
        
    def _get_min_offset(self):
        return self.ven_settings.min_setpoint_offset

    def _get_max_offset(self):
        return self.ven_settings.max_setpoint_offset

    def _update_settings(self):
        self.cool_baseline = self.ven_settings.cooling_setpoint
        self.heat_baseline = self.ven_settings.heating_setpoint

    def _check_user_override(self):
        pass

    def _test_check_user_override(self, current_cool_sp, current_heat_sp, grid_state):
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
        if grid_state == self.STATE_NORMAL:
            return False
        
        # If we haven't applied any setpoints yet, no override possible
        if self.last_applied_cool_sp is None or self.last_applied_heat_sp is None:
            return False
        
        # Check if current setpoints differ from what we last applied
        # Allow for small floating point differences
        cool_changed = abs(current_cool_sp - self.last_applied_cool_sp) > 0.5
        heat_changed = abs(current_heat_sp - self.last_applied_heat_sp) > 0.5
        
        if cool_changed or heat_changed:
            # User has overridden - opt out until next day
            self.opt_out()
            return True
        
        return False
    
    
    async def _optimize(self, current_cool_sp, current_heat_sp, grid_state):
        """
        Optimize thermostat setpoints based on current grid state and comfort baselines.
       
        Algorithm:
        - Normal state: No changes
        - Other states: 
          * Cooling: If current < cool_baseline + offset, adjust to cool_baseline + offset
          * Heating: If current > heat_baseline - offset, adjust to heat_baseline - offset
        
        Args:
            current_cool_sp: Current cooling setpoint (°F)
            current_heat_sp: Current heating setpoint (°F)
            grid_state: Current grid state (0=Normal, 1=Moderate, 2=High, 3=Emergency)
            
        Returns:
            Tuple of (new_cool_sp, new_heat_sp, adjustment_made, message)
            - new_cool_sp: Optimized cooling setpoint
            - new_heat_sp: Optimized heating setpoint
            - adjustment_made: True if any adjustment was made
            - message: Description of what was done
        """
        
        # Normal state: no changes
        if grid_state == self.STATE_NORMAL:
            self.last_applied_cool_sp = current_cool_sp
            self.last_applied_heat_sp = current_heat_sp
            return (current_cool_sp, current_heat_sp, False, "Normal state - no optimization")
        
        
        # Get offset for current state
        offset = self.get_offset_for_state(grid_state)
        
        # Calculate target setpoints
        target_cool_sp = self.cool_baseline + offset
        target_heat_sp = self.heat_baseline - offset
        
        # Initialize new setpoints
        new_cool_sp = current_cool_sp
        new_heat_sp = current_heat_sp
        adjustments = []
        
        # Cooling optimization
        # If current cooling setpoint is LOWER than baseline + offset, raise it
        if current_cool_sp < target_cool_sp:
            new_cool_sp = target_cool_sp
            adjustments.append(f"Cool SP: {current_cool_sp}°F → {new_cool_sp}°F")
        
        # Heating optimization
        # If current heating setpoint is HIGHER than baseline - offset, lower it
        if current_heat_sp > target_heat_sp:
            new_heat_sp = target_heat_sp
            adjustments.append(f"Heat SP: {current_heat_sp}°F → {new_heat_sp}°F")
        
        # Track what we applied
        self.last_applied_cool_sp = new_cool_sp
        self.last_applied_heat_sp = new_heat_sp
        
        # Build message
        state_names = {
            self.STATE_NORMAL: "Normal",
            self.STATE_MODERATE: "Moderate",
            self.STATE_HIGH: "High",
            self.STATE_EMERGENCY: "Emergency"
        }
        state_name = state_names.get(grid_state, "Unknown")
        
        if adjustments:
            message = f"{state_name} state (offset={offset}°F): " + ", ".join(adjustments)
            return (new_cool_sp, new_heat_sp, True, message)
        else:
            message = f"{state_name} state (offset={offset}°F): No adjustment needed"
            return (new_cool_sp, new_heat_sp, False, message)
    
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
            self.current_cool_sp = self.value_to_float(value['value'], value['prec'])
        elif property == 'CLISPH':
            self.current_heat_sp = self.value_to_float(value['value'], value['prec'])    
        elif property == 'ST':
            self.current_temp = self.value_to_float(value['value'], value['prec'])
        elif property == 'CLIMD':
            self.current_mode = str(value['value'])
