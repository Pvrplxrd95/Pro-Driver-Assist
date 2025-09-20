"""
Keyboard Input Processor for Pro Driver Assist
Handles keyboard input processing with smooth control adaptation
"""

import time
import math
import keyboard
import logging
from typing import Dict, Optional
from dataclasses import dataclass
from threading import Lock

@dataclass
class KeyState:
    pressed: bool = False
    press_time: float = 0
    release_time: float = 0
    hold_duration: float = 0
    value: float = 0

class KeyboardProcessor:
    def __init__(self, config: dict):
        self.config = config.get('keyboard_controls', {})
        self.key_states: Dict[str, KeyState] = {}
        self.lock = Lock()

        # Initialize states for all monitored keys
        self._init_key_states()

        # Control parameters
        self.steering_value = 0.0  # -1.0 to 1.0
        self.throttle_value = 0.0  # 0.0 to 1.0
        self.brake_value = 0.0     # 0.0 to 1.0

        # Smoothing parameters
        self.steering_smoothing = 0.8  # Higher = smoother
        self.pedal_smoothing = 0.7     # Higher = smoother

        # Start input processing
        self._setup_key_handlers()

    def _init_key_states(self):
        """Initialize key states for all monitored keys"""
        steering = self.config.get('steering', {})
        acceleration = self.config.get('acceleration', {})

        self.key_states = {
            steering.get('left_key', 'a'): KeyState(),
            steering.get('right_key', 'd'): KeyState(),
            acceleration.get('accelerate_key', 'w'): KeyState(),
            acceleration.get('brake_key', 's'): KeyState()
        }

    def _setup_key_handlers(self):
        """Set up keyboard event handlers"""
        for key in self.key_states:
            keyboard.on_press_key(key, self._key_pressed)
            keyboard.on_release_key(key, self._key_released)

    def _key_pressed(self, event):
        """Handle key press events"""
        with self.lock:
            key = event.name
            if key in self.key_states:
                state = self.key_states[key]
                current_time = time.time()

                if not state.pressed:
                    state.pressed = True
                    state.press_time = current_time
                    state.hold_duration = 0

    def _key_released(self, event):
        """Handle key release events"""
        with self.lock:
            key = event.name
            if key in self.key_states:
                state = self.key_states[key]
                current_time = time.time()

                state.pressed = False
                state.release_time = current_time
                state.hold_duration = current_time - state.press_time

    def update(self, delta_time: float):
        """Update input values based on current key states"""
        with self.lock:
            self._update_steering(delta_time)
            self._update_pedals(delta_time)
            self._apply_assists()

    def _update_steering(self, delta_time: float):
        """Update steering value with smooth transitions"""
        steering = self.config.get('steering', {})
        left_key = steering.get('left_key', 'a')
        right_key = steering.get('right_key', 'd')

        # Calculate raw steering input
        left_value = self._calculate_key_value(left_key)
        right_value = self._calculate_key_value(right_key)
        target_steering = right_value - left_value

        # Apply smoothing
        if steering.get('gradual_turn', True):
            self.steering_value = self._smooth_value(
                self.steering_value,
                target_steering,
                self.steering_smoothing,
                delta_time
            )
        else:
            self.steering_value = target_steering

        # Apply return to center
        if steering.get('return_to_center', True) and not (left_value or right_value):
            center_speed = steering.get('center_speed', 0.3)
            self.steering_value = self._smooth_value(
                self.steering_value,
                0.0,
                center_speed,
                delta_time
            )

    def _update_pedals(self, delta_time: float):
        """Update throttle and brake values with smooth transitions"""
        acceleration = self.config.get('acceleration', {})
        accelerate_key = acceleration.get('accelerate_key', 'w')
        brake_key = acceleration.get('brake_key', 's')

        # Calculate raw pedal inputs
        target_throttle = self._calculate_key_value(accelerate_key)
        target_brake = self._calculate_key_value(brake_key)

        # Apply progressive acceleration if enabled
        if acceleration.get('progressive_acceleration', True):
            self.throttle_value = self._smooth_value(
                self.throttle_value,
                target_throttle,
                self.pedal_smoothing,
                delta_time
            )
            self.brake_value = self._smooth_value(
                self.brake_value,
                target_brake,
                self.pedal_smoothing,
                delta_time
            )
        else:
            self.throttle_value = target_throttle
            self.brake_value = target_brake

    def _calculate_key_value(self, key: str) -> float:
        """Calculate input value for a key based on its state"""
        state = self.key_states.get(key)
        if not state or not state.pressed:
            return 0.0

        current_time = time.time()
        hold_time = current_time - state.press_time

        # Apply progressive curve to hold time
        curve = 1.0 - math.exp(-hold_time * 2.0)
        return min(1.0, curve)

    def _smooth_value(self, current: float, target: float, smoothing: float, delta_time: float) -> float:
        """Smooth transition between current and target values"""
        if abs(target - current) < 0.001:
            return target

        rate = 1.0 - math.pow(smoothing, delta_time * 60.0)
        return current + (target - current) * rate

    def _apply_assists(self):
        """Apply driving assists based on configuration"""
        assists = self.config.get('assists', {})

        if assists.get('counter_steer_assist', True):
            self._apply_counter_steer()

        if assists.get('anti_spin_assist', True):
            self._apply_anti_spin()

    def _apply_counter_steer(self):
        """Apply counter-steering assistance"""
        if abs(self.steering_value) > 0.8 and self.throttle_value > 0.7:
            strength = self.config.get('assists', {}).get('counter_steer_strength', 0.5)
            self.steering_value *= (1.0 - strength)

    def _apply_anti_spin(self):
        """Apply anti-spin assistance"""
        if abs(self.steering_value) > 0.6 and self.throttle_value > 0.8:
            strength = self.config.get('assists', {}).get('spin_prevention', 0.6)
            self.throttle_value *= (1.0 - strength)

    def get_inputs(self) -> Dict[str, float]:
        """Get current input values"""
        return {
            'steering': self.steering_value,
            'throttle': self.throttle_value,
            'brake': self.brake_value
        }

    def cleanup(self):
        """Clean up resources and unhook keyboard handlers"""
        for key in self.key_states:
            keyboard.unhook_key(key)
