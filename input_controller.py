"""
Input Controller for Pro Driver Assist
Manages both keyboard and steering wheel inputs
"""

import logging
import time
import threading
from typing import Dict, Optional
from pathlib import Path
from input_device_manager import InputDeviceManager, InputDevice
from keyboard_processor import KeyboardProcessor
from keyboard_visualizer import KeyboardVisualizer
import tkinter as tk
from tkinter import ttk

class InputController:
    def __init__(self, gui):
        self.gui = gui
        self.device_manager = InputDeviceManager()
        self.keyboard_processor = None
        self.keyboard_visualizer = None
        self.last_update_time = time.time()

        # Initialize keyboard support
        self._init_keyboard_support()

        # Register for device changes
        self.device_manager.register_device_changed_callback(self.on_device_changed)

        # Start update thread
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()

    def _init_keyboard_support(self):
        """Initialize keyboard support components"""
        try:
            # Initialize keyboard processor
            config = self.device_manager.get_keyboard_config()
            self.keyboard_processor = KeyboardProcessor(config)

            # Initialize visualization if we have a GUI
            if hasattr(self.gui, 'notebook'):
                viz_frame = ttk.Frame(self.gui.notebook)
                self.keyboard_visualizer = KeyboardVisualizer(viz_frame)
                self.gui.notebook.add(viz_frame, text="Keyboard Input")
                viz_frame.grid_rowconfigure(0, weight=1)
                viz_frame.grid_columnconfigure(0, weight=1)

            logging.info("Keyboard support initialized successfully")

        except Exception as e:
            logging.error(f"Error initializing keyboard support: {e}")
            raise

    def on_device_changed(self, device: InputDevice):
        """Handle input device changes"""
        try:
            logging.info(f"Input device changed to: {device.value}")

            if device == InputDevice.KEYBOARD:
                if self.keyboard_visualizer:
                    self.keyboard_visualizer.set_active(True)
                logging.info("Activated keyboard mode")

            elif device == InputDevice.STEERING_WHEEL:
                if self.keyboard_visualizer:
                    self.keyboard_visualizer.set_active(False)
                logging.info("Activated steering wheel mode")

        except Exception as e:
            logging.error(f"Error handling device change: {e}")

    def _update_loop(self):
        """Main update loop for input processing"""
        while self.running:
            try:
                current_time = time.time()
                delta_time = current_time - self.last_update_time
                self.last_update_time = current_time

                # Get current input device
                device = self.device_manager.get_current_device()

                if device == InputDevice.KEYBOARD and self.keyboard_processor:
                    # Update keyboard processing
                    self.keyboard_processor.update(delta_time)
                    inputs = self.keyboard_processor.get_inputs()

                    # Update visualization
                    if self.keyboard_visualizer:
                        self.keyboard_visualizer.update(inputs)

                    # Apply inputs to game
                    self._apply_inputs(inputs)

                elif device == InputDevice.STEERING_WHEEL:
                    # Handle wheel inputs (existing wheel code)
                    pass

                time.sleep(1/60)  # Cap at 60 Hz

            except Exception as e:
                logging.error(f"Error in input update loop: {e}")
                time.sleep(1)

    def _apply_inputs(self, inputs: Dict[str, float]):
        """Apply processed inputs to the game"""
        try:
            steering = inputs.get('steering', 0.0)   # -1.0 to 1.0
            throttle = inputs.get('throttle', 0.0)   # 0.0 to 1.0
            brake = inputs.get('brake', 0.0)         # 0.0 to 1.0

            # Convert normalized values to game inputs
            # TODO: Implement actual game input application
            pass

        except Exception as e:
            logging.error(f"Error applying inputs: {e}")

    def cleanup(self):
        """Clean up resources"""
        self.running = False
        if self.keyboard_processor:
            self.keyboard_processor.cleanup()
        self.device_manager.cleanup()
        if self.update_thread.is_alive():
            self.update_thread.join(timeout=1.0)
