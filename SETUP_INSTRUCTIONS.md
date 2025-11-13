# Unitree Go2 Web Interface - Setup Instructions

## Files Included

1. **go2_web_interface_with_stop.py** - Python backend with movement mode handling
2. **index_enhanced_with_stop.html** - HTML frontend with built-in stop commands in examples
3. **COMMAND_REFERENCE.md** - Complete command documentation

## Installation

### Step 1: Setup Files

1. Place `go2_web_interface_with_stop.py` in your project directory
2. Create a `templates` folder in the same directory
3. Place `index_enhanced_with_stop.html` in the `templates` folder
4. Rename `index_enhanced_with_stop.html` to `index_enhanced.html`

**File structure:**
```
your_project/
├── go2_web_interface_with_stop.py
└── templates/
    └── index_enhanced.html
```

### Step 2: Install Dependencies

```bash
pip install flask flask-cors opencv-python aiortc go2-webrtc-driver --break-system-packages
```

### Step 3: Run the Server

```bash
python3 go2_web_interface_with_stop.py
```

### Step 4: Connect

1. Open browser to http://localhost:5000
2. Ensure Unitree Go app is closed
3. Click "Connect"
4. Try the example sequences!

## What's Fixed

### The Movement Mode Problem (SOLVED!)

The robot has two states:
- **Movement Disabled**: Default after commands like stand, sit, hello, dance
- **Movement Enabled**: Only after sending the `stop` command

### The Solution

**Always include a `stop` command before movement sequences:**

```javascript
const sequence = [
  { action: 'command', command: 'stand', duration: 2 },
  { action: 'command', command: 'stop', duration: 0.5 },  // ← CRITICAL!
  { action: 'move', vx: 0.2, vy: 0, vz: 0, duration: 3 }  // Now works!
];
```

## Example Sequences (All Include Stop Command)

### Default Example
```javascript
const sequence = [
  { action: 'command', command: 'stand', duration: 2 },
  { action: 'command', command: 'stop', duration: 0.5 },
  { action: 'wait', duration: 1 },
  { action: 'move', vx: 0.2, vy: 0, vz: 0, duration: 3 },
  { action: 'move', vx: 0, vy: 0, vz: 0.6, duration: 2.5 },
  { action: 'command', command: 'sit', duration: 2 }
];
```

### Square Pattern (Click "Square" button)
```javascript
const sequence = [
  { action: 'command', command: 'stand', duration: 2 },
  { action: 'command', command: 'stop', duration: 0.5 },
  { action: 'wait', duration: 1 },
  // Walk square - 4 sides with turns
  { action: 'move', vx: 0.2, vy: 0, vz: 0, duration: 3 },
  { action: 'move', vx: 0, vy: 0, vz: 0.6, duration: 2.5 },
  { action: 'move', vx: 0.2, vy: 0, vz: 0, duration: 3 },
  { action: 'move', vx: 0, vy: 0, vz: 0.6, duration: 2.5 },
  { action: 'move', vx: 0.2, vy: 0, vz: 0, duration: 3 },
  { action: 'move', vx: 0, vy: 0, vz: 0.6, duration: 2.5 },
  { action: 'move', vx: 0.2, vy: 0, vz: 0, duration: 3 },
  { action: 'command', command: 'sit', duration: 2 }
];
```

### Circle Pattern (Click "Circle" button)
```javascript
const sequence = [
  { action: 'command', command: 'stand', duration: 2 },
  { action: 'command', command: 'stop', duration: 0.5 },
  { action: 'wait', duration: 1 },
  // Move forward while rotating = circle
  { action: 'move', vx: 0.15, vy: 0, vz: 0.4, duration: 10 },
  { action: 'command', command: 'sit', duration: 2 }
];
```

### Dance Routine (Click "Dance" button)
```javascript
const sequence = [
  { action: 'command', command: 'stand', duration: 2 },
  { action: 'wait', duration: 1 },
  { action: 'command', command: 'hello', duration: 3 },
  { action: 'wait', duration: 1 },
  { action: 'command', command: 'dance', duration: 8 },
  { action: 'wait', duration: 1 },
  { action: 'command', command: 'sit', duration: 2 }
];
// Note: Dance routine doesn't need 'stop' since it has no 'move' commands
```

