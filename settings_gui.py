import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from PIL import Image, ImageTk
from key_binding_dialog import KeyBindDialog
from settings import Settings, STEERING_MODES
import json
import logging

# Thread-safe message box implementation
class ThreadSafeMessageBox:
    def __init__(self, root=None):
        self.root = root
    def showinfo(self, title, message):
        tk.messagebox.showinfo(title, message)
    def showerror(self, title, message):
        tk.messagebox.showerror(title, message)
    def showwarning(self, title, message):
        tk.messagebox.showwarning(title, message)

class SettingsGUI:
    def __init__(self, settings):
        """
        Initialize GUI with settings
        settings: Either a Settings object or a config dict
        """
        # Convert dict to Settings object if needed
        from settings_new import Settings
        if isinstance(settings, dict):
            self.settings = Settings()
            self.settings.config = settings
        else:
            self.settings = settings

        # Initialize GUI state
        self.root = tk.Tk()
        self.root.title("Pro Driver Assist V2 Settings")

        try:
            self.root.iconbitmap('icon.ico')
        except tk.TclError:
            logging.warning("Could not load icon.ico - using default window icon")

        # Initialize GUI components
        self.msgbox = ThreadSafeMessageBox(self.root)        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Initialize state
        self.tabs = {}
        self._initialized = False
        self._stop_event = threading.Event()

        # Initialize variables from settings
        self.init_variables()

        # Create menu bar and setup GUI
        self.create_menu_bar()
        self.setup_gui()

        # Window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_gui(self):
        """Start the GUI thread if not already running"""
        if not self._gui_running:
            self._gui_thread = threading.Thread(target=self._run_gui, daemon=True)
            self._gui_thread.start()
            self._gui_running = True

            # Add input visualization tab if input manager exists
            if hasattr(self, 'input_manager'):
                self._add_input_visualization()
        else:
            logging.warning("GUI thread already running")

    def _add_input_visualization(self):
        """Add the input visualization tab to the notebook"""
        try:
            if not self.notebook:
                return

            # Create input visualization tab
            viz_frame = ttk.Frame(self.notebook)
            self.notebook.add(viz_frame, text="Input Display")

            # Create keyboard visualizer
            from keyboard_visualizer import KeyboardVisualizer
            viz = KeyboardVisualizer(viz_frame)

            # Store reference in input manager
            if hasattr(self, 'input_manager'):
                self.input_manager.keyboard_visualizer = viz

            logging.info("Added input visualization tab")

        except Exception as e:
            logging.error(f"Error adding input visualization: {e}")

    def save_current(self):
        """Save current settings to config file"""
        try:
            if hasattr(self, 'settings'):
                # Update settings from GUI variables
                self.settings.save()
                self.msgbox.showinfo("Success", "Settings saved successfully!")
            else:
                self.msgbox.showerror("Error", "Settings object not initialized")
        except Exception as e:
            logging.error(f"Failed to save settings: {e}")
            self.msgbox.showerror("Error", f"Failed to save settings: {e}")

    def show_about(self):
        """Show the about dialog"""
        about_text = """
Pro Driver Assist V2
Copyright © 2025 Josias Tlou

A powerful driving simulator assist tool with customizable settings,
force feedback, and input visualization.
        """
        self.msgbox.showinfo("About", about_text)

    def on_profile_change(self, *args):
        """Handle game profile change"""
        try:
            profile_name = self.game_var.get()
            if profile_name != 'Default':
                # Find matching profile
                for game_id, profile in self.settings.get_game_profiles().items():
                    if profile['name'] == profile_name:
                        self.load_game_profile(profile)
                        break
        except Exception as e:
            logging.error(f"Error changing profile: {e}")
            self.msgbox.showerror("Error", f"Failed to change profile: {e}")

    def add_new_game(self):
        """Add a new game profile"""
        try:
            # Create dialog to get game name and executable
            dialog = tk.Toplevel(self.root)
            dialog.title("Add New Game Profile")
            dialog.transient(self.root)
            dialog.grab_set()

            # Game name
            ttk.Label(dialog, text="Game Name:").grid(row=0, column=0, padx=5, pady=5)
            name_var = tk.StringVar()
            ttk.Entry(dialog, textvariable=name_var).grid(row=0, column=1, padx=5, pady=5)

            # Game executable
            ttk.Label(dialog, text="Executable Path:").grid(row=1, column=0, padx=5, pady=5)
            exec_var = tk.StringVar()
            ttk.Entry(dialog, textvariable=exec_var).grid(row=1, column=1, padx=5, pady=5)

            # Add button
            def add_profile():
                name = name_var.get().strip()
                exec_path = exec_var.get().strip()
                if not name or not exec_path:
                    self.msgbox.showerror("Error", "Please fill in both fields")
                    return

                # Create new profile with default settings
                new_profile = {
                    'name': name,
                    'executable': exec_path,
                    'settings': self.settings.get_profile_defaults()
                }

                # Add to settings
                self.settings.add_game_profile(new_profile)

                # Update profile menu
                games = ['Default'] + [profile['name'] for profile in self.settings.get_game_profiles().values()]
                self.profile_menu['menu'].delete(0, 'end')
                for game in games:
                    self.profile_menu['menu'].add_command(label=game, command=tk._setit(self.game_var, game))

                dialog.destroy()
                self.msgbox.showinfo("Success", f"Added profile for {name}")

            ttk.Button(dialog, text="Add", command=add_profile).grid(row=2, column=0, columnspan=2, pady=5)

            # Center dialog
            dialog.update()
            width = dialog.winfo_width()
            height = dialog.winfo_height()
            x = (self.root.winfo_width() - width) // 2
            y = (self.root.winfo_height() - height) // 2
            dialog.geometry(f"+{x}+{y}")

        except Exception as e:
            logging.error(f"Error adding game profile: {e}")
            self.msgbox.showerror("Error", f"Failed to add game profile: {e}")

    def export_profile(self):
        """Export current game profile"""
        try:
            # Get selected profile
            profile_name = self.game_var.get()
            if profile_name == 'Default':
                self.msgbox.showerror("Error", "Cannot export default profile")
                return

            # Create dialog to get export path
            dialog = tk.Toplevel(self.root)
            dialog.title("Export Game Profile")
            dialog.transient(self.root)
            dialog.grab_set()

            # Export path
            ttk.Label(dialog, text="Export Path:").grid(row=0, column=0, padx=5, pady=5)
            path_var = tk.StringVar(value=f"{profile_name}_profile.json")
            ttk.Entry(dialog, textvariable=path_var).grid(row=0, column=1, padx=5, pady=5)

            # Export button
            def do_export():
                export_path = path_var.get().strip()
                if not export_path:
                    self.msgbox.showerror("Error", "Please enter an export path")
                    return

                # Get profile data
                profile_data = None
                for game_id, profile in self.settings.get_game_profiles().items():
                    if profile['name'] == profile_name:
                        profile_data = profile
                        break

                if not profile_data:
                    self.msgbox.showerror("Error", "Profile not found")
                    return

                try:
                    # Save to file
                    with open(export_path, 'w') as f:
                        json.dump(profile_data, f, indent=4)

                    dialog.destroy()
                    self.msgbox.showinfo("Success", f"Profile exported to {export_path}")
                except Exception as e:
                    self.msgbox.showerror("Error", f"Failed to export profile: {e}")

            ttk.Button(dialog, text="Export", command=do_export).grid(row=1, column=0, columnspan=2, pady=5)

            # Center dialog
            dialog.update()
            width = dialog.winfo_width()
            height = dialog.winfo_height()
            x = (self.root.winfo_width() - width) // 2
            y = (self.root.winfo_height() - height) // 2
            dialog.geometry(f"+{x}+{y}")

        except Exception as e:
            logging.error(f"Error exporting profile: {e}")
            self.msgbox.showerror("Error", f"Failed to export profile: {e}")

    def import_profile(self):
        """Import a game profile"""
        try:
            # Create dialog to get import path
            dialog = tk.Toplevel(self.root)
            dialog.title("Import Game Profile")
            dialog.transient(self.root)
            dialog.grab_set()

            # Import path
            ttk.Label(dialog, text="Import Path:").grid(row=0, column=0, padx=5, pady=5)
            path_var = tk.StringVar()
            ttk.Entry(dialog, textvariable=path_var).grid(row=0, column=1, padx=5, pady=5)

            # Import button
            def do_import():
                import_path = path_var.get().strip()
                if not import_path:
                    self.msgbox.showerror("Error", "Please enter an import path")
                    return

                try:
                    # Load profile data
                    with open(import_path, 'r') as f:
                        profile_data = json.load(f)

                    # Validate profile data
                    if not all(key in profile_data for key in ['name', 'executable', 'settings']):
                        self.msgbox.showerror("Error", "Invalid profile file format")
                        return

                    # Add to settings
                    self.settings.add_game_profile(profile_data)

                    # Update profile menu
                    games = ['Default'] + [profile['name'] for profile in self.settings.get_game_profiles().values()]
                    self.profile_menu['menu'].delete(0, 'end')
                    for game in games:
                        self.profile_menu['menu'].add_command(label=game, command=tk._setit(self.game_var, game))

                    dialog.destroy()
                    self.msgbox.showinfo("Success", f"Profile imported from {import_path}")
                except Exception as e:
                    self.msgbox.showerror("Error", f"Failed to import profile: {e}")

            ttk.Button(dialog, text="Import", command=do_import).grid(row=1, column=0, columnspan=2, pady=5)

            # Center dialog
            dialog.update()
            width = dialog.winfo_width()
            height = dialog.winfo_height()
            x = (self.root.winfo_width() - width) // 2
            y = (self.root.winfo_height() - height) // 2
            dialog.geometry(f"+{x}+{y}")

        except Exception as e:
            logging.error(f"Error importing profile: {e}")
            self.msgbox.showerror("Error", f"Failed to import profile: {e}")

    def _run_gui(self):
        """The actual GUI thread function"""
        try:
            self.root = tk.Tk()
            self.root.title("Pro Driver Assist V2 Settings")
            self.msgbox = ThreadSafeMessageBox(self.root)
            self.init_variables()
            self.create_menu_bar()
            self.setup_gui()
            self.initialized.set()
            self.update_visualization()
            self.root.protocol("WM_DELETE_WINDOW", self.on_close)

            # Main loop with cleanup handling
            try:
                self.root.mainloop()
            except tk.TclError as e:
                if "application has been destroyed" not in str(e):
                    logging.error(f"Tkinter error: {e}")
            finally:
                if self.root:
                    self.root.destroy()
        except Exception as e:
            logging.error(f"Error in GUI thread: {e}")
            raise

    def start(self):
        """Start the GUI thread if not already started"""
        if not self._started:
            super().start()
            self._started = True
        else:
            logging.warning("GUI thread already started")

    def create_menu_bar(self):
        """Create the menu bar for the GUI"""
        try:
            menu_bar = tk.Menu(self.root)
            self.root.config(menu=menu_bar)

            # File menu
            file_menu = tk.Menu(menu_bar, tearoff=0)
            file_menu.add_command(label="Save Settings", command=self.save_current)
            file_menu.add_separator()
            file_menu.add_command(label="Exit", command=self.on_close)
            menu_bar.add_cascade(label="File", menu=file_menu)

            # Help menu
            help_menu = tk.Menu(menu_bar, tearoff=0)
            help_menu.add_command(label="About", command=self.show_about)
            menu_bar.add_cascade(label="Help", menu=help_menu)

        except Exception as e:
            logging.error(f"Error creating menu bar: {e}")
            raise

    def run(self):
        try:
            # Initialize GUI
            self.root = tk.Tk()
            self.root.title("Pro Driver Assist V2 Settings")
            self.msgbox = ThreadSafeMessageBox(self.root)

            # Initialize variables first
            self.init_variables()

            # Create menu bar and setup GUI
            self.create_menu_bar()
            self.setup_gui()
            self.initialized.set()
            self.update_visualization()

            # Set up close handler
            self.root.protocol("WM_DELETE_WINDOW", self.on_close)

            # Start GUI event loop with error handling
            self.root.mainloop()
        except Exception as e:
            logging.error(f"Error in GUI thread: {e}")
            raise

    def init_variables(self):
        """Initialize all GUI variables"""
        # Control variables
        self.steer_speed = tk.DoubleVar(value=500)
        self.throttle_speed = tk.DoubleVar(value=500)
        self.brake_speed = tk.DoubleVar(value=500)
        self.curve_strength = tk.DoubleVar(value=1.5)
        self.deadzone = tk.DoubleVar(value=10)
        self.response_speed = tk.DoubleVar(value=1.0)
        self.center_snap = tk.DoubleVar(value=0.8)
        self.steering_mode = tk.StringVar(value="Standard")

        # Force feedback variables
        self.force_feedback = tk.BooleanVar(value=True)
        self.vibration_strength = tk.DoubleVar(value=0.5)

        # Visualization variables
        self.show_wheel = tk.BooleanVar(value=True)
        self.show_pedals = tk.BooleanVar(value=True)
        self.show_speed = tk.BooleanVar(value=True)
        self.show_ff = tk.BooleanVar(value=True)

    def setup_gui(self):
        """Initialize and setup all GUI elements"""
        try:
            # Create menu bar
            self.create_menu_bar()

            # Create notebook for tabs
            self.notebook = ttk.Notebook(self.root)
            self.notebook.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

            # Configure grid weights
            self.root.grid_rowconfigure(0, weight=1)
            self.root.grid_columnconfigure(0, weight=1)

            # Create tabs using the TabBase classes
            from gui_tabs import ProfilesTab, ControlsTab, FeedbackTab, KeyBindingsTab, VisualizationTab

            # Create profiles tab
            profiles_tab = ttk.Frame(self.notebook)
            self.notebook.add(profiles_tab, text='Game Profiles')
            profiles_tab.grid_columnconfigure(0, weight=1)

            # Create profile selection frame
            profile_frame = ttk.LabelFrame(profiles_tab, text="Active Profile")
            profile_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            profile_frame.grid_columnconfigure(0, weight=1)

            # Game profile dropdown
            self.game_var = tk.StringVar(value="Default")
            games = ['Default'] + [profile['name'] for profile in self.settings.get_game_profiles().values()]
            self.profile_menu = ttk.OptionMenu(profile_frame, self.game_var, *games, command=self.on_profile_change)
            self.profile_menu.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

            # Profile management buttons
            btn_frame = ttk.Frame(profile_frame)
            btn_frame.grid(row=1, column=0, padx=5, pady=5)

            ttk.Button(btn_frame, text="Add Game", command=self.add_new_game).pack(side='left', padx=2)
            ttk.Button(btn_frame, text="Export Profile", command=self.export_profile).pack(side='left', padx=2)
            ttk.Button(btn_frame, text="Import Profile", command=self.import_profile).pack(side='left', padx=2)

            # Create controls tab
            controls_tab = ttk.Frame(self.notebook)
            self.notebook.add(controls_tab, text='Controls')
            controls_tab.grid_columnconfigure(0, weight=1)

            # Basic controls frame
            basic_frame = ttk.LabelFrame(controls_tab, text="Basic Controls")
            basic_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            basic_frame.grid_columnconfigure(1, weight=1)

            # Control sliders
            labels = ["Deadzone", "Steer Speed", "Throttle Speed", "Brake Speed",
                      "Curve Strength", "Response Speed", "Center Snap"]
            vars = [self.deadzone, self.steer_speed, self.throttle_speed,
                    self.brake_speed, self.curve_strength,
                    self.response_speed, self.center_snap]

            for i, (label, var) in enumerate(zip(labels, vars)):
                ttk.Label(basic_frame, text=label).grid(row=i, column=0, padx=5, pady=2)
                ttk.Scale(basic_frame, from_=0, to=100, variable=var,
                         orient='horizontal').grid(row=i, column=1, padx=5, pady=2, sticky="ew")

            # Steering mode
            mode_frame = ttk.Frame(basic_frame)
            mode_frame.grid(row=7, column=0, columnspan=2, pady=5, sticky="ew")
            mode_frame.grid_columnconfigure(1, weight=1)

            steering_mode = self.steering_mode.get()
            ttk.Label(mode_frame, text="Steering Mode").grid(row=0, column=0, padx=5, pady=2)
            ttk.OptionMenu(mode_frame, self.steering_mode, steering_mode,
                         *self.settings.STEERING_MODES.keys()).grid(row=0, column=1, padx=5, pady=2, sticky="ew")

            # Create feedback tab
            feedback_tab = ttk.Frame(self.notebook)
            self.notebook.add(feedback_tab, text='Force Feedback')
            feedback_tab.grid_columnconfigure(0, weight=1)

            # Force feedback frame
            feedback_frame = ttk.LabelFrame(feedback_tab, text="Force Feedback Settings")
            feedback_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            feedback_frame.grid_columnconfigure(1, weight=1)

            # Force Feedback toggle
            ttk.Checkbutton(feedback_frame, text="Enable Force Feedback",
                          variable=self.force_feedback,
                          command=self.toggle_force_feedback).grid(row=0, column=0, columnspan=2, padx=5, pady=2)

            # Vibration strength
            ttk.Label(feedback_frame, text="Vibration Strength", width=15).grid(row=1, column=0, padx=5, pady=2)
            ttk.Scale(feedback_frame, from_=0.0, to=1.0, resolution=0.1,
                    variable=self.vibration_strength, orient='horizontal').grid(row=1, column=1, padx=5, pady=2, sticky="ew")

            # Create key bindings tab
            keys_tab = ttk.Frame(self.notebook)
            self.notebook.add(keys_tab, text='Key Bindings')
            keys_tab.grid_columnconfigure(0, weight=1)

            # Key bindings frame
            keys_frame = ttk.LabelFrame(keys_tab, text="Key Mappings")
            keys_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            keys_frame.grid_columnconfigure(1, weight=1)

            # Add key binding dialog
            from key_binding_dialog import KeyBindDialog

            self.key_vars = {}
            for i, (key, value) in enumerate(self.settings.KEY_BINDINGS.items()):
                # Label
                ttk.Label(keys_frame, text=key.replace('_', ' ').title()).grid(
                    row=i, column=0, padx=5, pady=2)

                # Current value display
                var = tk.StringVar(value=value)
                self.key_vars[key] = var
                ttk.Entry(keys_frame, textvariable=var, width=10,
                         state='readonly').grid(row=i, column=1, padx=5, pady=2, sticky="w")

                # Change button
                def make_change_command(key_name, var):
                    return lambda: self.change_key_binding(key_name, var)

                ttk.Button(keys_frame, text="Change",
                          command=make_change_command(key, var)).grid(
                              row=i, column=2, padx=5, pady=2)

            # Reset to defaults button
            ttk.Button(keys_frame, text="Reset to Defaults",
                      command=self.reset_key_bindings).grid(
                          row=len(self.settings.KEY_BINDINGS), column=0,
                          columnspan=3, pady=10)

            # Create visualization tab
            viz_tab = ttk.Frame(self.notebook)
            self.notebook.add(viz_tab, text='Visualization')
            viz_tab.grid_columnconfigure(0, weight=1)

            # Visualization frame
            viz_frame = ttk.LabelFrame(viz_tab, text="Input Visualization")
            viz_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            viz_frame.grid_columnconfigure(1, weight=1)

            # Visualization settings
            ttk.Label(viz_frame, text="Show Wheel").grid(row=0, column=0, padx=5, pady=2)
            ttk.Checkbutton(viz_frame, variable=self.show_wheel).grid(row=0, column=1, padx=5, pady=2)

            ttk.Label(viz_frame, text="Show Pedals").grid(row=1, column=0, padx=5, pady=2)
            ttk.Checkbutton(viz_frame, variable=self.show_pedals).grid(row=1, column=1, padx=5, pady=2)

            ttk.Label(viz_frame, text="Show Speed").grid(row=2, column=0, padx=5, pady=2)
            ttk.Checkbutton(viz_frame, variable=self.show_speed).grid(row=2, column=1, padx=5, pady=2)

            ttk.Label(viz_frame, text="Show Force Feedback").grid(row=3, column=0, padx=5, pady=2)
            ttk.Checkbutton(viz_frame, variable=self.show_ff).grid(row=3, column=1, padx=5, pady=2)

            # Save button at bottom
            save_frame = ttk.Frame(self.root)
            save_frame.grid(row=1, column=0, pady=5)
            ttk.Button(save_frame, text="Save Settings", command=self.save_current).pack()

        except Exception as e:
            logging.error(f"Error setting up GUI elements: {e}")
            raise

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create tabs
        from gui_tabs import ProfilesTab, ControlsTab, FeedbackTab, KeyBindingsTab, VisualizationTab
        self.tabs['profiles'] = ProfilesTab(self.notebook, self)
        self.tabs['controls'] = ControlsTab(self.notebook, self)
        self.tabs['feedback'] = FeedbackTab(self.notebook, self)
        self.tabs['keybindings'] = KeyBindingsTab(self.notebook, self)
        self.tabs['visualization'] = VisualizationTab(self.notebook, self)

        # Add tabs to notebook
        self.notebook.add(self.tabs['profiles'], text='Game Profiles')
        self.notebook.add(self.tabs['controls'], text='Controls')
        self.notebook.add(self.tabs['feedback'], text='Force Feedback')
        self.notebook.add(self.tabs['keybindings'], text='Key Bindings')
        self.notebook.add(self.tabs['visualization'], text='Visualization')

        # Save button at bottom
        save_frame = ttk.Frame(self.root)
        save_frame.grid(row=1, column=0, pady=5)
        ttk.Button(save_frame, text="Save Settings", command=self.save_current).pack()

    def init_variables(self):
        """Initialize GUI variables from settings"""
        try:
            config = self.settings.config

            # Control variables
            self.steer_speed = tk.DoubleVar(value=config.get('steer_speed', 500))
            self.throttle_speed = tk.DoubleVar(value=config.get('throttle_speed', 500))
            self.brake_speed = tk.DoubleVar(value=config.get('brake_speed', 500))
            self.curve_strength = tk.DoubleVar(value=config.get('curve_strength', 1.5))
            self.deadzone = tk.DoubleVar(value=config.get('deadzone_size', 10))
            self.response_speed = tk.DoubleVar(value=config.get('response_speed', 1.0))
            self.center_snap = tk.DoubleVar(value=config.get('center_snap', 0.8))
            self.steering_mode = tk.StringVar(value=config.get('steering_mode', 'Standard'))

            # Force feedback variables
            self.force_feedback = tk.BooleanVar(value=config.get('force_feedback', True))
            self.vibration_strength = tk.DoubleVar(value=config.get('vibration_strength', 0.5))

            # Visualization variables
            viz_settings = config.get('visualization', {})
            self.show_wheel = tk.BooleanVar(value=viz_settings.get('show_wheel', True))
            self.show_pedals = tk.BooleanVar(value=viz_settings.get('show_pedals', True))
            self.show_speed = tk.BooleanVar(value=viz_settings.get('show_speed', True))
            self.show_ff = tk.BooleanVar(value=viz_settings.get('show_ff', True))

            # Game profile variable
            self.game_var = tk.StringVar(value='Default')

            logging.info("GUI variables initialized successfully")

        except Exception as e:
            logging.error(f"Error initializing GUI variables: {e}")
            self.msgbox.showerror("Error", "Failed to initialize settings. Using defaults.")

        def save_current(self):
            """Save current settings to config file"""
            if not self._initialized:
                messagebox.showerror("Error", "GUI not fully initialized")
                return

            try:
                # Collect settings from GUI variables
                settings = {
                    'steer_speed': self.steer_speed.get(),
                    'throttle_speed': self.throttle_speed.get(),
                    'brake_speed': self.brake_speed.get(),
                    'curve_strength': self.curve_strength.get(),
                    'deadzone': self.deadzone.get(),
                    'response_speed': self.response_speed.get(),
                    'center_snap': self.center_snap.get(),
                    'steering_mode': self.steering_mode.get(),
                    'force_feedback': self.force_feedback.get(),
                    'vibration_strength': self.vibration_strength.get(),
                    'show_wheel': self.show_wheel.get(),
                    'show_pedals': self.show_pedals.get(),
                    'show_speed': self.show_speed.get(),
                    'show_ff': self.show_ff.get()
                }

                # Save to config file
                config_dir = Path(__file__).parent / 'config'
                config_dir.mkdir(exist_ok=True)
                config_file = config_dir / 'pro_driver_assist_config.json'

                with open(config_file, 'w') as f:
                    json.dump(settings, f, indent=4)

                messagebox.showinfo("Success", "Settings saved successfully!")

            except Exception as e:
                logging.error(f"Error saving settings: {e}")
                messagebox.showerror("Error", f"Failed to save settings: {e}")

    def change_key_binding(self, key_name, var):
        """Show key binding dialog and update binding"""
        try:
            current_key = var.get()
            dialog = KeyBindDialog(self.root, f"Set {key_name.replace('_', ' ').title()} Key",
                                 current_key)
            result = dialog.get_result()

            if result:
                # Check if key is already used
                for k, v in self.key_vars.items():
                    if k != key_name and v.get() == result:
                        self.msgbox.showwarning(
                            "Key Already Bound",
                            f"'{result}' is already bound to {k.replace('_', ' ').title()}. "
                            "Please choose a different key.")
                        return

                # Update key binding
                var.set(result)
                self.settings.KEY_BINDINGS[key_name] = result
                logging.info(f"Updated {key_name} binding to {result}")

                # Update input manager if it exists
                if hasattr(self, 'input_manager'):
                    self.input_manager.update_key_bindings(self.settings.KEY_BINDINGS)

        except Exception as e:
            logging.error(f"Error changing key binding: {e}")
            self.msgbox.showerror("Error", f"Failed to change key binding: {e}")

    def reset_key_bindings(self):
        """Reset all key bindings to defaults"""
        try:
            if self.msgbox.askyesno("Confirm Reset",
                                   "Are you sure you want to reset all key bindings to defaults?"):
                # Reset to defaults
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

                # Update variables and settings
                for key, value in default_bindings.items():
                    if key in self.key_vars:
                        self.key_vars[key].set(value)
                        self.settings.KEY_BINDINGS[key] = value

                # Update input manager if it exists
                if hasattr(self, 'input_manager'):
                    self.input_manager.update_key_bindings(self.settings.KEY_BINDINGS)

                self.msgbox.showinfo("Success", "Key bindings reset to defaults")
                logging.info("Reset all key bindings to defaults")

        except Exception as e:
            logging.error(f"Error resetting key bindings: {e}")
            self.msgbox.showerror("Error", f"Failed to reset key bindings: {e}")

    def on_close(self):
        """Handle window close event"""
        try:
            if self.root:
                self.root.destroy()

                # Stop force feedback if active
                if hasattr(self, 'ff_system'):
                    self.ff_system.stop()

                # Clean up visualization if exists
                if hasattr(self, 'input_viz'):
                    self.input_viz = None

                # Signal stop event
                if hasattr(self, '_stop_event'):
                    self._stop_event.set()

        except Exception as e:
            logging.error(f"Error handling window close: {e}")
            if self.msgbox:
                self.msgbox.showerror("Error", f"Failed to close GUI: {e}")

        finally:
            # Ensure root window is destroyed properly
            if self.root:
                try:
                    self.root.quit()
                    self.root.destroy()
                except:
                    pass
                self.root = None
