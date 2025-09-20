import threading
import time
import winsound
import logging
from typing import Optional
from vehicle_dynamics import VehicleData

class ForceFeedback:
    def __init__(self, vehicle_data: Optional[VehicleData] = None):
        self.active = False
        self.thread = None
        self.stopping = False
        self.vehicle = vehicle_data
        self.last_steering = 0
        self.last_speed = 0
        self.vibration_patterns = {
            'road': {'frequency': 100, 'duration': 50},
            'curb': {'frequency': 200, 'duration': 100},
            'collision': {'frequency': 500, 'duration': 200}
        }

    def set_vehicle(self, vehicle_data: VehicleData):
        """Update the vehicle data for physics calculations"""
        self.vehicle = vehicle_data

    def start(self):
        """Start the force feedback processing"""
        if not self.active:
            self.active = True
            self.stopping = False
            self.thread = threading.Thread(target=self._feedback_loop, daemon=True)
            self.thread.start()
            logging.info("Force feedback started")

    def stop(self):
        """Stop the force feedback processing"""
        if self.active:
            self.stopping = True
            self.active = False
            if self.thread:
                self.thread.join(timeout=1.0)
            logging.info("Force feedback stopped")

    def calculate_force_intensity(self, steering: float, throttle: float, brake: float, speed: float) -> float:
        """Calculate force feedback intensity based on vehicle dynamics"""
        if not self.vehicle:
            return 0.0

        # Base intensity from steering input
        steering_intensity = abs(steering) / 32768.0  # Normalize to 0-1

        # Adjust for vehicle characteristics
        grip_factor = self.vehicle.tire_grip_factor
        weight_dist = self.vehicle.weight_distribution

        # Speed-based adjustment (higher speed = more feedback)
        speed_factor = min(speed / 100.0, 1.0)  # Cap at 100 km/h

        # Weight transfer effect
        weight_transfer = (throttle - brake) * 0.1 * (1 - weight_dist)

        # Combine factors
        intensity = steering_intensity * grip_factor * (1 + speed_factor) * (1 + abs(weight_transfer))

        return min(intensity, 1.0)  # Cap at 1.0

    def _generate_feedback(self, intensity: float, pattern_type: str = 'road'):
        """Generate force feedback using system beep"""
        if intensity <= 0:
            return

        pattern = self.vibration_patterns.get(pattern_type, self.vibration_patterns['road'])

        # Adjust frequency and duration based on intensity
        frequency = int(pattern['frequency'] * (0.5 + intensity * 0.5))
        duration = int(pattern['duration'] * intensity)

        if duration > 0:
            try:
                winsound.Beep(frequency, duration)
            except Exception as e:
                logging.error(f"Error generating force feedback: {e}")

    def update_feedback(self, steering: float, throttle: float, brake: float, speed: float):
        """Update force feedback based on current driving state"""
        if not self.active or not self.vehicle:
            return

        intensity = self.calculate_force_intensity(steering, throttle, brake, speed)

        # Steering vibration
        if abs(steering) > 1000:  # Deadzone threshold
            self._generate_feedback(intensity, 'road')

        # Collision detection (sudden steering changes)
        steering_change = abs(steering - self.last_steering)
        if steering_change > 5000:  # Sudden change threshold
            self._generate_feedback(0.8, 'collision')

        # Road texture simulation
        if intensity > 0.1:
            road_texture_chance = 0.05 * intensity
            if time.time() % 1.0 < road_texture_chance:  # Random road feel
                self._generate_feedback(0.3, 'road')

        self.last_steering = steering
        self.last_speed = speed

    def _feedback_loop(self):
        """Main force feedback processing loop"""
        try:
            while not self.stopping:
                # This loop is kept for compatibility but actual feedback
                # is now driven by update_feedback() calls
                time.sleep(0.016)  # ~60 FPS
        except Exception as e:
            logging.error(f"Error in force feedback loop: {e}")
            self.stopping = True
