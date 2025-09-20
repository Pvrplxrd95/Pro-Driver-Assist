"""
Keyboard Input Visualization for Pro Driver Assist
Provides real-time visual feedback for keyboard inputs
"""

import tkinter as tk
from tkinter import ttk
import math
from typing import Dict, Optional
import logging

class KeyboardVisualizer:
    def __init__(self, parent_frame: ttk.Frame):
        self.parent = parent_frame
        self.canvas_width = 300
        self.canvas_height = 200

        # Visual parameters
        self.steering_color = "#2196F3"  # Blue
        self.throttle_color = "#4CAF50"  # Green
        self.brake_color = "#F44336"     # Red
        self.background_color = "#212121" # Dark grey
        self.grid_color = "#424242"      # Lighter grey

        # Set up the UI after defining colors
        self.setup_ui()

        # Animation parameters
        self.smooth_steering = 0.0
        self.smooth_throttle = 0.0
        self.smooth_brake = 0.0
        self.smoothing_factor = 0.3

    def setup_ui(self):
        """Set up the visualization canvas and elements"""
        # Create main canvas
        self.canvas = tk.Canvas(
            self.parent,
            width=self.canvas_width,
            height=self.canvas_height,
            bg=self.background_color,
            highlightthickness=0
        )
        self.canvas.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Create frame for indicators
        self.indicator_frame = ttk.Frame(self.parent)
        self.indicator_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # Add digital indicators
        self.steering_label = ttk.Label(self.indicator_frame, text="Steering: 0%")
        self.steering_label.pack(side="left", padx=5)

        self.throttle_label = ttk.Label(self.indicator_frame, text="Throttle: 0%")
        self.throttle_label.pack(side="left", padx=5)

        self.brake_label = ttk.Label(self.indicator_frame, text="Brake: 0%")
        self.brake_label.pack(side="left", padx=5)

        # Draw initial grid
        self._draw_grid()

    def _draw_grid(self):
        """Draw reference grid on canvas"""
        # Vertical center line
        self.canvas.create_line(
            self.canvas_width/2, 0,
            self.canvas_width/2, self.canvas_height,
            fill=self.grid_color, dash=(4, 4)
        )

        # Horizontal lines for throttle/brake zones
        for i in range(1, 4):
            y = self.canvas_height * (i/4)
            self.canvas.create_line(
                0, y, self.canvas_width, y,
                fill=self.grid_color, dash=(4, 4)
            )

    def update(self, inputs: Dict[str, float]):
        """Update visualization with new input values"""
        try:
            # Extract input values
            steering = inputs.get('steering', 0.0)  # -1.0 to 1.0
            throttle = inputs.get('throttle', 0.0)  # 0.0 to 1.0
            brake = inputs.get('brake', 0.0)       # 0.0 to 1.0

            # Smooth the values for animation
            self.smooth_steering += (steering - self.smooth_steering) * self.smoothing_factor
            self.smooth_throttle += (throttle - self.smooth_throttle) * self.smoothing_factor
            self.smooth_brake += (brake - self.smooth_brake) * self.smoothing_factor

            # Clear previous drawings
            self.canvas.delete("input_viz")

            # Draw steering indicator
            self._draw_steering_indicator(self.smooth_steering)

            # Draw throttle and brake indicators
            self._draw_pedal_indicators(self.smooth_throttle, self.smooth_brake)

            # Update digital readouts
            self._update_labels(steering, throttle, brake)

        except Exception as e:
            logging.error(f"Error updating keyboard visualization: {e}")

    def _draw_steering_indicator(self, steering: float):
        """Draw steering position indicator"""
        # Calculate steering position
        center_x = self.canvas_width / 2
        center_y = self.canvas_height / 2
        radius = min(self.canvas_width, self.canvas_height) / 4

        # Draw steering wheel representation
        angle = steering * math.pi / 2  # Convert to radians (-90 to +90 degrees)

        # Draw wheel circle
        self.canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            outline=self.steering_color,
            width=2,
            tags="input_viz"
        )

        # Draw direction line
        end_x = center_x + radius * math.sin(angle)
        end_y = center_y - radius * math.cos(angle)
        self.canvas.create_line(
            center_x, center_y,
            end_x, end_y,
            fill=self.steering_color,
            width=3,
            tags="input_viz"
        )

    def _draw_pedal_indicators(self, throttle: float, brake: float):
        """Draw throttle and brake indicators"""
        bar_width = 30
        max_height = self.canvas_height * 0.8

        # Draw throttle bar
        throttle_height = max_height * throttle
        throttle_x = self.canvas_width * 0.25
        self.canvas.create_rectangle(
            throttle_x - bar_width/2,
            self.canvas_height - throttle_height,
            throttle_x + bar_width/2,
            self.canvas_height,
            fill=self.throttle_color,
            tags="input_viz"
        )

        # Draw brake bar
        brake_height = max_height * brake
        brake_x = self.canvas_width * 0.75
        self.canvas.create_rectangle(
            brake_x - bar_width/2,
            self.canvas_height - brake_height,
            brake_x + bar_width/2,
            self.canvas_height,
            fill=self.brake_color,
            tags="input_viz"
        )

    def _update_labels(self, steering: float, throttle: float, brake: float):
        """Update digital readout labels"""
        self.steering_label.configure(
            text=f"Steering: {int(steering * 100):+d}%"
        )
        self.throttle_label.configure(
            text=f"Throttle: {int(throttle * 100)}%"
        )
        self.brake_label.configure(
            text=f"Brake: {int(brake * 100)}%"
        )

    def set_active(self, is_active: bool):
        """Set whether keyboard mode is active"""
        if is_active:
            self.parent.grid()
        else:
            self.parent.grid_remove()
