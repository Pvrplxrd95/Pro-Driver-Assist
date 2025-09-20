"""
Input Manager for Pro Driver Assist
Manages both keyboard and steering wheel inputs with automatic switching
"""

import logging
import threading
import time
from pathlib import Path
from typing import Dict, Optional, Tuple
import keyboard
import pydirectinput
from input_device_manager import InputDeviceManager, InputDevice
from keyboard_processor import KeyboardProcessor

class InputManager:
    def __init__(self, config: dict, gui=None):
        """
        Initialize the input manager
        config: The main program configuration
        gui: Optional GUI reference for visualization
        """
        self.config = config
        self.gui = gui
        self.device_manager = InputDeviceManager()
        self.keyboard_processor = None
        self.keyboard_visualizer = None
        self.running = True
        self.last_update = time.time()

        # Initialize keyboard support
        self._init_keyboard_support()

        # Start input processing thread
        self.input_thread = threading.Thread(target=self._input_loop, daemon=True)
        self.input_thread.start()

    def _init_keyboard_support(self):
        """Initialize keyboard input processing"""
        try:
            # Default key bindings if none exist
            default_bindings = {
                'steer_left': 'a',
                'steer_right': 'd',
                'throttle': 'w',
                'brake': 's',
                'gear_up': 'shift',
                'gear_down': 'ctrl',
                'clutch': 'space',
                'handbrake': 'alt'
            }

            # Get key bindings from config or use defaults
            key_bindings = self.config.get('key_bindings', default_bindings)

            # Convert main config to keyboard config format
            keyboard_config = {
                'steering_keys': {
                    'left': key_bindings.get('steer_left', 'a'),
                    'right': key_bindings.get('steer_right', 'd')
                },
                'throttle_key': key_bindings.get('throttle', 'w'),
                'brake_key': key_bindings.get('brake', 's'),
                'sensitivity': {
                    'steering': self.config.get('response_speed', 1.0),
                    'throttle': 1.0,
                    'brake': 1.0
                },
                'smoothing': {
                    'steering': 0.3,  # Lower = more responsive
                    'throttle': 0.2,
                    'brake': 0.2
                }
            }

            self.keyboard_processor = KeyboardProcessor(keyboard_config)
            logging.info("Keyboard input processor initialized")

        except Exception as e:
            logging.error(f"Failed to initialize keyboard support: {e}")

    def _input_loop(self):
        """Main input processing loop"""
        while self.running:
            try:
                current_time = time.time()
                delta_time = current_time - self.last_update
                self.last_update = current_time

                # Get current input device
                device = self.device_manager.get_current_device()

                if device == InputDevice.KEYBOARD:
                    self._process_keyboard_input(delta_time)
                else:
                    # Default to wheel input
                    self._process_wheel_input(delta_time)

                # Cap update rate
                time.sleep(1/60)

            except Exception as e:
                logging.error(f"Error in input loop: {e}")
                time.sleep(1.0)

    def _process_keyboard_input(self, delta_time: float):
        """Process keyboard inputs"""
        try:
            # Update keyboard processor
            self.keyboard_processor.update(delta_time)
            inputs = self.keyboard_processor.get_inputs()

            # Convert normalized inputs (-1 to 1) to axis values (0 to 32767)
            axis_values = self._convert_to_axis_values(inputs)

            # Send inputs to the game
            self._apply_axis_values(axis_values)

            # Update visualization if available
            if self.keyboard_visualizer:
                self.keyboard_visualizer.update(inputs)

        except Exception as e:
            logging.error(f"Error processing keyboard input: {e}")

    def _process_wheel_input(self, delta_time: float):
        """Process wheel inputs (placeholder for existing wheel code)"""
        # This will be integrated with the existing wheel input code
        pass

    def _convert_to_axis_values(self, inputs: Dict[str, float]) -> Dict[str, int]:
        """Convert normalized inputs to axis values"""
        CENTER = 32768 // 2
        MAX_AXIS = 32767

        try:
            # Convert steering (-1 to 1) to axis value
            steering = int(CENTER + (inputs['steering'] * CENTER))
            steering = max(0, min(MAX_AXIS, steering))

            # Convert throttle and brake (0 to 1) to axis values
            throttle = int(inputs['throttle'] * MAX_AXIS)
            brake = int(inputs['brake'] * MAX_AXIS)

            return {
                'steering': steering,
                'throttle': throttle,
                'brake': brake
            }

        except Exception as e:
            logging.error(f"Error converting input values: {e}")
            return {'steering': CENTER, 'throttle': 0, 'brake': 0}

    def _apply_axis_values(self, axis_values: Dict[str, int]):
        """Apply axis values to the game using direct input"""
        try:
            # Apply steering
            pydirectinput.moveRel(
                axis_values['steering'] - pydirectinput.position()[0],
                0,
                relative=False
            )

            # Apply throttle
            if 'throttle' in axis_values:
                # TODO: Implement actual throttle application
                pass

            # Apply brake
            if 'brake' in axis_values:
                # TODO: Implement actual brake application
                pass

        except Exception as e:
            logging.error(f"Error applying axis values: {e}")

    def set_config(self, config: dict):
        """Update configuration"""
        self.config = config
        self._init_keyboard_support()  # Reinitialize with new config

    def update_key_bindings(self, key_bindings: dict):
        """Update key bindings and reinitialize keyboard support"""
        try:
            self.config['key_bindings'] = key_bindings
            self._init_keyboard_support()
            logging.info("Updated key bindings in input manager")
        except Exception as e:
            logging.error(f"Error updating key bindings: {e}")

    def cleanup(self):
        """Clean up resources"""
        self.running = False
        if self.keyboard_processor:
            self.keyboard_processor.cleanup()
        if self.device_manager:
            self.device_manager.cleanup()
        if hasattr(self, 'input_thread') and self.input_thread.is_alive():
            self.input_thread.join(timeout=1.0)