## Command Quick Reference

### Available Commands

| Command | What It Does | Movement Mode After |
|---------|--------------|---------------------|
| `stop` | **Activates movement mode** | ✓ Enabled |
| `stand` | Stand up | ✗ Disabled |
| `sit` | Sit down | ✗ Disabled |
| `damp` | Relax/passive mode | ✗ Disabled |
| `hello` | Wave gesture | ✗ Disabled |
| `dance` | Dance routine | ✗ Disabled |

### Movement Parameters

```javascript
{ action: 'move', vx: 0.2, vy: 0, vz: 0, duration: 3 }
```

- **vx**: Forward(+)/Backward(-) speed, range: -0.5 to 0.5 m/s
- **vy**: Left(+)/Right(-) speed, range: -0.5 to 0.5 m/s
- **vz**: Rotate Left(+)/Right(-), range: -1.0 to 1.0 rad/s
- **duration**: Time in seconds

## Troubleshooting

### Problem: Sequence doesn't move
**Solution:** Make sure you have `{ action: 'command', command: 'stop', duration: 0.5 }` before move commands

### Problem: Movement stops after 'stand' command
**Solution:** Add stop command after stand:
```javascript
{ action: 'command', command: 'stand', duration: 2 },
{ action: 'command', command: 'stop', duration: 0.5 },  // Re-enable movement
{ action: 'move', vx: 0.2, vy: 0, vz: 0, duration: 3 }
```

### Problem: Robot doesn't respond
**Solutions:**
- Ensure Unitree Go app is closed
- Check robot IP address (default: 192.168.12.1)
- Restart the Python server
- Reconnect to robot

## Safety Tips

1. **Start with low speeds** - Use 0.1-0.2 m/s for vx/vy
2. **Test in open space** - Ensure clear area around robot
3. **Use Stop button** - Emergency stop available at all times
4. **Watch battery** - Low battery affects performance
5. **Gradual movements** - Don't make sudden speed changes

## Advanced Usage

### Creating Custom Sequences

```javascript
const sequence = [
  // 1. Always start by enabling movement mode
  { action: 'command', command: 'stop', duration: 0.5 },
  
  // 2. Add your movements
  { action: 'move', vx: 0.2, vy: 0, vz: 0, duration: 2 },
  
  // 3. If you use another command, re-enable movement after
  { action: 'command', command: 'hello', duration: 3 },
  { action: 'command', command: 'stop', duration: 0.5 },
  
  // 4. Continue with more movements
  { action: 'move', vx: 0, vy: 0, vz: 0.5, duration: 3 },
  
  // 5. End safely
  { action: 'command', command: 'sit', duration: 2 }
];
```

### Pattern Templates

**Figure-8:**
```javascript
{ action: 'command', command: 'stop', duration: 0.5 },
{ action: 'move', vx: 0.15, vy: 0, vz: -0.4, duration: 10 },  // Right circle
{ action: 'move', vx: 0.15, vy: 0, vz: 0.4, duration: 10 }    // Left circle
```

**Zigzag:**
```javascript
{ action: 'command', command: 'stop', duration: 0.5 },
{ action: 'move', vx: 0.2, vy: 0.1, vz: 0, duration: 2 },     // Diagonal right
{ action: 'move', vx: 0.2, vy: -0.1, vz: 0, duration: 2 },    // Diagonal left
{ action: 'move', vx: 0.2, vy: 0.1, vz: 0, duration: 2 }      // Diagonal right
```

## Documentation

See **COMMAND_REFERENCE.md** for complete command documentation with detailed explanations and more examples.

## Support

- Check console logs (F12 in browser) for debugging
- Python terminal shows detailed sequence execution
- Test individual commands before complex sequences
- Start simple and build up complexity

Happy robot dog programming! 🐕🤖
