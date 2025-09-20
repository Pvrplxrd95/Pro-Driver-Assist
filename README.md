# Pro Driver Assist

Advanced racing simulation assistance software that provides smooth, dynamic control adaptations for PC racing games. This program enhances your gaming experience by providing intelligent input processing and force feedback optimization.

## Features

### Core Functionality
- Dynamic input smoothing and optimization
- Adaptive force feedback
- Custom game profiles
- Real-time input visualization
- Vehicle-specific dynamics modeling
- Multi-game support

### Control Features
- Adjustable steering sensitivity
- Throttle and brake response curves
- Custom deadzone configuration
- Force feedback optimization
- Center snap adjustment
- Input response speed control

### Vehicle Support
- Extensive vehicle database with detailed parameters
- Support for various vehicle types (Racing, Arcade, Simulation)
- Custom vehicle profile creation
- Dynamic physics modeling

## System Requirements

### Hardware Requirements
- Windows 10/11 64-bit operating system
- DirectInput compatible steering wheel
- Minimum 4GB RAM
- 2.0 GHz dual-core processor or better
- 500MB available disk space

### Software Requirements
- Python 3.10 or newer
- Required Python packages (see requirements.txt)
- DirectX 11 or newer
- .NET Framework 4.7.2 or newer

## Installation

1. **Environment Setup**
   ```bash
   # Create and activate virtual environment
   python -m venv .venv
   .venv\Scripts\activate

   # Install required packages
   pip install -r requirements.txt
   ```

2. **Configuration**
   - Run the program for first-time setup
   - Configure your wheel settings
   - Create game profiles

## Usage

### Basic Setup
1. Launch Pro Driver Assist
2. Select or create a game profile
3. Configure control settings
4. Start your game
5. Use the visualization tab to monitor inputs

### Creating Game Profiles
1. Click "Add Game" button
2. Enter game name
3. Select game executable
4. Configure vehicle type and sensitivity
5. Save profile

### Control Configuration
- **Deadzone**: Adjust input dead zone (0-8000)
- **Steer Speed**: Control steering response (100-2000)
- **Throttle Speed**: Adjust acceleration smoothing (100-2000)
- **Brake Speed**: Configure braking response (100-2000)
- **Curve Strength**: Set input curve (1.0-3.0)
- **Response Speed**: Adjust overall responsiveness (0.5-2.0)
- **Center Snap**: Configure return to center (0.5-2.0)

### Force Feedback Settings
- Enable/disable force feedback
- Adjust vibration strength
- Configure centering force
- Set detail level

## Safety Features

### Emergency Controls
- Emergency override key combination: Ctrl + Shift + Esc
- Automatic failsafe triggers
- Input validation and sanitization
- Error recovery mechanisms

### Monitoring and Diagnostics
- Real-time input monitoring
- System health checks
- Performance metrics
- Error logging and reporting

## Troubleshooting

### Common Issues
1. **Input Lag**
   - Check CPU usage
   - Verify USB port connection
   - Adjust response speed settings

2. **Force Feedback Issues**
   - Verify wheel drivers
   - Check USB power settings
   - Calibrate wheel in Windows

3. **Game Detection**
   - Verify game executable path
   - Check game compatibility
   - Update game profile

### Error Codes
- E001: Input device not found
- E002: Profile loading error
- E003: Configuration error
- E004: Hardware communication error

## Support and Contact

### Getting Help
- GitHub Issues: [Report bugs](https://github.com/Pvrplxrd95/Pro-Driver-Assist/issues)
- Email Support: josiast28@gmail.com


### Contributing
- Fork the repository
- Create feature branch
- Submit pull request
- Follow coding standards

## Legal and Licensing

### Copyright
Copyright © 2025 Josiah Cohen Software. All rights reserved.

### License
This software is protected by copyright law and international treaties.
Unauthorized reproduction or distribution of this software, or any portion of it,
may result in severe civil and criminal penalties.

### Disclaimer
This software is provided "as is" without warranty of any kind. Use at your own risk.
Not responsible for any damage to equipment or injury resulting from use.

## Version History

### Current Version: 2.0.0
- Enhanced force feedback
- Improved vehicle dynamics
- New user interface
- Multi-game support

### Previous Versions
- 1.5.0: Added vehicle profiles
- 1.0.0: Initial release

## Credits and Acknowledgments

### Development Team
- Lead Developer: Josias Tlou
- Physics Engine: Pro Driver Assist Team
- UI Design: Pro Driver Assist Team

### Special Thanks
- Beta testing community
- Contributing developers
- Racing simulation community

