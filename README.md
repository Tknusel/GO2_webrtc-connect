# Unitree Go2 WebRTC Control Interface

A comprehensive web-based control interface for the Unitree Go2 robot dog using WebRTC. Features real-time video streaming, virtual joystick controls, programmable movement sequences, and a full command library.

## Features

- 🎮 **Virtual Joystick Controls** - Intuitive dual-joystick interface for robot movement
- 📹 **Real-time Video Streaming** - Live video feed from the robot's camera
- 🤖 **Command Library** - Access to all Unitree Go2 sport commands
- 📝 **Programmable Sequences** - Create and execute custom movement routines
- 🌐 **Web-based Interface** - Control from any device with a web browser
- 🔧 **Two Interface Options** - Basic and Advanced modes

## System Requirements

### Operating System
- macOS (10.14 or later)
- Linux (Ubuntu 20.04+ recommended)

### Software Requirements
- Python 3.9 or later (Python 3.12+ recommended)
- pip (Python package manager)
- git

### Hardware Requirements
- WiFi connection to Unitree Go2 robot
- Computer with webcam support (for video streaming)

## Installation

### Step 1: Install System Dependencies

#### macOS
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3 (if not already installed)
brew install python3

# Install git (if not already installed)
brew install git

# Install PortAudio (required for sounddevice)
brew install portaudio
```

#### Linux (Ubuntu/Debian)
```bash
# Update package list
sudo apt-get update

# Install Python 3 and pip
sudo apt-get install -y python3 python3-pip python3-venv

# Install git
sudo apt-get install -y git

# Install system libraries required by dependencies
sudo apt-get install -y \
    libportaudio2 \
    libsndfile1 \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    libopencv-dev \
    portaudio19-dev
```

### Step 2: Clone the Repository

```bash
cd ~/Downloads
git clone https://github.com/YOUR_USERNAME/GO2_webrtc-connect.git
cd GO2_webrtc-connect-main
```

### Step 3: Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
```

### Step 4: Install Python Dependencies

The `setup.py` file handles all Python dependencies, including the Unitree WebRTC driver from GitHub.

```bash
# Install the package and all dependencies
pip install -e .
```

This will automatically install:
- Flask web framework
- OpenCV for video processing
- aiortc for WebRTC
- All required libraries for the Unitree Go2 driver
- The `go2-webrtc-driver` package from https://github.com/legion1581/unitree_webrtc_connect

**Note:** If you encounter permission errors, you may need to use:
```bash
pip install -e . --user
```

### Step 5: Verify Installation

```bash
# Test that the driver is installed correctly
python3 show_commands.py
```

You should see a list of available sport commands and RTC topics.

## Configuration

### Robot Connection

