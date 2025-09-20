from tkinter import ttk, StringVar, Scale
import tkinter as tk
from tab_base import TabBase
import logging

class ProfilesTab(TabBase):
    def setup_tab(self):
        # Profile selection frame
        profile_frame = ttk.LabelFrame(self, text="Active Profile")
        profile_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        profile_frame.grid_columnconfigure(0, weight=1)

        # Profile management buttons
        btn_frame = ttk.Frame(profile_frame)
        btn_frame.grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text="Add Game", command=self.main_gui.add_new_game).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Export Profile", command=self.main_gui.export_profile).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Import Profile", command=self.main_gui.import_profile).pack(side='left', padx=2)

class ControlsTab(TabBase):
    def setup_tab(self):
        # Basic controls frame
        basic_frame = ttk.LabelFrame(self, text="Basic Controls")
        basic_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        basic_frame.grid_columnconfigure(1, weight=1)

        # Control sliders
        labels = ["Deadzone", "Steer Speed", "Throttle Speed", "Brake Speed",
                  "Curve Strength", "Response Speed", "Center Snap"]
        vars = [self.main_gui.deadzone, self.main_gui.steer_speed, self.main_gui.throttle_speed,
                self.main_gui.brake_speed, self.main_gui.curve_strength, self.main_gui.response_speed,
                self.main_gui.center_snap]
        ranges = [(0, 8000), (100, 2000), (100, 2000), (100, 2000),
                  (1.0, 3.0), (0.5, 2.0), (0.5, 2.0)]
        resolutions = [1, 1, 1, 1, 0.1, 0.1, 0.1]

        # Add error labels for each control
        self.error_labels = {}

        for i, (label, var, (from_, to_), res) in enumerate(zip(labels, vars, ranges, resolutions)):
            ttk.Label(basic_frame, text=label, width=15).grid(row=i, column=0, padx=5, pady=2)

            # Create and configure the scale widget
            scale = Scale(
                basic_frame,
                from_=from_,
                to=to_,
                resolution=res,
                variable=var,
                orient='horizontal',
                showvalue=True
            )
            scale.grid(row=i, column=1, padx=5, pady=2, sticky="ew")

            # Add validation and error handling
            scale.bind("<ButtonRelease-1>", lambda e, v=var, min=from_, max=to_, name=label:
                      self.validate_control(e, v, min, max, name))

            # Add error label (hidden by default)
            error_label = ttk.Label(basic_frame, text="", foreground="red")
            error_label.grid(row=i, column=2, padx=5, pady=2)
            self.error_labels[label] = error_label

    def validate_control(self, event, var, min_val, max_val, name):
        """Validate control values and show error messages if needed"""
        try:
            value = float(var.get())
            error_label = self.error_labels[name]

            if value < min_val or value > max_val:
                error_label.config(text=f"Value must be between {min_val} and {max_val}")
                # Reset to nearest valid value
                var.set(max(min_val, min(max_val, value)))
            else:
                error_label.config(text="")
                # Log the valid change
                logging.info(f"{name} value changed to: {value}")

            # Notify main application of the change
            self.main_gui.on_control_change(name, value)

        except (ValueError, TypeError) as e:
            self.error_labels[name].config(text="Invalid value")
            logging.error(f"Error in {name} control: {str(e)}")
            # Reset to minimum valid value
            var.set(min_val)

class FeedbackTab(TabBase):
    def setup_tab(self):
        # Force feedback frame
        feedback_frame = ttk.LabelFrame(self, text="Force Feedback Settings")
        feedback_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        feedback_frame.grid_columnconfigure(1, weight=1)

        # Force Feedback toggle
        ttk.Checkbutton(
            feedback_frame,
            text="Enable Force Feedback",
            variable=self.main_gui.force_feedback,
            command=self.main_gui.toggle_force_feedback
        ).grid(row=0, column=0, columnspan=2, padx=5, pady=2)

        # Vibration strength
        ttk.Label(feedback_frame, text="Vibration Strength", width=15).grid(row=1, column=0, padx=5, pady=2)
        Scale(
            feedback_frame,
            from_=0.0,
            to=1.0,
            resolution=0.1,
            variable=self.main_gui.vibration_strength,
            orient='horizontal',
            showvalue=True
        ).grid(row=1, column=1, padx=5, pady=2, sticky="ew")

class KeyBindingsTab(TabBase):
    def setup_tab(self):
        # Key bindings frame
        keys_frame = ttk.LabelFrame(self, text="Key Mappings")
        keys_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        keys_frame.grid_columnconfigure(1, weight=1)

        # Key mapping entries
        self.main_gui.key_vars = {}
        for i, (key, value) in enumerate(self.main_gui.KEY_BINDINGS.items()):
            ttk.Label(keys_frame, text=key.replace('_', ' ').title()).grid(row=i, column=0, padx=5, pady=2)
            var = StringVar(value=value)
            self.main_gui.key_vars[key] = var
            ttk.Entry(keys_frame, textvariable=var, width=10).grid(row=i, column=1, padx=5, pady=2, sticky="w")

class VisualizationTab(TabBase):
    def setup_tab(self):
        # Visualization frame
        viz_frame = ttk.LabelFrame(self, text="Input Visualization")
        viz_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        viz_frame.grid_columnconfigure(0, weight=1)
        viz_frame.grid_rowconfigure(0, weight=1)

        # Create canvas for visualization (tkinter.Canvas, not ttk.Canvas)
        self.main_gui.viz_canvas = tk.Canvas(viz_frame, width=200, height=300, bg='white')
        self.main_gui.viz_canvas.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Initialize visualization
        self.main_gui.input_viz = self.main_gui.InputVisualization(self.main_gui.viz_canvas)
