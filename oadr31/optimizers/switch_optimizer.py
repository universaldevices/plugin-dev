from iox import IoXWrapper
from nucore import Node
from .base_optimizer import BaseOptimizer, TESTING_MODE, OPT_OUT_DURATION
from opt_config.ven_settings import GridState, VENSettings, ComfortLevel
import asyncio

DUTY_CYCLE_PERIOD_SECONDS = (OPT_OUT_DURATION/2) if TESTING_MODE else (60 * 60)  # 1 hour
    
class SwitchOptimizer(BaseOptimizer):
    """
    Switch optimization algorithm for demand response across four grid states:
    Normal, Moderate, High, and Emergency (Special).
    
    The algorithm uses duty cycling to reduce load - switches are turned on/off
    in cycles based on the duty cycle percentage for the current grid state.
    If a customer manually changes state during an active optimization state, 
    the system opts out until the next day.
    """

    def __init__(self, ven_settings: VENSettings, node:Node, iox:IoXWrapper ):
        """
        Initialize the switch optimizer.
        
        Args:
            ven_settings: VENSettings instance containing configuration
            node: Node instance associated with this optimizer
            iox: IoXWrapper instance for interacting with IoX
        """
        # Track last applied switch settings to detect user changes
        super().__init__(ven_settings, node, iox)
        self.last_applied_state = None
        self.current_state = None
        self.initial_state = None
        self.switch_prec = None
        self.switch_uom = None
        
        # Duty cycle control
        self.duty_cycle_task = None
        self.duty_cycle_running = False
        self.current_duty_cycle = None 
        self.cycle_period_seconds = DUTY_CYCLE_PERIOD_SECONDS 

    def _get_min_offset(self):
        return self.ven_settings.min_duty_cycle_offset
    
    def _get_max_offset(self):
        return self.ven_settings.max_duty_cycle_offset

    def _update_settings(self):
        self._stop_duty_cycle()

    def _get_offset(self, value: float) -> float:
        max_offset = self._get_max_offset()

        return value if value > max_offset else max_offset

    def _calibrate(self):
        """
        Calibrate the optimizer. Default is simple linear offsets based on min/max and number of states. 
        Override in subclasses if different calibration is required.
        
        Subclasses can override this method to implement custom calibration logic.
        """
        min_offset = self._get_min_offset()
        max_offset = self._get_max_offset()

        #adjust min and max based on comfort level
        comfort_level = self.ven_settings.comfort_level
        if comfort_level == ComfortLevel.MAX_COMFORT:
            self.normal_offset = min_offset 
            self.moderate_offset  = self._get_offset(min_offset - 5.0)
            self.high_offset = self._get_offset(min_offset - 10.0)
            self.emergency_offset = max_offset 
        elif comfort_level == ComfortLevel.BALANCED:
            self.normal_offset = self._get_offset(min_offset - 10.0)  
            self.moderate_offset  = self._get_offset(min_offset - 20.0) 
            self.high_offset = self._get_offset(min_offset - 30.0)     
            self.emergency_offset = max_offset 
        elif comfort_level == ComfortLevel.MAX_SAVINGS:
            self.normal_offset = self._get_offset(min_offset - 20.0) 
            self.moderate_offset  = self._get_offset(min_offset - 30.0) 
            self.high_offset = self._get_offset(min_offset - 40.0)     
            self.emergency_offset = max_offset 


    def _check_user_override (self, grid_state):
        """
        Check if the user has manually changed the dimmer level during an active optimization state.
        If detected, opt out of optimization until the next day.
        
        Args:
            grid_state: Current grid state
            
        Returns:
            True if user override detected and opted out, False otherwise
        """
        if not self.duty_cycle_running:
            return False

        # If we haven't applied any setpoints yet, no override possible
        if self.last_applied_state is not None and self.current_state is not None: 
            if self.last_applied_state != self.current_state:
                self.history.insert(self._get_device_name(), "Switch State", grid_state=grid_state, 
                                    requested_value=self.last_applied_state, current_value=self.current_state, 
                                    opt_status="User Override", opt_expires_at=self._get_opt_out_expiry().isoformat()) 
                return True
        
        return False
    
    def _adjust_level(self, level:float): 
        """
        Generate command to set the switch state 
        
        Args:
            level: New state value (0=OFF, >0=ON)
            
        Returns:
            new_level if successful, None otherwise
        """
        commands = []
        if level is not None: 
            command_id = 'DOF' if level == 0 else 'DON'
            commands.append({
                'device_id': self.node.address,
                'command_id': command_id, 
                'command_params': []
            })

        if len(commands) > 0: 
            response = self.iox.send_commands(commands)
            if response is None or len(response) == 0:
                self.print ('failed to send switch command to IoX.')
                return None
            if response[0] is None or response[0].status_code != 200:
                return None
        return level
    
    async def _run_duty_cycle(self, duty_cycle_percent: int):
        """
        Run duty cycle control loop.
        
        Args:
            duty_cycle_percent: Duty cycle percentage (0-100)
        """
        on_seconds = ((self.cycle_period_seconds * duty_cycle_percent) / 100).total_seconds()
        off_seconds = (self.cycle_period_seconds).total_seconds() - on_seconds
        
        self.print(f"starting duty cycle for {self.node.name}: "
              f"{duty_cycle_percent}% ({on_seconds}s ON, {off_seconds}s OFF)")
        
        try:
            while self.duty_cycle_running:
                # Turn OFF
                if off_seconds > 0 and self.duty_cycle_running:
                    self._adjust_level(0)
                    self.last_applied_state = 0
                    try:
                        await asyncio.sleep(off_seconds)
                    except asyncio.CancelledError:
                        break
                
                # Turn ON
                if on_seconds > 0:
                    self._adjust_level(1)
                    self.last_applied_state = 1
                    try:
                        await asyncio.sleep(on_seconds)
                    except asyncio.CancelledError:
                        break
                
        except asyncio.CancelledError:
            self.print(f"duty cycle cancelled for {self.node.name}")
            self._adjust_level(0)  # Turn off when stopping
            raise
    
    async def _start_duty_cycle(self, duty_cycle_percent: int):
        """Start duty cycle in background task"""
        if duty_cycle_percent >= 100:
            # Full power - just turn on
            await self._stop_duty_cycle()
            self._adjust_level(1)
            self.last_applied_state = 1
            return
        
        if duty_cycle_percent <= 0:
            # No power - turn off
            await self._stop_duty_cycle()
            self._adjust_level(0)
            self.last_applied_state = 0
            return
        
        # Update duty cycle
        self.current_duty_cycle = duty_cycle_percent
        
        # Start new task if not running
        if not self.duty_cycle_running:
            self.duty_cycle_running = True
            self.duty_cycle_task = asyncio.create_task(self._run_duty_cycle(duty_cycle_percent))
    
    async def _stop_duty_cycle(self):
        """Stop duty cycle and turn device off"""
        self.duty_cycle_running = False
        if self.duty_cycle_task and not self.duty_cycle_task.done():
            self.duty_cycle_task.cancel()
            try:
                await self.duty_cycle_task
            except asyncio.CancelledError:
                pass
        if self.initial_state is not None: 
            self._adjust_level(1 if self.initial_state>0 else 0)  # Ensure off
                
    async def _optimize(self, grid_state):
        """
        Optimize switch using duty cycling based on current grid state.
        
        Algorithm:
        - Normal state (0): 100% duty cycle (always on)
        - Other states: Reduce duty cycle based on grid state severity
        
        Args:
            grid_state: Current grid state (0=Normal, 1=Moderate, 2=High, 3=Emergency)
            
        """

        if grid_state == GridState.NORMAL:
            if self.duty_cycle_running:
                # Reset to normal operation
                await self._stop_duty_cycle()
                self.print(f'grid state is NORMAL. Stopping duty cycle optimization.')
                self.history.insert(
                    self._get_device_name(), 
                    "Duty Cycle", 
                    grid_state=grid_state, 
                    requested_value=100,
                    current_value=self.current_duty_cycle, 
                    opt_status="Reset to Normal"
                )
                self.current_duty_cycle = None
            return
        
        if self.current_state == 0: 
            # Device is already off, no optimization needed
            return
        
        target_duty_cycle = self.get_offset_for_state(grid_state) 
        if target_duty_cycle > 100:
            target_duty_cycle = 100
        elif target_duty_cycle < 0:
            target_duty_cycle = 0

        if self.current_duty_cycle is not None:
            if self.current_duty_cycle == target_duty_cycle:
                self.print (f'target duty cycle unchanged from last applied value. Skipping optimization.')
                return
            else:
                #stop current duty cycle to change to new one
                self.print(f"stopping duty cycle run since the value has changed") 
                await self._stop_duty_cycle()
        
        self.print(f'optimizing with duty cycle {target_duty_cycle}% for grid state {grid_state}')
        
        # Record optimization
        self.history.insert(
            self._get_device_name(), 
            "Duty Cycle", 
            grid_state=grid_state, 
            requested_value=target_duty_cycle,
            current_value=self.current_duty_cycle, 
            opt_status="Optimized" if grid_state != GridState.NORMAL else "Reset to Normal"
        )
        
        # Start or update duty cycling
        await self._start_duty_cycle(target_duty_cycle)

    def _opt_out(self):
        self._stop_duty_cycle
    
    def _reset_opt_out(self):
        """
        Manually reset the opt-out status (e.g., for testing or user request).
        """
        self.last_applied_state = None
        # Stop duty cycling
        if hasattr(self, 'duty_cycle_task') and self.duty_cycle_task:
            asyncio.create_task(self._stop_duty_cycle())

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
                self.switch_prec = value['prec']
                self.switch_uom = value['uom']
                self.current_state = 0 if float(value['value']) == 0 else 1
                if self.initial_state is None:
                    self.initial_state = self.current_state
            except Exception as e:
                self.print(f"error updating internal state for property {property}: {e}")