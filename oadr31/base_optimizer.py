from ven_settings import VENSettings
from abc import ABC, abstractmethod
from nucore import Node
from nucore import Profile
from iox import IoXWrapper

class BaseOptimizer(ABC):
    """
    Base optimizer class for demand response optimization.
    All optimizers should inherit from this class.
    """
    
    # Grid states
    NUM_STATES = 4
    STATE_NORMAL = 0
    STATE_MODERATE = 1
    STATE_HIGH = 2
    STATE_EMERGENCY = 3  # Special/Emergency
    
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
        
        self.last_grid_state = None
        self.callibrate()
    
    def callibrate(self):
        """
        Calibrate the optimizer. Default is simple linear offsets based on min/max and number of states. 
        Override in subclasses if different calibration is required.
        """
        min_offset = self._get_min_offset()
        max_offset = self._get_max_offset()

        # Define offsets for each state within min/max bounds
        # Simple linear distribution of offsets based on NUM_STATES
        range_offset = max_offset - min_offset
        step = range_offset / (self.NUM_STATES - 1) if self.NUM_STATES > 1 else 0   
        self.normal_offset = min_offset
        self.moderate_offset = min_offset + step
        self.high_offset = min_offset + 2 * step
        self.emergency_offset = max_offset


    async def optimize(self, grid_state: int):
        """
        Optimize device settings based on current grid state and comfort baselines.
        
        Args:
            state: Current grid state (0-3)
        """
        if self.last_grid_state is None or grid_state == self.last_grid_state:
            print(f"grid state has not changed from {self.last_grid_state} to {grid_state}, skipping optimization")
            return

        # Check if we're opted out
        if self.check_opt_out_status():
            print(f"{self.node.name} is Opted out until {self.opt_out_until.strftime('%Y-%m-%d %H:%M:%S')}")
            return 

        # Check for user override
        if self._check_user_override():
            print(f"{self.node.name} is in user override mode till {self.opt_out_until.strftime('%Y-%m-%d %H:%M:%S')}")
            return
        
        return await self._optimize(grid_state)
    
    
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
    def _check_user_override(self):
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

    @abstractmethod 
    def _reset_opt_out(self):
        """Reset the opt-out states held by children """
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
