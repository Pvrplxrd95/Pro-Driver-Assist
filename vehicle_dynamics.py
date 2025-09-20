"""
Vehicle Dynamics Manager for Pro Driver Assist V2
Handles loading and managing vehicle-specific physics data
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass

@dataclass
class VehicleData:
    """Data class for vehicle dynamics parameters"""
    make: str
    model: str
    year: int
    wheelbase: float
    weight_distribution: float  # Front weight distribution (0.5 = 50/50)
    steering_ratio: float
    tire_grip_factor: float
    suspension_settings: Dict[str, float]
    aero_coefficients: Dict[str, float]
    performance_data: Dict[str, float]
    tire_data: Optional[Dict[str, float]] = None
    suv_specific: Optional[Dict[str, float]] = None
    active_systems: Optional[Dict[str, float]] = None
    track_focused_settings: Optional[Dict[str, float]] = None
    track_telemetry: Optional[Dict[str, Dict]] = None

    @property
    def name(self) -> str:
        """Get vehicle name in format 'Make Model'"""
        return f"{self.make} {self.model}"

    @property
    def filename(self) -> str:
        """Get filename for this vehicle"""
        return f"{self.make.lower()}_{self.model.lower().replace(' ', '_')}.json"

class VehicleDynamicsManager:
    """Manages vehicle dynamics data loading and access"""

    def __init__(self):
        self.vehicles: Dict[str, VehicleData] = {}
        self.datasets_path = Path(__file__).parent / "datasets" / "vehicle_dynamics"
        self._load_all_vehicles()

    def _load_all_vehicles(self):
        """Load all vehicle data from JSON files"""
        if not self.datasets_path.exists():
            logging.warning(f"Vehicle dynamics datasets directory not found: {self.datasets_path}")
            return

        for json_file in self.datasets_path.glob("*.json"):
            if json_file.name == "track_surfaces.json":
                continue  # Skip track surfaces file

            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)

                vehicle = VehicleData(**data)
                self.vehicles[vehicle.name] = vehicle
                logging.info(f"Loaded vehicle data: {vehicle.name}")

            except Exception as e:
                logging.error(f"Error loading vehicle data from {json_file}: {e}")

    def get_vehicle(self, name: str) -> Optional[VehicleData]:
        """Get vehicle data by name"""
        return self.vehicles.get(name)

    def get_all_vehicles(self) -> List[VehicleData]:
        """Get list of all available vehicles"""
        return list(self.vehicles.values())

    def get_vehicle_names(self) -> List[str]:
        """Get list of all vehicle names"""
        return list(self.vehicles.keys())

    def save_vehicle(self, vehicle: VehicleData):
        """Save vehicle data to JSON file"""
        if not self.datasets_path.exists():
            self.datasets_path.mkdir(parents=True, exist_ok=True)

        filepath = self.datasets_path / vehicle.filename
        data = {
            "make": vehicle.make,
            "model": vehicle.model,
            "year": vehicle.year,
            "wheelbase": vehicle.wheelbase,
            "weight_distribution": vehicle.weight_distribution,
            "steering_ratio": vehicle.steering_ratio,
            "tire_grip_factor": vehicle.tire_grip_factor,
            "suspension_settings": vehicle.suspension_settings,
            "aero_coefficients": vehicle.aero_coefficients,
            "performance_data": vehicle.performance_data,
            "tire_data": vehicle.tire_data,
            "suv_specific": vehicle.suv_specific,
            "active_systems": vehicle.active_systems
        }

        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
            logging.info(f"Saved vehicle data: {vehicle.name}")
        except Exception as e:
            logging.error(f"Error saving vehicle data: {e}")

# Global instance
vehicle_manager = VehicleDynamicsManager()
