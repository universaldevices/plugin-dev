import json
import os
from typing import Dict, Any, Optional

from enum import IntEnum

class ComfortLevel(IntEnum):
    MAX_COMFORT = 0
    MAX_SAVINGS = 1

class GridState(IntEnum):
    NORMAL = 0
    MODERATE = 1
    HIGH = 2
    DR = 3

class EventMode(IntEnum):
    PRICE = 0
    SIMPLE = 1
    BOTH = 2

class VENSettings:
    """
    A class to store and retrieve OADR3 VEN properties to/from JSON storage.
    This ensures persistence of user-configured settings across restarts.
    """
    def __init__(self, storage_file: str = 'oadr31_ven_opt_settings_v2.json'):
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
            'CGS': 0,             # Current Grid Status (0=Normal, 1=Moderate, Hight, and DR)
            'cooling_baseline_f'    : 72,       # Baseline Cooling Setpoint in Fahrenheit
            'heating_baseline_f'    : 70,       # Baseline Heating Setpoint
            'light_baseline_percent': 100,      # Baseline Light Level (%)
            'duty_cycle_percent'    : 100,      # Baseline Light Level (%)
            'Comfort': {
                'setpoint_offsets_f': {
                    '0': 0,     # State - Normal
                    '1': 1,     # State - Moderate
                    '2': 2,     # State - High
                    '3': 4,     # State - DR 
                },
                'light_level_offsets': {
                    '0': 100,   # State - Normal
                    '1': 95,    # State - Moderate
                    '2': 90,    # State - High
                    '3': 80,    # State - DR 
                },
                'duty_cycle_offsets': {
                    '0': 100,   # State - Normal
                    '1': 95,    # State - Moderate
                    '2': 90,    # State - High
                    '3': 80,    # State - DR 
                },
            },
            'Savings': {
                'setpoint_offsets_f': {
                    '0': 0,     # State - Normal
                    '1': 2,     # State - Moderate
                    '2': 3,     # State - High
                    '3': 4,     # State - DR 
                },
                'light_level_offsets': {
                    '0': 100,   # State - Normal
                    '1': 90,    # State - Moderate
                    '2': 85,    # State - High
                    '3': 70,    # State - DR 
                },
                'duty_cycle_offsets': {
                    '0': 100,   # State - Normal
                    '1': 90,    # State - Moderate
                    '2': 85,    # State - High
                    '3': 70,    # State - DR 
                },
            }
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
    def light_level_baseline(self) -> int:
        """Get Light Level Baseline (%)"""
        return self.get('light_baseline_percent', 100)
    @property 
    def cooling_baseline_f(self) -> int:
        """Get Cooling Setpoint Baseline (F)"""
        return self.get('cooling_baseline_f', 74)
    
    @property
    def heating_baseline_f(self) -> int:
        """Get Heating Setpoint Baseline (F)"""
        return self.get('heating_baseline_f', 77)
    @property 
    def duty_cycle_baseline(self) -> int:
        """Get Duty Cycle Baseline (%)"""
        return self.get('duty_cycle_percent', 100)
    
    @property
    def comfort_level(self) -> int:
        """Get Comfort Level (0-2)"""
        return self.get('CL', 1)
    
    @comfort_level.setter
    def comfort_level(self, value: int):
        """Set Comfort Level (0-2)"""
        self.set('CL', value)
    
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
        return self.get('CGS', 0)

    @current_grid_status.setter
    def current_grid_status(self, value: int):
        self.set('CGS', value)  

    def getComfortSettings(self) -> Dict[str, Any]:
        """Get Comfort Settings Dictionary"""
        return self.get('Comfort', {})
    
    def getSavingsSettings(self) -> Dict[str, Any]:
        """Get Savings Settings Dictionary"""
        return self.get('Savings', {})