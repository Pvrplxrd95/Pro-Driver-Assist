"""
Game to Vehicle Mapping System for Pro Driver Assist V2
Maps racing game executables to appropriate vehicle dynamics profiles
"""

import logging
from typing import Dict, Optional
from vehicle_dynamics import VehicleData, vehicle_manager

class GameMapper:
    """Maps game executables to vehicle profiles"""

    def __init__(self):
        # Default mappings for common racing games
        self.game_mappings: Dict[str, str] = {
            # Simulation Racing Games
            'assettocorsa.exe': 'Ferrari 488 GT3',
            'assettocorsa.exe': 'Ferrari 488 GT3',  # Alternative spelling
            'rfactor2.exe': 'Porsche 911 GT3',
            'raceroom.exe': 'BMW M4',
            'iracing.exe': 'Toyota GR86',
            'forzamotorsport7.exe': 'Ford GT',
            'forzamotorsport2023.exe': 'Ford GT',
            'dirtrally2.exe': 'Subaru WRX STI',
            'dirt4.exe': 'Ford Fiesta R5',
            'projectcars2.exe': 'Mercedes AMG GT',
            'f1_2023.exe': 'Mercedes W14',
            'f1_2022.exe': 'Mercedes W13',

            # Arcade Racing Games
            'needforspeed.exe': 'Lamborghini Huracan',
            'nfsunbound.exe': 'Lamborghini Huracan',
            'burnout.exe': 'Pagani Huayra R',
            'thecrew2.exe': 'Ferrari 488 Spider',
            'grid.exe': 'McLaren Senna',
            'f12022.exe': 'McLaren MCL36',

            # Generic mappings for unknown games
            'default': 'BMW M4'
        }

        # Load custom mappings from config if available
        self._load_custom_mappings()

    def _load_custom_mappings(self):
        """Load custom game mappings from config file"""
        try:
            import json
            from pathlib import Path

            config_path = Path(__file__).parent / "config" / "game_mappings.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    custom_mappings = json.load(f)
                    self.game_mappings.update(custom_mappings)
                    logging.info("Loaded custom game mappings")
        except Exception as e:
            logging.warning(f"Could not load custom game mappings: {e}")

    def get_vehicle_for_game(self, game_exe: str) -> Optional[VehicleData]:
        """Get the appropriate vehicle for a game executable"""
        if not game_exe:
            return None

        # Normalize game executable name
        game_key = game_exe.lower().strip()

        # Look up mapping
        vehicle_name = self.game_mappings.get(game_key)

        if vehicle_name:
            vehicle = vehicle_manager.get_vehicle(vehicle_name)
            if vehicle:
                logging.info(f"Mapped {game_exe} to vehicle: {vehicle_name}")
                return vehicle
            else:
                logging.warning(f"Vehicle '{vehicle_name}' not found in database")

        # Fallback to default vehicle
        default_vehicle = vehicle_manager.get_vehicle(self.game_mappings['default'])
        if default_vehicle:
            logging.info(f"Using default vehicle for {game_exe}: {self.game_mappings['default']}")
            return default_vehicle

        logging.warning(f"No suitable vehicle found for {game_exe}")
        return None

    def add_mapping(self, game_exe: str, vehicle_name: str):
        """Add a custom game-to-vehicle mapping"""
        if vehicle_manager.get_vehicle(vehicle_name):
            self.game_mappings[game_exe.lower()] = vehicle_name
            self._save_mappings()
            logging.info(f"Added mapping: {game_exe} -> {vehicle_name}")
        else:
            logging.error(f"Cannot add mapping: vehicle '{vehicle_name}' not found")

    def remove_mapping(self, game_exe: str):
        """Remove a game mapping"""
        if game_exe.lower() in self.game_mappings:
            del self.game_mappings[game_exe.lower()]
            self._save_mappings()
            logging.info(f"Removed mapping for: {game_exe}")

    def get_available_games(self) -> list[str]:
        """Get list of all mapped games"""
        return list(self.game_mappings.keys())

    def get_mapping_info(self, game_exe: str) -> Optional[str]:
        """Get vehicle name for a game executable"""
        return self.game_mappings.get(game_exe.lower())

    def _save_mappings(self):
        """Save custom mappings to config file"""
        try:
            import json
            from pathlib import Path

            config_dir = Path(__file__).parent / "config"
            config_dir.mkdir(exist_ok=True)

            config_path = config_dir / "game_mappings.json"

            # Only save non-default mappings
            default_mappings = {
                'assettocorsa.exe': 'Ferrari 488 GT3',
                'rfactor2.exe': 'Porsche 911 GT3',
                'raceroom.exe': 'BMW M4',
                'iracing.exe': 'Toyota GR86',
                'forzamotorsport7.exe': 'Ford GT',
                'dirtrally2.exe': 'Subaru WRX STI',
                'needforspeed.exe': 'Lamborghini Huracan',
                'grid.exe': 'McLaren Senna',
                'default': 'BMW M4'
            }

            custom_mappings = {
                game: vehicle for game, vehicle in self.game_mappings.items()
                if game not in default_mappings or default_mappings[game] != vehicle
            }

            with open(config_path, 'w') as f:
                json.dump(custom_mappings, f, indent=4)

        except Exception as e:
            logging.error(f"Could not save game mappings: {e}")

# Global instance
game_mapper = GameMapper()
