import json
import os
from typing import Dict, List, Optional

class InputRecorder:
    def __init__(self):
        self.recording = False
        self.recorded_inputs = []
        self.current_recording = []
        self.recordings_dir = 'recordings'
        os.makedirs(self.recordings_dir, exist_ok=True)

    def start_recording(self):
        """Start recording inputs"""
        if not self.recording:
            self.recording = True
            self.current_recording = []

    def stop_recording(self):
        """Stop recording and save inputs"""
        if self.recording:
            self.recording = False
            if self.current_recording:
                self.recorded_inputs.append(self.current_recording)
                self.current_recording = []

    def add_input(self, input_data: Dict[str, float]):
        """Add input data to current recording"""
        if self.recording:
            self.current_recording.append({
                'timestamp': time.time(),
                'steering': input_data.get('steering', 0.0),
                'throttle': input_data.get('throttle', 0.0),
                'brake': input_data.get('brake', 0.0),
                'buttons': input_data.get('buttons', {})
            })

    def save_recording(self, filename: str):
        """Save current recording to file"""
        if not self.current_recording:
            return False

        filepath = os.path.join(self.recordings_dir, filename)
        try:
            with open(filepath, 'w') as f:
                json.dump(self.current_recording, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving recording: {e}")
            return False

    def load_recording(self, filename: str) -> Optional[List[Dict]]:
        """Load a recording from file"""
        filepath = os.path.join(self.recordings_dir, filename)
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading recording: {e}")
            return None

    def get_available_recordings(self) -> List[str]:
        """Get list of available recordings"""
        return [f for f in os.listdir(self.recordings_dir) 
                if f.endswith('.json')]

    def clear_recordings(self):
        """Clear all recorded inputs"""
        self.recorded_inputs = []
        self.current_recording = []