1. **Power on the Unitree Go2 robot**
2. **Connect to the robot's WiFi network**
   - Default SSID: `Unitree_Go2XXXXXXX`
   - Default password: (check your robot's manual or WiFi sticker)
3. **Note the robot's IP address**
   - Default: `192.168.12.1`
   - If different, update in the Python files

### Test Connection

Run the connection test script to verify setup:

```bash
python3 connection_test.py
```

This will:
- Test network connectivity
- Establish WebRTC connection
- Verify data channels
- Test command execution

## Usage

### Starting the Web Interface

#### Basic Interface (Simplified Controls)
```bash
python3 go2_webinterface_base.py
```

#### Advanced Interface (Full Command Library)
```bash
python3 go2_webinterface_advanced.py
```

The server will start on `http://localhost:5000`

### Accessing the Interface

1. Open your web browser
2. Navigate to `http://localhost:5000`
3. **Important:** Close the official Unitree Go app if running
4. Click "Connect" button
5. Wait for connection (10-30 seconds)

### Using the Controls

#### Virtual Joysticks
- **Left Joystick:** Forward/backward and left/right movement (vx, vy)
- **Right Joystick:** Rotation control (vz)

#### Command Buttons
- **Stand:** Robot stands up
- **Sit:** Robot sits down
- **Hello:** Wave gesture
- **Dance:** Dance routine
- **Stop:** Activate movement mode (required before movements)

#### Programming Sequences

Use the sequence editor to create custom routines:

```javascript
const sequence = [
  { action: 'command', command: 'stand', duration: 2 },
  { action: 'command', command: 'stop', duration: 0.5 },  // Activate movement mode
  { action: 'move', vx: 0.2, vy: 0, vz: 0, duration: 3 },  // Move forward
  { action: 'move', vx: 0, vy: 0, vz: 0.6, duration: 2.5 }, // Turn
  { action: 'command', command: 'sit', duration: 2 }
];
executeSequence(sequence);
```

**Pre-loaded Examples:**
- **Square Pattern:** Robot walks in a square
- **Circle Pattern:** Robot walks in a circle
- **Dance Routine:** Performs hello and dance moves

## Command Reference

### Movement Commands (`move`)
- `vx`: Forward/backward velocity (-0.5 to 0.5 m/s)
- `vy`: Left/right velocity (-0.5 to 0.5 m/s)
- `vz`: Rotation velocity (-1.0 to 1.0 rad/s)
- `duration`: Duration in seconds

### Available Commands (`command`)
- `stop`: Activate movement mode (required before move commands)
- `stand`: Stand up
- `sit`: Sit down
- `damp`: Damped/relaxed mode
- `hello`: Wave gesture
- `dance`: Dance routine

See `COMMAND_REFERENCE.md` for complete documentation.

## Project Structure

```
GO2_webrtc-connect-main/
├── README.md                              # This file
├── setup.py                               # Python package configuration
├── requirements_complete.txt              # Detailed dependency list
├── go2_webinterface_base.py              # Basic web interface
├── go2_webinterface_advanced.py          # Advanced web interface
├── connection_test.py                     # Connection diagnostic tool
├── show_commands.py                       # Display available commands
├── COMMAND_REFERENCE.md                   # Complete command documentation
├── SETUP_INSTRUCTIONS.md                  # Original setup guide
├── Commands.md                            # Command ID reference
└── templates/
    ├── index_webinterface_base.html      # Basic interface HTML
    └── index_webinterface_advanced.html  # Advanced interface HTML
```

## Troubleshooting

### Connection Issues

**Problem:** Cannot connect to robot
- **Solution:** Ensure Unitree Go app is completely closed
- **Solution:** Verify you're connected to the robot's WiFi
- **Solution:** Try rebooting the robot
- **Solution:** Run `connection_test.py` for diagnostics

**Problem:** Connection timeout
- **Solution:** Check if robot IP is correct (default: 192.168.12.1)
- **Solution:** Ensure no firewall is blocking WebRTC
- **Solution:** Robot may be busy - wait 30 seconds and retry

### Movement Issues

**Problem:** Robot doesn't move after commands
- **Solution:** Always send `stop` command before movement sequences
- **Solution:** Check that movement speeds are within safe limits
- **Solution:** Ensure robot is in standing position

### Installation Issues

**Problem:** `pip install` fails
- **Solution:** Update pip: `pip install --upgrade pip`
- **Solution:** Try with `--user` flag: `pip install -e . --user`
- **Solution:** On macOS, may need to install Command Line Tools: `xcode-select --install`

**Problem:** PortAudio errors on macOS
- **Solution:** Install via Homebrew: `brew install portaudio`

**Problem:** OpenCV import errors
- **Solution:** Reinstall: `pip uninstall opencv-python && pip install opencv-python`

### Python Version Issues

**Problem:** Python version too old
- **Solution:** Install Python 3.9+ via Homebrew (macOS) or apt (Linux)
- **Solution:** Use `python3.12` explicitly if multiple versions installed

## Safety Notes

⚠️ **Important Safety Guidelines:**

1. Always maintain clear space around the robot
2. Start with slow movements (low velocity values)
3. Have emergency stop ready (Ctrl+C in terminal)
4. Test new sequences in a safe, open area
5. Do not exceed recommended speed limits:
   - Linear: ±0.5 m/s
   - Angular: ±1.0 rad/s

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Credits

- Original WebRTC driver: [legion1581/unitree_webrtc_connect](https://github.com/legion1581/unitree_webrtc_connect)
- Unitree Robotics for the Go2 platform
- nipplejs for virtual joystick controls

## License

This project is provided as-is for educational and research purposes.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review `COMMAND_REFERENCE.md`
3. Run `connection_test.py` for diagnostics
4. Check the original driver repository for updates

## Version History

- **v1.0.0** - Initial release with basic and advanced interfaces
  - Virtual joystick controls
  - Real-time video streaming
  - Programmable movement sequences
  - Full command library support

---

**Enjoy controlling your Unitree Go2! 🐕🤖**
