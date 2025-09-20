import json
import os
from typing import Dict, Any

# Default settings
DEFAULT_SETTINGS = {
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

# Steering modes
STEERING_MODES = {
    'Standard': 'Standard',
    'Sport': {
        'curve_strength': 1.8,
        'response_speed': 1.2,
        'center_snap': 0.9
    },
    'Race': {
        'curve_strength': 2.2,
        'response_speed': 1.5,
        'center_snap': 0.7
    }
}

# Game Profiles with keyboard mappings
GAME_PROFILES = {
    'assetto_corsa.exe': {
        'name': 'Assetto Corsa',
        'steer_speed': 600,
        'throttle_speed': 500,
        'brake_speed': 500,
        'curve_strength': 1.5,
        'deadzone_size': 10,
        'steering_mode': 'Race',
        'force_feedback': True,
        'vibration_strength': 0.7,
        'response_speed': 1.5,
        'center_snap': 0.7
    }
}

# Default key bindings
KEY_BINDINGS = {
    'gear_up': 'up',
    'gear_down': 'down',
    'clutch': 'left_shift',
    'handbrake': 'space'
}

class Settings:
    def __init__(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.game_profiles = GAME_PROFILES.copy()
        self.key_bindings = KEY_BINDINGS.copy()
        self.config_file = 'pro_driver_assist_config.json'
        self.load()

    def load(self, config_file=None):
        """Load settings from a JSON file"""
        if config_file is None:
            config_file = self.config_file

        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.settings.update(config.get('settings', {}))
                    self.game_profiles.update(config.get('game_profiles', {}))
                    self.key_bindings.update(config.get('key_bindings', {}))
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save(self, config_file=None):
        """Save settings to a JSON file"""
        if config_file is None:
            config_file = self.config_file

        try:
            config = {
                'settings': self.settings,
                'game_profiles': self.game_profiles,
                'key_bindings': self.key_bindings
            }
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key, default=None):
        """Get a setting value with optional default"""
        return self.settings.get(key, default)

    def set(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
