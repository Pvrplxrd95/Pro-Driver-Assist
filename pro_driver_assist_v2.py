#!/usr/bin/env python3

"""
Pro Driver Assist V2
Copyright © 2025 Josias Tlou
All rights reserved.

This program is protected by copyright law and international treaties.
Unauthorized reproduction or distribution of this program, or any portion of it,
may result in severe civil and criminal penalties.

Developer: Josias Tlou
Version: 3.0
Website: https://github.com/pvrplxrd95
Email: josiast28@gmail.com
"""

import json
import logging
import math
import os
import psutil
import queue
import random
import sys
import time
import winsound
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import threading

# Set up logging with both file and console handlers
log_dir = Path(__file__).parent / 'logs'
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f'pro_driver_assist_v2_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Check for missing dependencies
try:
    import keyboard
    import mouse
    from input_device_manager import InputDeviceManager, InputDevice
    from keyboard_processor import KeyboardProcessor
    from keyboard_visualizer import KeyboardVisualizer
    import numpy as np
    import pandas as pd
    import pydirectinput
    import pystray
    import requests
    import tkinter as tk
    from PIL import Image
    from tkinter import ttk, filedialog, messagebox
except ImportError as e:
    logging.error(f"Missing dependency: {e}")
    print("\nError: Missing required dependencies. Please install them using:")
    print("pip install -r requirements.txt")
    sys.exit(1)

# Initialize PyDirectInput
pydirectinput.FAILSAFE = False

# Create config directory and file if they don't exist
config_dir = Path(__file__).parent / 'config'
config_dir.mkdir(exist_ok=True)
config_file = config_dir / 'pro_driver_assist_config.json'

DEFAULT_SETTINGS = {
    'steer_speed': 500,
    'throttle_speed': 700,
    'brake_speed': 800,
    'curve_strength': 1.5,
    'deadzone_size': 2000,
    'steering_mode': 'Comfort',
    'force_feedback': False,
    'vibration_strength': 0.0,
    'response_speed': 1.0,
    'center_snap': 1.0,
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

if not config_file.exists():
    try:
        with open(config_file, 'w') as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)
        logging.info(f"Created default config file at {config_file}")
    except Exception as e:
        pass
        logging.error(f"Failed to create config file: {e}")
        print("\nError: Could not create configuration file.")
        sys.exit(1)

# Constants and Settings
MAX_AXIS = 32768
CENTER_AXIS = MAX_AXIS // 2
CONFIG_FILE = Path(__file__).parent / "pro_driver_assist_settings.json"

VIBRATION_PATTERNS = {
    'road': {'frequency': 100, 'duration': 50},
    'curb': {'frequency': 200, 'duration': 100},
    'collision': {'frequency': 500, 'duration': 200}
}

# Steering modes
STEERING_MODES = {
    'Comfort': {
        'curve_strength': 1.3,
        'response_speed': 0.8,
        'center_snap': 1.2
    },
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
        'throttle_speed': 800,
        'brake_speed': 900,
        'curve_strength': 1.8,
        'deadzone_size': 1500,
        'steering_mode': 'Sport',
        'force_feedback': True,
        'vibration_strength': 0.7,
        'key_mapping': {
            'steer_left': 'a',
            'steer_right': 'd',
            'throttle': 'w',
            'brake': 's',
            'gear_up': 'e',
            'gear_down': 'q',
            'clutch': 'c',
            'handbrake': 'space'
        }
    },
}

# Initial Settings
steering = CENTER_AXIS
throttle = 0
brake = 0
vibration_active = False

# Default settings
steer_speed = 500
throttle_speed = 700
brake_speed = 800
curve_strength = 1.5
deadzone_size = 2000
steering_mode = 'Comfort'
force_feedback = False
vibration_strength = 0.0
response_speed = 1.0
center_snap = 1.0

# Key bindings (can be customized)
KEY_BINDINGS = {
    'steer_left': 'a',
    'steer_right': 'd',
    'throttle': 'w',
    'brake': 's',
    'gear_up': 'shift',
    'gear_down': 'ctrl',
    'clutch': 'space',
    'handbrake': 'alt',
    'exit': 'esc'
}

