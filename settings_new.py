"""
Settings management for Pro Driver Assist
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

class Settings:
    def __init__(self):
        self.config_dir = Path(__file__).parent / 'config'
        self.config_file = self.config_dir / 'pro_driver_assist_config.json'
        self.config = self._load_settings()

    def _load_settings(self) -> dict:
        """Load settings from file or create with defaults"""
        try:
            # Create config directory if it doesn't exist
            self.config_dir.mkdir(exist_ok=True)

            # Default settings
            default_settings = {
                'steer_speed': 500,
                'throttle_speed': 500,
                'brake_speed': 500,
                'curve_strength': 1.5,
                'deadzone_size': 10,
                'steering_mode': 'Standard',
                'force_feedback': True,
                'vibration_strength': 0.5,
                'response_speed': 1.0,
                'center_snap': 0.8,
                'key_bindings': {
                    'steer_left': 'a',
                    'steer_right': 'd',
                    'throttle': 'w',
                    'brake': 's',
                    'gear_up': 'shift',
                    'gear_down': 'ctrl',
                    'clutch': 'space',
                    'handbrake': 'alt',
                    'exit': 'esc'
                },
                'visualization': {
                    'show_wheel': True,
                    'show_pedals': True,
                    'show_speed': True,
                    'show_ff': True,
                    'theme': {
                        'background': '#212121',
                        'grid': '#424242',
                        'steering': '#2196F3',
                        'throttle': '#4CAF50',
                        'brake': '#F44336'
                    }
                },
                'game_profiles': {}
            }

            # Load existing settings or create new ones
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    saved_settings = json.load(f)

                # Update default settings with saved values
                self._deep_update(default_settings, saved_settings)
                logging.info("Settings loaded successfully")
            else:
                # Create new settings file
                with open(self.config_file, 'w') as f:
                    json.dump(default_settings, f, indent=4)
                logging.info("Created new settings file with defaults")

            return default_settings

        except Exception as e:
            logging.error(f"Error loading settings: {e}")
            return default_settings

    def _deep_update(self, d1: dict, d2: dict):
        """Deep update dictionary d1 with d2"""
        for k, v in d2.items():
            if k in d1:
                if isinstance(v, dict) and isinstance(d1[k], dict):
                    self._deep_update(d1[k], v)
                else:
                    d1[k] = v

    def save(self):
        """Save current settings to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            logging.info("Settings saved successfully")
        except Exception as e:
            logging.error(f"Error saving settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """Set a setting value"""
        self.config[key] = value

    def get_game_profiles(self) -> Dict[str, dict]:
        """Get game profiles"""
        return self.config.get('game_profiles', {})

    def add_game_profile(self, profile: dict):
        """Add a new game profile"""
        if 'game_profiles' not in self.config:
            self.config['game_profiles'] = {}
        self.config['game_profiles'][profile['executable']] = profile

    def get_key_bindings(self) -> Dict[str, str]:
        """Get key bindings"""
        return self.config.get('key_bindings', {})

    def set_key_bindings(self, bindings: Dict[str, str]):
        """Set key bindings"""
        self.config['key_bindings'] = bindings

    def get_visualization_settings(self) -> dict:
        """Get visualization settings"""
        return self.config.get('visualization', {})

    def set_visualization_settings(self, settings: dict):
        """Set visualization settings"""
        self.config['visualization'] = settings
