import time
from typing import Dict, Any

# Constants
CENTER_AXIS = 0

# Button constants
BUTTONS = {
    'gear_up': False,
    'gear_down': False,
    'clutch': False,
    'handbrake': False
}

class InputState:
    def __init__(self):
        self.steering = CENTER_AXIS
        self.throttle = 0
        self.brake = 0
        self.buttons = BUTTONS.copy()
        self._key_states = {}
        self._last_update = 0
        self._update_interval = 0.016  # ~60 FPS

    def update_key_states(self):
        """Batch update all key states"""
        current_time = time.time()
        if current_time - self._last_update < self._update_interval:
            return

        self._last_update = current_time
        
        # Update button states
        for button, key in self.buttons.items():
            if key in self._key_states:
                self.buttons[button] = self._key_states[key]

    def is_key_pressed(self, key):
        """Check if a key is pressed using cached state"""
        return self._key_states.get(key, False)

    def set_key_state(self, key, state):
        """Set the state of a key"""
        self._key_states[key] = state
