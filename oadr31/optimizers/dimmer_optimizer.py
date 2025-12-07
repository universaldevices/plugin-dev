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

    def _get_min_offset(self):
        return self.ven_settings.min_light_adjustment_offset
    
    def _get_max_offset(self):
        return self.ven_settings.max_light_adjustment_offset

    def _update_settings(self):
        self.light_level_baseline = self.ven_settings.light_level

    def _check_user_override (self, grid_state):
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
        if grid_state == GridState.NORMAL: 
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
    
    async def _optimize(self, grid_state):
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
        pass     
    
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
        print (property, value)
        pass