from settings import Settings
from input_state import InputState
from force_feedback import ForceFeedback
from input_visualization import InputVisualization
from input_recorder import InputRecorder
from vehicle_dynamics import vehicle_manager, VehicleData
from game_mapping import game_mapper
from tab_base import TabBase
from gui_tabs import ProfilesTab, ControlsTab, FeedbackTab, KeyBindingsTab, VisualizationTab

# Create global settings instance
settings = Settings()

class ThreadSafeUI:
    def __init__(self, root):
        self.root = root
        self._lock = threading.Lock()

    def run_on_main(self, func, *args, **kwargs):
        if not self.root:
            return None
        result = None
        done = threading.Event()

        def wrapper():
            nonlocal result
            try:
                with self._lock:
                    result = func(*args, **kwargs)
            finally:
                done.set()

        self.root.after(0, wrapper)
        done.wait(timeout=1.0)
        return result

    def show_error(self, title, message):
        def show():
            messagebox.showerror(title, message)
        self.run_on_main(show)

    def show_info(self, title, message):
        def show():
            messagebox.showinfo(title, message)
        self.run_on_main(show)

class SettingsGUI:
    def __init__(self):
        self.msgbox = None
        self.initialized = threading.Event()
        self._gui_lock = threading.Lock()
        self.KEY_BINDINGS = KEY_BINDINGS
        self.InputVisualization = InputVisualization

        try:
            self.root = tk.Tk()
            self.root.title("Pro Driver Assist Settings")
            self.root.geometry("800x600")
            self.root.minsize(600, 400)

            self.root.grid_rowconfigure(0, weight=1)
            self.root.grid_columnconfigure(0, weight=1)

            self.ui = ThreadSafeUI(self.root)
            self.msgbox = self.ui

            self.init_variables()

            self.notebook = ttk.Notebook(self.root)
            self.notebook.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

            self.profiles_dir = Path(__file__).parent / 'profiles'
            self.profiles_dir.mkdir(exist_ok=True)
            self.profiles = self.load_profiles()
            self.current_profile = tk.StringVar(value="Default")
            self.profile_modified = False

            self.setup_gui_elements()
            self.create_menu_bar()

            self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        except Exception as e:
            logging.error(f"Error initializing settings GUI: {e}")
            if self.msgbox:
                self.msgbox.showerror("Error", f"Failed to initialize settings GUI: {e}")
            raise

    def init_variables(self):
        try:
            self.deadzone = tk.IntVar(value=deadzone_size)
            self.steer_speed = tk.IntVar(value=steer_speed)
            self.throttle_speed = tk.IntVar(value=throttle_speed)
            self.brake_speed = tk.IntVar(value=brake_speed)
            self.curve_strength = tk.DoubleVar(value=curve_strength)
            self.steering_mode = tk.StringVar(value=steering_mode)
            self.force_feedback = tk.BooleanVar(value=force_feedback)
            self.vibration_strength = tk.DoubleVar(value=vibration_strength)
            self.response_speed = tk.DoubleVar(value=response_speed)
            self.center_snap = tk.DoubleVar(value=center_snap)
            self.selected_vehicle = tk.StringVar(value="BMW M4")
        except Exception as e:
            logging.error(f"Error initializing variables: {e}")
            if self.msgbox:
                self.msgbox.showerror("Error", f"Failed to initialize variables: {e}")
            raise

    def setup_gui_elements(self):
        try:
            profiles_tab = ProfilesTab(self.notebook, self)
            controls_tab = ControlsTab(self.notebook, self)
            feedback_tab = FeedbackTab(self.notebook, self)
            keybindings_tab = KeyBindingsTab(self.notebook, self)
            visualization_tab = VisualizationTab(self.notebook, self)

            self.notebook.add(profiles_tab, text='Game Profiles')
            self.notebook.add(controls_tab, text='Controls')
            self.notebook.add(feedback_tab, text='Force Feedback')
            self.notebook.add(keybindings_tab, text='Key Bindings')
            self.notebook.add(visualization_tab, text='Visualization')

            save_frame = ttk.Frame(self.root)
            save_frame.grid(row=1, column=0, pady=5)
            ttk.Button(save_frame, text="Save Settings", command=self.save_current).pack()

        except Exception as e:
            logging.error(f"Error setting up GUI elements: {e}")
            if self.msgbox:
                self.msgbox.showerror("Error", f"Failed to setup GUI elements: {e}")
            raise

    def create_menu_bar(self):
        try:
            menubar = tk.Menu(self.root)
            self.root.config(menu=menubar)

            file_menu = tk.Menu(menubar, tearoff=0)
            file_menu.add_command(label="Save Settings", command=self.save_current)
            file_menu.add_separator()
            file_menu.add_command(label="Export Profile", command=self.export_profile)
            file_menu.add_command(label="Import Profile", command=self.import_profile)
            file_menu.add_separator()
            file_menu.add_command(label="Exit", command=self.on_close)
            menubar.add_cascade(label="File", menu=file_menu)

        except Exception as e:
            logging.error(f"Error creating menu bar: {e}")
            if self.msgbox:
                self.msgbox.showerror("Error", f"Failed to create menu bar: {e}")

    def save_current(self):
        try:
            global steer_speed, throttle_speed, brake_speed, curve_strength, deadzone_size
            global steering_mode, force_feedback, vibration_strength, response_speed, center_snap

            steer_speed = self.steer_speed.get()
            throttle_speed = self.throttle_speed.get()
            brake_speed = self.brake_speed.get()
            curve_strength = self.curve_strength.get()
            deadzone_size = self.deadzone.get()
            steering_mode = self.steering_mode.get()
            force_feedback = self.force_feedback.get()
            vibration_strength = self.vibration_strength.get()
            response_speed = self.response_speed.get()
            center_snap = self.center_snap.get()

            save_settings()

            if self.msgbox:
                self.msgbox.showinfo("Settings Saved", "Your settings have been saved successfully!")
            logging.info("Settings saved successfully")

        except Exception as e:
            logging.error(f"Error saving settings: {e}")
            if self.msgbox:
                self.msgbox.showerror("Error", f"Failed to save settings: {e}")

    def load_profiles(self):
        try:
            profiles = []
            if hasattr(self, 'profiles_dir') and self.profiles_dir.exists():
                for profile_file in self.profiles_dir.glob("*.json"):
                    profiles.append(profile_file.stem)
            return profiles
        except Exception as e:
            logging.error(f"Error loading profiles: {e}")
            return []

    def add_new_game(self):
        """Add a new game profile with executable path"""
        try:
            # Create a dialog for new game entry
            dialog = tk.Toplevel(self.root)
            dialog.title("Add New Game")
            dialog.transient(self.root)
            dialog.grab_set()

            # Create main frame with padding
            main_frame = ttk.Frame(dialog, padding="10")
            main_frame.grid(row=0, column=0, sticky="nsew")

            # Add entry fields
            ttk.Label(main_frame, text="Game Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            name_entry = ttk.Entry(main_frame, width=40)
            name_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

            # Executable path selection
            ttk.Label(main_frame, text="Game Executable:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            path_var = tk.StringVar()
            path_entry = ttk.Entry(main_frame, textvariable=path_var, width=40)
            path_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

            def browse_exe():
                filepath = filedialog.askopenfilename(
                    title="Select Game Executable",
                    filetypes=[
                        ("Executable files", "*.exe"),
                        ("All files", "*.*")
                    ],
                    initialdir="C:/Program Files (x86)/Steam/steamapps/common"
                )
                if filepath:
                    path_var.set(filepath)
                    # Try to extract game name if not already entered
                    if not name_entry.get().strip():
                        import os
                        suggested_name = os.path.splitext(os.path.basename(filepath))[0]
                        name_entry.insert(0, suggested_name.replace("_", " ").title())

            browse_btn = ttk.Button(main_frame, text="Browse...", command=browse_exe)
            browse_btn.grid(row=1, column=2, padx=5, pady=5)

            # Additional game settings frame
            settings_frame = ttk.LabelFrame(main_frame, text="Game Settings", padding="5")
            settings_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=10)

            # Add game settings
            ttk.Label(settings_frame, text="Vehicle Type:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
            vehicle_type = ttk.Combobox(settings_frame, values=["Racing", "Arcade", "Simulation"], state="readonly")
            vehicle_type.set("Racing")
            vehicle_type.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

            ttk.Label(settings_frame, text="Control Sensitivity:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
            sensitivity = ttk.Scale(settings_frame, from_=1, to=10, orient="horizontal")
            sensitivity.set(5)
            sensitivity.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

            # Buttons frame
            btn_frame = ttk.Frame(main_frame)
            btn_frame.grid(row=3, column=0, columnspan=3, pady=10)

            def save_game():
                game_name = name_entry.get().strip()
                exe_path = path_var.get().strip()

                if not game_name:
                    self.msgbox.show_error("Error", "Game name cannot be empty")
                    return

                if not exe_path:
                    self.msgbox.show_error("Error", "Game executable path cannot be empty")
                    return

                if not Path(exe_path).exists():
                    self.msgbox.show_error("Error", "Selected executable file does not exist")
                    return

                try:
                    # Create new profile with additional settings
                    new_profile = self.create_default_profile()
                    new_profile.update({
                        "executable_path": exe_path,
                        "vehicle_type": vehicle_type.get(),
                        "control_sensitivity": sensitivity.get(),
                        "last_launched": "",
                        "auto_launch": False
                    })

                    profile_path = self.profiles_dir / f"{game_name}.json"
                    if profile_path.exists():
                        if not self.msgbox.askyesno("Warning",
                            f"A profile for {game_name} already exists. Do you want to overwrite it?"):
                            return

                    # Save the new profile
                    self.save_profile(new_profile, profile_path)

                    # Update the profile list
                    self.load_profiles()
                    self.current_profile.set(game_name)

                    dialog.destroy()
                    self.msgbox.show_info("Success", f"Added new game profile: {game_name}")

                except Exception as e:
                    self.msgbox.show_error("Error", f"Failed to create game profile: {str(e)}")
                    logging.error(f"Error creating game profile: {e}")

            ttk.Button(btn_frame, text="Save", command=save_game).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)

            # Configure grid weights
            dialog.grid_rowconfigure(0, weight=1)
            dialog.grid_columnconfigure(0, weight=1)
            main_frame.grid_columnconfigure(1, weight=1)

            # Center the dialog
            dialog.update_idletasks()
            dialog.geometry(f"500x400")  # Set initial size
            x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
            y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
            dialog.geometry(f"+{x}+{y}")

        except Exception as e:
            if self.msgbox:
                self.msgbox.show_error("Error", f"Failed to create new game dialog: {str(e)}")
            logging.error(f"Error creating new game dialog: {e}")

    def export_profile(self):
        try:
            profile_name = self.current_profile.get()
            if profile_name == "Default":
                if self.msgbox:
                    self.msgbox.showerror("Error", "Cannot export the Default profile.")
                return

            profile_path = self.profiles_dir / f"{profile_name}.json"
            if not profile_path.exists():
                if self.msgbox:
                    self.msgbox.showerror("Error", f"Profile '{profile_name}' not found.")
                return

            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")],
                initialfile=f"{profile_name}.json",
                title="Export Profile"
            )

            if filename:
                import shutil
                shutil.copy(profile_path, filename)
                if self.msgbox:
                    self.msgbox.showinfo("Success", f"Profile '{profile_name}' exported successfully.")
        except Exception as e:
            logging.error(f"Error exporting profile: {e}")
            if self.msgbox:
                self.msgbox.showerror("Error", f"Failed to export profile: {e}")

    def create_default_profile(self):
        """Create a new default profile with basic settings"""
        return {
            "steer_speed": 500,
            "throttle_speed": 500,
            "brake_speed": 500,
            "curve_strength": 1.5,
            "deadzone": 1000,
            "steering_mode": "normal",
            "force_feedback": True,
            "vibration_strength": 0.5,
            "response_speed": 1.0,
            "center_snap": 1.0,
            "key_bindings": self.KEY_BINDINGS.copy()
        }

    def import_profile(self):
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json")],
                title="Import Profile"
            )

            if filename:
                profile_name = Path(filename).stem
                new_path = self.profiles_dir / f"{profile_name}.json"

                if new_path.exists():
                    if not messagebox.askyesno("Confirm", f"Profile '{profile_name}' already exists. Overwrite?"):
                        return

                import shutil
                shutil.copy(filename, new_path)
                self.profiles = self.load_profiles()
                if self.msgbox:
                    self.msgbox.showinfo("Success", f"Profile '{profile_name}' imported successfully.")
        except Exception as e:
            logging.error(f"Error importing profile: {e}")
            if self.msgbox:
                self.msgbox.showerror("Error", f"Failed to import profile: {e}")

    def toggle_force_feedback(self):
        global force_feedback
        force_feedback = self.force_feedback.get()
        logging.info(f"Force feedback toggled to: {force_feedback}")

    def on_close(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            sys.exit(0)

    def run(self):
        try:
            self.initialized.set()
            self.root.mainloop()
        except Exception as e:
            logging.error(f"Error in GUI main loop: {e}")
            if self.msgbox:
                self.msgbox.showerror("Error", f"Failed to run GUI: {e}")

def save_settings():
    try:
        config = {
            'steer_speed': steer_speed,
            'throttle_speed': throttle_speed,
            'brake_speed': brake_speed,
            'curve_strength': curve_strength,
            'deadzone_size': deadzone_size,
            'steering_mode': steering_mode,
            'force_feedback': force_feedback,
            'vibration_strength': vibration_strength,
            'response_speed': response_speed,
            'center_snap': center_snap,
            'key_bindings': KEY_BINDINGS,
            'game_profiles': GAME_PROFILES
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        logging.info("Settings saved successfully")
    except Exception as e:
        logging.error(f"Error saving settings: {e}")

def load_settings():
    global steer_speed, throttle_speed, brake_speed, curve_strength, deadzone_size
    global steering_mode, force_feedback, vibration_strength, response_speed, center_snap
    global KEY_BINDINGS, GAME_PROFILES

    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                steer_speed = config.get('steer_speed', steer_speed)
                throttle_speed = config.get('throttle_speed', throttle_speed)
                brake_speed = config.get('brake_speed', brake_speed)
                curve_strength = config.get('curve_strength', curve_strength)
                deadzone_size = config.get('deadzone_size', deadzone_size)
                steering_mode = config.get('steering_mode', steering_mode)
                force_feedback = config.get('force_feedback', force_feedback)
                vibration_strength = config.get('vibration_strength', vibration_strength)
                response_speed = config.get('response_speed', response_speed)
                center_snap = config.get('center_snap', center_snap)
                KEY_BINDINGS.update(config.get('key_bindings', {}))
                if 'game_profiles' in config:
                    GAME_PROFILES.update(config['game_profiles'])
            logging.info("Settings loaded successfully")
            return config  # Return the loaded config
    except Exception as e:
        logging.error(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS  # Return default settings on error

def main():
    try:
        # Load settings and ensure defaults
        config = load_settings()

        # Ensure key bindings exist
        if 'key_bindings' not in config:
            config['key_bindings'] = DEFAULT_SETTINGS['key_bindings']
            logging.info("Using default key bindings")

        # Ensure visualization settings exist
        if 'visualization' not in config:
            config['visualization'] = DEFAULT_SETTINGS['visualization']
            logging.info("Using default visualization settings")

        # Create GUI first
        from settings_gui import SettingsGUI
        gui = SettingsGUI(config)

        # Initialize input manager
        from input_manager import InputManager
        input_manager = None
        try:
            input_manager = InputManager(config, gui)
            gui.input_manager = input_manager
            logging.info("Input manager initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize input manager: {e}")

        # Initialize keyboard visualization if GUI is ready
        if input_manager and hasattr(gui, 'notebook'):
            try:
                from keyboard_visualizer import KeyboardVisualizer
                viz_frame = ttk.Frame(gui.notebook)
                gui.notebook.add(viz_frame, text="Input Display")
                viz = KeyboardVisualizer(viz_frame)
                input_manager.keyboard_visualizer = viz
                logging.info("Keyboard visualization initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize keyboard visualization: {e}")

        # Run main loop
        gui.run()

        # Cleanup on exit
        if input_manager:
            input_manager.cleanup()
        logging.error(f"Application startup error: {e}")
        # messagebox.showerror("Application Error", f"A critical error occurred: {e}") # Commented out as messagebox might not be initialized
        sys.exit(1)
    except Exception as e:
        logging.error(f"Application startup error: {e}")
        # messagebox.showerror("Application Error", f"A critical error occurred: {e}") # Commented out as messagebox might not be initialized
        sys.exit(1)

if __name__ == "__main__":
    main()
