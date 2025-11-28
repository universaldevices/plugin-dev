
class ThermostatOptimizer:
    """
    Thermostat optimization algorithm for demand response across four grid states:
    Normal, Moderate, High, and Emergency (Special).
    
    The algorithm adjusts thermostat setpoints based on grid conditions while respecting
    user comfort preferences. If a customer manually changes setpoints during an active
    optimization state, the system opts out until the next day.
    """
    
    # Grid states
    STATE_NORMAL = 0
    STATE_MODERATE = 1
    STATE_HIGH = 2
    STATE_EMERGENCY = 3  # Special/Emergency
    
    def __init__(self, cool_baseline, heat_baseline, 
                 normal_offset=0, moderate_offset=1, high_offset=2, emergency_offset=3):
        """
        Initialize the thermostat optimizer.
        
        Args:
            cool_baseline: Comfort level baseline for cooling (°F)
            heat_baseline: Comfort level baseline for heating (°F)
            normal_offset: Offset for normal state (default: 0)
            moderate_offset: Offset for moderate state (default: 1)
            high_offset: Offset for high state (default: 2)
            emergency_offset: Offset for emergency state (default: 3)
        """
        self.cool_baseline = cool_baseline
        self.heat_baseline = heat_baseline
        self.normal_offset = normal_offset
        self.moderate_offset = moderate_offset
        self.high_offset = high_offset
        self.emergency_offset = emergency_offset
        
        # Track opt-out status
        self.opted_out = False
        self.opt_out_until = None  # Timestamp until which we're opted out
        
        # Track last applied setpoints to detect user changes
        self.last_applied_cool_sp = None
        self.last_applied_heat_sp = None
    
    def get_offset_for_state(self, state):
        """
        Get the offset value for a given grid state.
        
        Args:
            state: Grid state (STATE_NORMAL, STATE_MODERATE, STATE_HIGH, STATE_EMERGENCY)
            
        Returns:
            Offset value for the state
        """
        if state == self.STATE_NORMAL:
            return self.normal_offset
        elif state == self.STATE_MODERATE:
            return self.moderate_offset
        elif state == self.STATE_HIGH:
            return self.high_offset
        elif state == self.STATE_EMERGENCY:
            return self.emergency_offset
        else:
            return 0
    
    def check_user_override(self, current_cool_sp, current_heat_sp, grid_state):
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
    
    def opt_out(self):
        """
        Opt out of optimization until the next day (midnight).
        """
        from datetime import datetime, timedelta
        
        self.opted_out = True
        # Set opt-out until midnight of the next day
        now = datetime.now()
        next_day = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        self.opt_out_until = next_day
    
    def check_opt_out_status(self):
        """
        Check if we're still opted out, and clear the opt-out if time has expired.
        
        Returns:
            True if currently opted out, False otherwise
        """
        if not self.opted_out:
            return False
        
        from datetime import datetime
        
        if self.opt_out_until and datetime.now() >= self.opt_out_until:
            # Opt-out period has expired
            self.opted_out = False
            self.opt_out_until = None
            return False
        
        return True
    
    def optimize_thermostat(self, current_cool_sp, current_heat_sp, grid_state):
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
        # Check if we're opted out
        if self.check_opt_out_status():
            return (current_cool_sp, current_heat_sp, False, 
                    f"Opted out until {self.opt_out_until.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check for user override
        if self.check_user_override(current_cool_sp, current_heat_sp, grid_state):
            return (current_cool_sp, current_heat_sp, False,
                    "User override detected - opted out until next day")
        
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
    
    def reset_opt_out(self):
        """
        Manually reset the opt-out status (e.g., for testing or user request).
        """
        self.opted_out = False
        self.opt_out_until = None
        self.last_applied_cool_sp = None
        self.last_applied_heat_sp = None
