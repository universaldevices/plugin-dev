from ven_settings import VENSettings, ComfortLevel, GridState
from abc import ABC, abstractmethod
from nucore import Node
from nucore import Profile
from iox import IoXWrapper

class BaseOptimizer(ABC):
    """
    Base optimizer class for demand response optimization.
    All optimizers should inherit from this class.
    """
    
    def __init__(self, ven_settings: VENSettings, node:Node, iox:IoXWrapper):
        """
        Initialize the optimizer with VEN settings.
        
        Args:
            ven_settings: VENSettings instance containing configuration
            node: Node instance associated with this optimizer
            iox: IoXWrapper instance for interacting with IoX
        """
        self.node = node
        self.iox = iox
        self.update_settings(ven_settings)
        self.reset_opt_out()
        
        self.last_grid_state = GridState.NORMAL
        self.calibrate()
    
    def calibrate(self):
        """
        Calibrate the optimizer. Default is simple linear offsets based on min/max and number of states. 
        Override in subclasses if different calibration is required.
        """
        min_offset = self._get_min_offset()
        max_offset = self._get_max_offset()

        #adjust min and max based on comfort level
        comfort_level = self.ven_settings.comfort_level
        if comfort_level == ComfortLevel.MAX_COMFORT:
            pass # No change
        elif comfort_level == ComfortLevel.BALANCED:
            min_offset = abs(min_offset + 1.0)
            max_offset = abs(max_offset + 1.0)
        elif comfort_level == ComfortLevel.MAX_SAVINGS:
            min_offset = abs(min_offset + 2.0)
            max_offset = abs(max_offset + 2.0)

        # Define offsets for each state within min/max bounds
        # Simple linear distribution of offsets based on NUM_STATES
        range_offset = max_offset - min_offset
        step = range_offset / 2   
        self.normal_offset = 0 # No offset for normal state
        self.moderate_offset = min_offset   
        self.high_offset = min_offset + step 
        self.emergency_offset = max_offset


    async def optimize(self, grid_state: int):
        """
        Optimize device settings based on current grid state and comfort baselines.
        
        Args:
            state: Current grid state (0-3)
        """
        grid_state = int(grid_state) 
        if self.last_grid_state is None or grid_state == self.last_grid_state:
            print(f"grid state has not changed from {self.last_grid_state} to {grid_state}, skipping optimization")
            return

        # Check if we're opted out
        if self.check_opt_out_status():
            print(f"{self.node.name} is Opted out until {self.opt_out_until.strftime('%Y-%m-%d %H:%M:%S')}")
            return 

        # Check for user override
        if self._check_user_override(grid_state):
            print(f"{self.node.name} is in user override mode till {self.opt_out_until.strftime('%Y-%m-%d %H:%M:%S')}")
            return
        
        await self._optimize(grid_state)
        self.last_grid_state = grid_state
    
    
    def get_offset_for_state(self, state):
        """
        Get the offset value for a given grid state.
        
        Args:
            state: Grid state (NORMAL, MODERATE, HIGH, EMERGENCY)
            
        Returns:
            Offset value for the state
        """
        state = int(state)
        if state == GridState.NORMAL: 
            return self.normal_offset
        elif state == GridState.MODERATE: 
            return self.moderate_offset
        elif state == GridState.HIGH:
            return self.high_offset
        elif state == GridState.EMERGENCY:
            return self.emergency_offset
        else:
            return 0

    @abstractmethod    
    def _get_min_offset(self):
        """
        Override this method in subclasses to get the minimum offset value
        from VEN settings.
        
        Returns:
            Minimum offset value
        """
        pass

    @abstractmethod
    def _get_max_offset(self):
        """
        Override this method in subclasses to get the minimum offset value
        from VEN settings.
        
        Returns:
            Minimum offset value
        """
        pass

    @abstractmethod 
    def _check_user_override(self, grid_state):
        """
        Override this method in subclasses to check if the user has manually changed
        device settings during an active optimization state.
        If detected, opt out of optimization until the next day.
        
        Returns:
            True if user override detected and opted out, False otherwise
        """
        pass

    @abstractmethod
    async def _optimize(self, grid_state: int):
        """
        Override this method in subclasses to implement optimization logic.
        
        Args:
            grid_state: Current grid state (0-3)
            
        Returns:
            Optimization results (format depends on subclass implementation)
        """
        pass

    def update_settings(self, ven_settings: VENSettings):
        """
        Args:
            ven_settings: Updated VENSettings instance
        """
        self.ven_settings = ven_settings
        self._update_settings()

    @abstractmethod 
    def _update_settings(self):
        """
        Override this method in subclasses to reset optimization settings based on 
        self.ven_settings. 
        """
        pass

    def reset_opt_out(self):
        """Reset the opt-out status"""
        self.opted_out = False
        self.opt_out_until = None
        self._reset_opt_out()


    def value_to_float(self, value, precision):
        """Format a float value to the specified precision.
        
        Args:
            value: Float value to format
            precision: Number of decimal places
            
        Returns:
            Formatted float as string
        """
        if precision is None or precision == '0':
            return float(value)
        div = 10 ** int(precision)
        return float(int(value)/div)

    @abstractmethod 
    def _reset_opt_out(self):
        """Reset the opt-out states held by children """
        pass

    async def update_internal_state(self, event):
        """
        Update internal state based on event changes.
        
        Args:
            event: Event data that may affect internal state
            {
                'seqnum': str or None,
                'sid': str or None,
                'timestamp': str or None,
                'control': str,
                'action': {
                    'value': str,
                    'uom': str or None,
                    'prec': str or None
                },
                'node': str,
                'fmtAct': str,
                'fmtName': str
            }
        """
        if event is None or 'control' not in event or 'action' not in event:
            print("Invalid event data, cannot update internal state")
            return
        
        control = event['control']
        action = event['action']
        if control is None or action is None:
            print("Invalid control or action in event data")
            return
        await self._update_internal_state(control, action)

    @abstractmethod 
    async def _update_internal_state(self, property, value):
        """
        Override this method in subclasses to update internal state based on control and action.
        
        Args:
            control: Control string from event
            action: Action dictionary from event
                'action': {
                    'value': str,
                    'uom': str or None,
                    'prec': str or None
                }
        """
        pass
    
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
    

    def is_opted_out(self):
        """Check if currently opted out"""
        return self.opted_out
