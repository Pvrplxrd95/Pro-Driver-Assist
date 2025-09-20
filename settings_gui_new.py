"""
Pro Driver Assist V2
Thread-safe GUI implementation
"""
import tkinter as tk
from tkinter import ttk
import threading
import logging
import time
from thread_safe_ui import ThreadSafeUI
from periodic_updates import PeriodicUpdates
from pro_driver_assist_v2 import KEY_BINDINGS, settings

class SettingsGUI(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

        # Thread synchronization primitives
        self.initialized = threading.Event()
        self._gui_lock = threading.Lock()
        self._updates = None
        self._initialization_timeout = 30  # 30 seconds timeout

        # GUI state variables
        self.root = None
        self.current_game = None
        self.input_viz = None
        self.msgbox = None

        # GUI components
        self.notebook = None
        self.tabs = {}
        self.game_var = None
        self.profile_menu = None

        # Timing variables
        self.last_process_check = 0
        self.process_check_interval = 2.0  # Check every 2 seconds

        # Settings references
        self.KEY_BINDINGS = KEY_BINDINGS
        self.game_profiles = settings.game_profiles

        # GUI state variables
        self.steer_speed = None
        self.throttle_speed = None
        self.brake_speed = None
        self.curve_strength = None
        self.deadzone = None
        self.steering_mode = None
        self.force_feedback = None
        self.vibration_strength = None
        self.response_speed = None
        self.center_snap = None
        self.key_vars = {}

        # Control change callback
        self.control_callbacks = {}

        # Start the thread
        # self.start()  # Removed to avoid double-starting the thread

    def on_control_change(self, control_name, value):
        """Handle control value changes with error checking"""
        try:
            # Validate the new value
            if not isinstance(value, (int, float)):
                raise ValueError(f"Invalid value type for {control_name}: {type(value)}")

            # Apply the change
            if hasattr(self, control_name.lower().replace(" ", "_")):
                setattr(self, control_name.lower().replace(" ", "_"), value)

            # Call any registered callbacks
            if control_name in self.control_callbacks:
                self.control_callbacks[control_name](value)

            # Log the change
            logging.info(f"Control {control_name} updated to {value}")

        except Exception as e:
            logging.error(f"Error updating {control_name}: {str(e)}")
            self.msgbox.showerror("Error", f"Failed to update {control_name}: {str(e)}")

    def run(self):
        try:
            # Initialize main window with timeout handling
            init_start_time = time.time()

            # Initialize main window
            self.root = tk.Tk()
            self.root.title("Pro Driver Assist V2 Settings")

            # Initialize thread-safe UI manager
            self.ui = ThreadSafeUI(self.root)
            self.msgbox = self.ui  # Use thread-safe UI for message boxes

            # Initialize variables and setup GUI
            self.init_variables()
            self.setup_gui()

            # Initialize and start periodic updates
            self._updates = PeriodicUpdates(self)
            self._updates.start()

            # Check initialization time
            if time.time() - init_start_time > self._initialization_timeout:
                raise TimeoutError("GUI initialization timed out")

            # Signal that initialization is complete
            self.initialized.set()

            # Set up close handler and other window properties
            self.root.protocol("WM_DELETE_WINDOW", self.on_close)
            self.root.minsize(400, 300)

            # Start GUI event loop
            self.root.mainloop()

        except TimeoutError as te:
            logging.error(f"GUI initialization timeout: {te}")
            self.cleanup()
        except Exception as e:
            logging.error(f"Error in GUI thread: {e}")
            self.cleanup()

    def cleanup(self):
        """Clean up resources in case of initialization failure"""
        if hasattr(self, 'root') and self.root:
            try:
                self.root.destroy()
            except:
                pass
        if hasattr(self, '_updates') and self._updates:
            try:
                self._updates.stop()
                self._updates.join()
            except:
                pass

    def on_close(self):
        """Handle window closing event properly"""
        try:
            # Stop periodic updates if they're running
            if self._updates:
                self._updates.stop()
                self._updates.join()

            # Destroy the root window
            if self.root:
                self.root.quit()
                self.root.destroy()

        except Exception as e:
            logging.error(f"Error during window close: {e}")
        finally:
            # Ensure the window is destroyed
            if self.root:
                try:
                    self.root.destroy()
                except:
                    pass
                try:
                    self.root.destroy()
                except:
                    pass
