"""
Input Device Manager for Pro Driver Assist
Handles detection and management of input devices (keyboard and steering wheel)
"""

import threading
import logging
import keyboard
import time
from typing import Optional, Dict, Callable
from enum import Enum
from pathlib import Path
import json

class InputDevice(Enum):
    KEYBOARD = "keyboard"
    STEERING_WHEEL = "steering_wheel"
    UNKNOWN = "unknown"

class InputDeviceManager:
    def __init__(self):
        self.current_device: InputDevice = InputDevice.UNKNOWN
        self.device_lock = threading.Lock()
        self.device_changed_callbacks: list[Callable] = []
        self.last_keyboard_time = 0
        self.last_wheel_time = 0
        self.detection_threshold = 0.5  # Time in seconds to determine active device
        self.config_dir = Path(__file__).parent / "config"
        self.keyboard_config = self._load_keyboard_config()

        # Start device detection thread
        self.running = True
        self.detection_thread = threading.Thread(target=self._device_detection_loop, daemon=True)
        self.detection_thread.start()

    def _load_keyboard_config(self) -> dict:
        """Load keyboard configuration from file"""
        try:
            config_file = self.config_dir / "keyboard_config_template.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    return json.load(f)
            logging.warning("Keyboard config not found, using defaults")
            return self._get_default_keyboard_config()
        except Exception as e:
            logging.error(f"Error loading keyboard config: {e}")
            return self._get_default_keyboard_config()

    def _get_default_keyboard_config(self) -> dict:
        """Return default keyboard configuration"""
        return {
            "keyboard_controls": {
                "steering": {
                    "left_key": "a",
                    "right_key": "d",
                    "gradual_turn": True,
                    "turn_speed": 0.5
                },
                "acceleration": {
                    "accelerate_key": "w",
                    "brake_key": "s",
                    "progressive_acceleration": True
                }
            }
        }

    def register_device_changed_callback(self, callback: Callable):
        """Register a callback for device change events"""
        self.device_changed_callbacks.append(callback)

    def _notify_device_changed(self):
        """Notify all registered callbacks of device change"""
        for callback in self.device_changed_callbacks:
            try:
                callback(self.current_device)
            except Exception as e:
                logging.error(f"Error in device change callback: {e}")

    def _device_detection_loop(self):
        """Main loop for device detection"""
        while self.running:
            try:
                # Check for keyboard activity
                if any(keyboard.is_pressed(key) for key in ['w', 'a', 's', 'd', 'space']):
                    self.last_keyboard_time = time.time()

                # Check for steering wheel activity (implement wheel detection)
                wheel_active = self._check_wheel_activity()
                if wheel_active:
                    self.last_wheel_time = time.time()

                # Determine active device
                current_time = time.time()
                keyboard_active = (current_time - self.last_keyboard_time) < self.detection_threshold
                wheel_active = (current_time - self.last_wheel_time) < self.detection_threshold

                with self.device_lock:
                    new_device = InputDevice.UNKNOWN
                    if keyboard_active and not wheel_active:
                        new_device = InputDevice.KEYBOARD
                    elif wheel_active and not keyboard_active:
                        new_device = InputDevice.STEERING_WHEEL

                    if new_device != self.current_device:
                        self.current_device = new_device
                        self._notify_device_changed()
                        logging.info(f"Input device changed to: {new_device.value}")

                time.sleep(0.1)  # Prevent excessive CPU usage

            except Exception as e:
                logging.error(f"Error in device detection loop: {e}")
                time.sleep(1)  # Wait before retrying

    def _check_wheel_activity(self) -> bool:
        """Check for steering wheel input activity"""
        # TODO: Implement actual wheel detection
        # This should check for DirectInput or similar wheel activity
        return False

    def get_current_device(self) -> InputDevice:
        """Get currently active input device"""
        with self.device_lock:
            return self.current_device

    def is_keyboard_mode(self) -> bool:
        """Check if keyboard is the current input device"""
        return self.get_current_device() == InputDevice.KEYBOARD

    def is_wheel_mode(self) -> bool:
        """Check if steering wheel is the current input device"""
        return self.get_current_device() == InputDevice.STEERING_WHEEL

    def get_keyboard_config(self) -> dict:
        """Get current keyboard configuration"""
        return self.keyboard_config

    def cleanup(self):
        """Clean up resources"""
        self.running = False
        if self.detection_thread.is_alive():
            self.detection_thread.join(timeout=1.0)
