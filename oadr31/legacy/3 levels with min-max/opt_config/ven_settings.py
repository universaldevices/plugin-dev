import json
import os
from typing import Dict, Any, Optional

from enum import IntEnum

class ComfortLevel(IntEnum):
    MAX_COMFORT = 0
    BALANCED = 1
    MAX_SAVINGS = 2

class GridState(IntEnum):
    NORMAL = 0
    MODERATE = 1
    HIGH = 2
    EMERGENCY = 3

class EventMode(IntEnum):
    PRICE = 0
    SIMPLE = 1
    BOTH = 2

class VENSettings:
    """
    A class to store and retrieve OADR3 VEN properties to/from JSON storage.
    This ensures persistence of user-configured settings across restarts.
    """
    def __init__(self, storage_file: str = 'oadr3ven_settings.json'):
        """
        Initialize the VENSettings storage handler.
        
        Args:
            storage_file: Path to the JSON file for storing settings
        """
        self.storage_file = storage_file
        self.settings: Dict[str, Any] = {}
        self._load()
    
    def _load(self) -> None:
        """Load settings from JSON file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    self.settings = json.load(f)
            else:
                self.settings = self._get_default_settings()
                self._save()
        except Exception as ex:
            print(f'Failed to load settings: {str(ex)}')
            self.settings = self._get_default_settings()
    
    def _save(self) -> bool:
        """Save current settings to JSON file"""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as ex:
            print(f'Failed to save settings: {str(ex)}')
            return False
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Return default settings for all properties"""
        return {
            'CL': 0,              # Comfort Level (0=Max Comfort, 1=Balanced, 2=Max Savings)
            'ST': 0,              # Price  
            'GHG': 0,             # Greenhouse Gas Emissions
            'CGS': 0,             # Current Grid Status (0=Normal, 1=Moderate, Hight, and Emergency)
            'CSP_F': 74,          # Desired Cooling Setpoint (°F)
            'HSP_F': 77,          # Desired Heating Setpoint (°F)
            'CLL': 100,           # Desired Light Level (%)
            'MIN_OFF_DEG': 1,     # Min Setpoint Offset (°F)
            'MAX_OFF_DEG': 4,     # Max Setpoint Offset (°F)
            'MIN_LAO': 10,        # Min Light Adjustment Offset (%)
            'MAX_LAO': 50,        # Max Light Adjustment Offset (%)
            'MIN_DCO': 90,        # Min Duty Cycle Offset (%)
            'MAX_DCO': 50,        # Max Duty Cycle Offset (%)
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value by key.
        
        Args:
            key: The setting key (e.g., 'CL', 'CSP_F')
            default: Default value if key doesn't exist
            
        Returns:
            The setting value or default
        """
        return self.settings.get(key, default)

    def is_changed(self, key: str, value: Any) -> bool:
        """
        Check if a setting value has changed. 
        
        Args:
            key: The setting key (e.g., 'CL', 'CSP_F')
            value: The value to compare
            
        Returns:
            True if value changed, False otherwise
        """
        try:
            prev_value = self.settings.get(key)
            return float(prev_value) != float(value)
        except Exception as ex:
            return False

    
    def set(self, key: str, value: Any) -> list[bool]: 
        """
        Set a setting value and save to file.
        
        Args:
            key: The setting key (e.g., 'CL', 'CSP_F')
            value: The value to store
            
        Returns:
            True if successfully saved, False otherwise
        """
        self.settings[key] = value
        return self._save()
    
    def update(self, settings_dict: Dict[str, Any]) -> bool:
        """
        Update multiple settings at once.
        
        Args:
            settings_dict: Dictionary of key-value pairs to update
            
        Returns:
            True if successfully saved, False otherwise
        """
        self.settings.update(settings_dict)
        return self._save()
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all settings.
        
        Returns:
            Dictionary of all settings
        """
        return self.settings.copy()
    
    def reset_to_defaults(self) -> bool:
        """
        Reset all settings to their default values.
        
        Returns:
            True if successfully saved, False otherwise
        """
        self.settings = self._get_default_settings()
        return self._save()
    
    def delete(self, key: str) -> bool:
        """
        Delete a specific setting.
        
        Args:
            key: The setting key to delete
            
        Returns:
            True if successfully saved, False otherwise
        """
        if key in self.settings:
            del self.settings[key]
            return self._save()
        return True
    
    def exists(self, key: str) -> bool:
        """
        Check if a setting exists.
        
        Args:
            key: The setting key to check
            
        Returns:
            True if the key exists, False otherwise
        """
        return key in self.settings
    
    # Convenience property accessors for all VEN settings
    
    @property
    def comfort_level(self) -> int:
        """Get Comfort Level (0-2)"""
        return self.get('CL', 1)
    
    @comfort_level.setter
    def comfort_level(self, value: int):
        """Set Comfort Level (0-2)"""
        self.set('CL', value)
    
    @property
    def cooling_setpoint(self) -> float:
        """Get Desired Cooling Setpoint (°F)"""
        return self.get('CSP_F', 72)
    
    @cooling_setpoint.setter
    def cooling_setpoint(self, value: float):
        """Set Desired Cooling Setpoint (°F)"""
        self.set('CSP_F', value)
    
    @property
    def heating_setpoint(self) -> float:
        """Get Desired Heating Setpoint (°F)"""
        return self.get('HSP_F', 68)
    
    @heating_setpoint.setter
    def heating_setpoint(self, value: float):
        """Set Desired Heating Setpoint (°F)"""
        self.set('HSP_F', value)
    
    @property
    def light_level(self) -> int:
        """Get Desired Light Level (%)"""
        return self.get('CLL', 100)
    
    @light_level.setter
    def light_level(self, value: int):
        """Set Desired Light Level (%)"""
        self.set('CLL', value)
    
    @property
    def min_setpoint_offset(self) -> float:
        """Get Min Setpoint Offset (°F)"""
        return self.get('MIN_OFF_DEG', 0)
    
    @min_setpoint_offset.setter
    def min_setpoint_offset(self, value: float):
        """Set Min Setpoint Offset (°F)"""
        self.set('MIN_OFF_DEG', value)
    
    @property
    def max_setpoint_offset(self) -> float:
        """Get Max Setpoint Offset (°F)"""
        return self.get('MAX_OFF_DEG', 5)
    
    @max_setpoint_offset.setter
    def max_setpoint_offset(self, value: float):
        """Set Max Setpoint Offset (°F)"""
        self.set('MAX_OFF_DEG', value)
    
    @property
    def min_light_adjustment_offset(self) -> int:
        """Get Min Light Adjustment Offset (%)"""
        return self.get('MIN_LAO', 0)
    
    @min_light_adjustment_offset.setter
    def min_light_adjustment_offset(self, value: int):
        """Set Min Light Adjustment Offset (%)"""
        self.set('MIN_LAO', value)
    
    @property
    def max_light_adjustment_offset(self) -> int:
        """Get Max Light Adjustment Offset (%)"""
        return self.get('MAX_LAO', 50)
    
    @max_light_adjustment_offset.setter
    def max_light_adjustment_offset(self, value: int):
        """Set Max Light Adjustment Offset (%)"""
        self.set('MAX_LAO', value)
    
    @property
    def min_duty_cycle_offset(self) -> int:
        """Get Min Duty Cycle Offset (%)"""
        return self.get('MIN_DCO', 0)
    
    @min_duty_cycle_offset.setter
    def min_duty_cycle_offset(self, value: int):
        """Set Min Duty Cycle Offset (%)"""
        self.set('MIN_DCO', value)
    
    @property
    def max_duty_cycle_offset(self) -> int:
        """Get Max Duty Cycle Offset (%)"""
        return self.get('MAX_DCO', 50)
    
    @max_duty_cycle_offset.setter
    def max_duty_cycle_offset(self, value: int):
        """Set Max Duty Cycle Offset (%)"""
        self.set('MAX_DCO', value)

    @property
    def price(self) -> float:
        """Get Price"""
        return self.get('ST', 0)
    
    @price.setter
    def price(self, value: float):
        """Set Price"""
        self.set('ST', value)      

    @property
    def greenhouse_gas_emissions(self) -> float:
        """Get Greenhouse Gas Emissions"""
        return self.get('GHG', 0)

    @greenhouse_gas_emissions.setter
    def greenhouse_gas_emissions(self, value: float):
        """Set Greenhouse Gas Emissions"""
        self.set('GHG', value)
    
    @property
    def current_grid_status(self) -> int:
        """Get Current Grid Status (0=Normal, 1=Alert, 2=Emergency)"""
        return self.get('CGS', 0)

    @current_grid_status.setter
    def current_grid_status(self, value: int):
        """Set Current Grid Status (0=Normal, 1=Alert, 2=Emergency)"""
        self.set('CGS', value)  
