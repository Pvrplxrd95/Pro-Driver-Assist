Pro Driver Assist
Copyright © 2025 Josiah Cohen Software
All rights reserved.

Website: https://github.com/josiahcohen
Email: josiah.cohen@example.com

This software is protected by copyright law and international treaties.
Unauthorized reproduction or distribution of this software, or any portion of it,
may result in severe civil and criminal penalties.

--------------------------------------
Pro Driver Assist - Installer Package
--------------------------------------
1. Open 'InstallerScript.iss' with Inno Setup.
2. Click Compile.
3. The installer will be created (ProDriverAssistInstaller.exe).
4. Installer will create a Desktop Shortcut and Auto-launch app after install.

Notes:
- To change the icon, replace 'app.ico' with a new one.
- To change the app name, edit InstallerScript.iss accordingly.

# Pro Driver Assist System v3

A keyboard to virtual joystick mapping tool for racing games with configurable profiles.

## Features
- Keyboard to vJoy mapping for racing games
- Real-time control adjustments
- Game-specific profiles with auto-detection
- Customizable key bindings
- Live input visualization
- Input recording and playback
- Profile import/export
- Comprehensive logging system

## New Features
### Input Visualization
- Real-time steering wheel position
- Throttle and brake pedal indicators
- Live updates at 60Hz

### Input Recording
- Record and playback driving inputs
- Save complex maneuvers for practice
- Accessible through Recording menu
- Automatic timing synchronization

### Profile Management
- Import/Export game profiles
- Auto-detection of running games
- Pre-configured profiles for popular games
- Custom profile creation

### Logging System
- Detailed event logging
- Timestamped log files
- Error tracking and debugging
- Located in the 'logs' folder

## Pre-installed Game Profiles
- Assetto Corsa
- DiRT Rally 2.0
- BeamNG.drive
- Custom game profiles can be added

## Requirements
- Python 3.6 or higher
- vJoy driver installed
- Required Python packages (install using `pip install -r requirements.txt`):
  - keyboard
  - pyvjoy
  - psutil

## Setup
1. Install vJoy driver
2. Install required Python packages: `pip install -r requirements.txt`
3. Run `pro_driver_assist.py`

## Usage
1. Launch the program
2. The settings GUI will appear with:
   - Game profile selection
   - Control settings
   - Input visualization
   - Recording controls
3. Select a game profile or add a new one
4. Adjust settings as needed
5. Use Recording menu to capture and playback inputs
6. Settings are automatically saved

## Controls (Default)
- Arrow Keys: Steering and Throttle/Brake
- Shift: Gear Up
- Ctrl: Gear Down
- Right Shift: Clutch
- Space: Handbrake
- ESC: Exit

## Recording Features
1. Start Recording: Begins capturing all inputs
2. Stop Recording: Saves the recorded sequence
3. Start Playback: Replays recorded inputs
4. Stop Playback: Ends playback mode

## Importing/Exporting Profiles
1. File > Export Profile: Save current profile
2. File > Import Profile: Load saved profile
3. Profiles are saved in JSON format

## Logging
- Logs are stored in the 'logs' folder
- Each session creates a new log file
- Format: pro_driver_assist_YYYYMMDD_HHMMSS.log

# Pro Driver Assist System v3 PRO

A keyboard to virtual joystick mapping tool for racing games with configurable profiles and advanced features.

## PRO Features

### Advanced Sensitivity Controls
- Three steering modes: Comfort, Sport, and Race
- Adjustable response speed and center snap
- Fine-tuned curve control for precision

### Force Feedback
- Simulated force feedback through audio
- Road texture and collision feedback
- Adjustable vibration strength
- Game-specific feedback profiles

### Multi-Device Support
- Keyboard controls
- Mouse steering support
- Real-time device switching
- Custom input mapping

### Advanced Profiles
- Game-specific settings
- Import/Export profiles
- Auto game detection
- Quick profile switching

### Real-time Visualization
- Steering wheel position
- Pedal indicators
- Live input feedback
- Force feedback visualization

### Input Recording
- Record and playback driving inputs
- Save complex maneuvers
- Practice mode with replay
- Automatic timing sync

## Setup
1. Install vJoy driver
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run pro_driver_assist.py

## Controls
### Default Keyboard Controls
- Arrow Keys: Steering and Throttle/Brake
- Shift: Gear Up
- Ctrl: Gear Down
- Right Shift: Clutch
- Space: Handbrake
- ESC: Exit

### Mouse Control
- Click and hold to enable mouse steering
- Mouse position controls steering angle
- Keyboard still controls throttle/brake

## Steering Modes
1. Comfort Mode
   - Smoother steering response
   - Stronger center snap
   - Ideal for casual driving

2. Sport Mode
   - Balanced response
   - Medium center snap
   - Good for general racing

3. Race Mode
   - Quick steering response
   - Reduced center snap
   - Best for competitive racing

## Force Feedback Settings
- Enable/Disable feedback
- Adjust vibration strength
- Customize feedback intensity
- Game-specific profiles

## Profile Management
1. Game Profiles
   - Auto-detection of games
   - Pre-configured settings
   - Custom profile creation
   
2. Import/Export
   - Share profiles
   - Backup settings
   - Transfer between computers

## Advanced Settings
- Response Speed: Adjust steering sensitivity
- Center Snap: Control return-to-center force
- Curve Strength: Fine-tune steering precision
- Deadzone: Eliminate unwanted movement

## Requirements
- Python 3.6 or higher
- vJoy driver
- Required packages (see requirements.txt)
- Windows OS

## Logging
- Detailed event logging
- Error tracking
- Performance monitoring
- Session history
