import tkinter as tk
from tkinter import ttk
from typing import Optional, Tuple, Dict

class InputVisualization:
    def __init__(self, canvas):
        self.canvas = canvas
        self.cached_wheel = None
        self.last_angle = None
        self.last_throttle = None
        self.last_brake = None
        self.last_speed = None
        self.last_ff_state = None
        self.wheel_spokes = [
            (0, -1), (0.866, -0.5), (0.866, 0.5),
            (0, 1), (-0.866, 0.5), (-0.866, -0.5)
        ]
        self.active_buttons = set()
        self.safe_key_names = {
            'shift_l': 'shift',
            'shift_r': 'shift',
            'ctrl_l': 'ctrl',
            'ctrl_r': 'ctrl',
            'alt_l': 'alt',
            'alt_r': 'alt'
        }
        self._dirty = True  # Flag to track if redraw is needed

    def update(self, steering: float, throttle: float, brake: float, speed: float, force_feedback_active: bool):
        """Update visualization only if values have changed significantly"""
        if (self.last_angle != steering or
            self.last_throttle != throttle or
            self.last_brake != brake or
            self.last_speed != speed or
            self.last_ff_state != force_feedback_active):
            
            self.last_angle = steering
            self.last_throttle = throttle
            self.last_brake = brake
            self.last_speed = speed
            self.last_ff_state = force_feedback_active
            self._dirty = True

    def _draw_steering_wheel(self, x: float, y: float, radius: float, inner_radius: float, angle: float):
        """Draw steering wheel with optimized redraw"""
        # Clear previous wheel
        if self.cached_wheel:
            for item in self.cached_wheel:
                self.canvas.delete(item)

        # Draw wheel rim
        wheel = self.canvas.create_oval(
            x - radius, y - radius,
            x + radius, y + radius,
            outline='black', width=2
        )

        # Draw spokes
        spokes = []
        for dx, dy in self.wheel_spokes:
            spoke_angle = math.atan2(dy, dx) + angle
            spoke_dx = math.cos(spoke_angle) * radius
            spoke_dy = math.sin(spoke_angle) * radius
            spoke = self.canvas.create_line(
                x + spoke_dx, y + spoke_dy,
                x + spoke_dx * inner_radius, y + spoke_dy * inner_radius,
                fill='black', width=2
            )
            spokes.append(spoke)

        self.cached_wheel = [wheel] + spokes

    def _draw_pedals(self, throttle: float, brake: float):
        """Draw pedals with optimized redraw"""
        # Draw throttle pedal
        self._draw_pedal(
            250, 300, 100, 30,
            throttle * 30, 'green', 'Throttle'
        )

        # Draw brake pedal
        self._draw_pedal(
            350, 300, 100, 30,
            brake * 30, 'red', 'Brake'
        )

    def _draw_pedal(self, x: float, base_y: float, width: float, height: float,
                   fill_height: float, color: str, label: str):
        """Draw a single pedal with gradient effect"""
        # Draw pedal base
        self.canvas.create_rectangle(
            x, base_y,
            x + width, base_y + height,
            fill='gray', outline='black'
        )

        # Draw filled portion
        self.canvas.create_rectangle(
            x, base_y + height - fill_height,
            x + width, base_y + height,
            fill=color, outline=''
        )

        # Draw label
        self.canvas.create_text(
            x + width/2, base_y + height + 20,
            text=label, font=('Arial', 10)
        )

    def _draw_speed_indicator(self, speed: float):
        """Draw speed indicator"""
        self.canvas.create_text(
            300, 400,
            text=f"Speed: {speed:.1f} km/h",
            font=('Arial', 12),
            fill='black'
        )

    def _draw_force_feedback_indicator(self, x: float, y: float):
        """Draw force feedback indicator"""
        self.canvas.create_rectangle(
            x, y,
            x + 100, y + 20,
            fill='gray', outline='black'
        )
        self.canvas.create_text(
            x + 50, y + 10,
            text="Force Feedback",
            font=('Arial', 10)
        )

    def _adjust_color(self, base_color: str, intensity: float):
        """Adjust color intensity for gradient effect"""
        if base_color == 'green':
            return f"#{int(255 * intensity):02x}ff{int(255 * intensity):02x}"
        elif base_color == 'red':
            return f"ff{int(255 * intensity):02x}{int(255 * intensity):02x}"
        return base_color

    def _safe_check_key(self, key: str) -> bool:
        """Safely check if a key is pressed"""
        try:
            return key in self.active_buttons
        except Exception:
            return False

    def _draw_button_states(self, key_map: Dict[str, str]):
        """Draw button indicators with safe key checking"""
        y = 450
        for key, label in key_map.items():
            safe_key = self.safe_key_names.get(key.lower(), key.lower())
            if self._safe_check_key(safe_key):
                color = 'green'
            else:
                color = 'gray'
            
            self.canvas.create_rectangle(
                250, y,
                350, y + 20,
                fill=color, outline='black'
            )
            self.canvas.create_text(
                300, y + 10,
                text=label,
                font=('Arial', 10)
            )
            y += 30
