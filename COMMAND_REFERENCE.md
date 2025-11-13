# Unitree Go2 Command Reference

## Overview
This document describes all available commands and actions for the Unitree Go2 robot dog through the web interface.

---

## Movement Commands (API 1008)

Movement commands control the robot's walking/running motion. **Movement mode must be active** to use these commands.

### Action Type: `move`

**Format:**
```javascript
{ action: 'move', vx: 0.2, vy: 0, vz: 0, duration: 3 }
```

**Parameters:**
- `vx`: Forward/backward velocity (m/s)
  - Positive = forward
  - Negative = backward
  - Range: -0.5 to 0.5 m/s (conservative limit)
- `vy`: Left/right velocity (m/s)
  - Positive = left
  - Negative = right
  - Range: -0.5 to 0.5 m/s
- `vz`: Rotation velocity (rad/s)
  - Positive = rotate left (counter-clockwise)
  - Negative = rotate right (clockwise)
  - Range: -1.0 to 1.0 rad/s
- `duration`: How long to move (seconds)

**Examples:**
```javascript
// Move forward for 3 seconds
{ action: 'move', vx: 0.2, vy: 0, vz: 0, duration: 3 }

// Move backward
{ action: 'move', vx: -0.2, vy: 0, vz: 0, duration: 2 }

// Strafe left
{ action: 'move', vx: 0, vy: 0.15, vz: 0, duration: 2 }

// Rotate in place (left)
{ action: 'move', vx: 0, vy: 0, vz: 0.6, duration: 2 }

// Move forward while rotating (curved path)
{ action: 'move', vx: 0.15, vy: 0, vz: 0.4, duration: 5 }

// Diagonal movement
{ action: 'move', vx: 0.2, vy: 0.1, vz: 0, duration: 3 }
```

---

## Robot Commands (Sport Mode)

These commands control the robot's posture and behaviors.

### Action Type: `command`

**Format:**
```javascript
{ action: 'command', command: 'stand', duration: 2 }
```

### Available Commands:

#### 1. **`stop`** (StopMove)
**What it does:** 
- **Activates movement mode** - allows movement commands to work
- Stops any current movement
- **CRITICAL:** This must be called before movement commands will work
- Does NOT make the robot sit or lie down - just enables control

**Usage:**
```javascript
{ action: 'command', command: 'stop', duration: 0.5 }
```

**When to use:**
- At the start of any sequence that includes movements
- After any other command (stand, sit, hello, etc.) before moving
- When you want to stop movement and prepare for new commands

---

#### 2. **`stand`** (StandUp)
**What it does:**
- Robot stands up from sitting or damped position
- Legs fully extended, ready posture
- **WARNING:** Deactivates movement mode! Send `stop` command after to re-enable movement.

**Usage:**
```javascript
{ action: 'command', command: 'stand', duration: 2 }
```

**Typical sequence:**
```javascript
{ action: 'command', command: 'stand', duration: 2 },
{ action: 'command', command: 'stop', duration: 0.5 },  // Re-activate movement
{ action: 'move', vx: 0.2, vy: 0, vz: 0, duration: 3 }  // Now can move
```

---

#### 3. **`sit`** (Sit)
**What it does:**
- Robot sits down (haunches down, front legs extended)
- Low power consumption position
- **WARNING:** Deactivates movement mode

**Usage:**
```javascript
{ action: 'command', command: 'sit', duration: 2 }
```

**Use at end of sequences:**
```javascript
{ action: 'move', vx: 0.2, vy: 0, vz: 0, duration: 3 },
{ action: 'command', command: 'sit', duration: 2 }  // Finish in sitting position
```

---

#### 4. **`damp`** (Damp)
**What it does:**
- Robot goes into relaxed/passive mode
- Legs become compliant, robot may lie down
- Minimal power consumption
- Robot can be manually moved/positioned in this mode
- **WARNING:** Deactivates movement mode

**Usage:**
```javascript
{ action: 'command', command: 'damp', duration: 2 }
```

**When to use:**
- When you want to manually position the robot
- To conserve battery
- Emergency soft-stop

---

#### 5. **`hello`** (Hello)
**What it does:**
- Performs a "hello" gesture/behavior
- Robot may wave or perform greeting motion
- **WARNING:** Deactivates movement mode after completion

**Usage:**
```javascript
{ action: 'command', command: 'hello', duration: 3 }
```

**In a sequence:**
```javascript
{ action: 'command', command: 'stop', duration: 0.5 },
{ action: 'command', command: 'hello', duration: 3 },
{ action: 'command', command: 'stop', duration: 0.5 },  // Re-enable movement
{ action: 'move', vx: 0.2, vy: 0, vz: 0, duration: 2 }
```

---

#### 6. **`dance`** (Dance1)
**What it does:**
- Performs a pre-programmed dance routine
- Robot moves through coordinated motions
- **WARNING:** Deactivates movement mode after completion

**Usage:**
```javascript
{ action: 'command', command: 'dance', duration: 5 }
```

**Note:** Duration should be long enough for the dance to complete (usually 5-10 seconds)

---

## Wait Command

### Action Type: `wait`

**What it does:**
- Pauses sequence execution
- Robot maintains current state
- Useful for timing between actions

**Format:**
```javascript
{ action: 'wait', duration: 2 }
```

**Usage examples:**
```javascript
// Wait before starting to move
{ action: 'command', command: 'stand', duration: 2 },
{ action: 'wait', duration: 1 },  // Give robot time to stabilize
{ action: 'command', command: 'stop', duration: 0.5 },
{ action: 'move', vx: 0.2, vy: 0, vz: 0, duration: 3 }

// Pause between movements
{ action: 'move', vx: 0.2, vy: 0, vz: 0, duration: 2 },
{ action: 'wait', duration: 0.5 },  // Brief pause
{ action: 'move', vx: 0, vy: 0, vz: 0.6, duration: 2 }
```

---

## Complete Sequence Examples

### Example 1: Simple Forward Movement
```javascript
const sequence = [
  { action: 'command', command: 'stop', duration: 0.5 },   // Activate movement mode
  { action: 'move', vx: 0.2, vy: 0, vz: 0, duration: 3 },  // Move forward
  { action: 'command', command: 'sit', duration: 2 }       // Sit down at end
];
```

### Example 2: Square Pattern
```javascript
const sequence = [
  { action: 'command', command: 'stand', duration: 2 },
  { action: 'command', command: 'stop', duration: 0.5 },    // Enable movement
  { action: 'wait', duration: 1 },
  // Side 1
  { action: 'move', vx: 0.2, vy: 0, vz: 0, duration: 3 },
  { action: 'move', vx: 0, vy: 0, vz: 0.6, duration: 2.5 }, // Turn 90°
  // Side 2
  { action: 'move', vx: 0.2, vy: 0, vz: 0, duration: 3 },
  { action: 'move', vx: 0, vy: 0, vz: 0.6, duration: 2.5 },
  // Side 3
  { action: 'move', vx: 0.2, vy: 0, vz: 0, duration: 3 },
  { action: 'move', vx: 0, vy: 0, vz: 0.6, duration: 2.5 },
  // Side 4
  { action: 'move', vx: 0.2, vy: 0, vz: 0, duration: 3 },
  { action: 'command', command: 'sit', duration: 2 }
];
```

### Example 3: Circle Pattern
```javascript
const sequence = [
  { action: 'command', command: 'stand', duration: 2 },
  { action: 'command', command: 'stop', duration: 0.5 },    // Enable movement
  { action: 'wait', duration: 1 },
  // Move forward while turning = circle
  { action: 'move', vx: 0.15, vy: 0, vz: 0.4, duration: 10 },
  { action: 'command', command: 'sit', duration: 2 }
];
```

### Example 4: Dance Routine
```javascript
const sequence = [
  { action: 'command', command: 'stand', duration: 2 },
  { action: 'wait', duration: 1 },
  { action: 'command', command: 'hello', duration: 3 },     // Wave hello
  { action: 'wait', duration: 1 },
  { action: 'command', command: 'dance', duration: 8 },     // Dance
  { action: 'wait', duration: 1 },
  { action: 'command', command: 'sit', duration: 2 }        // Bow
];
```

### Example 5: Figure-8 Pattern
```javascript
const sequence = [
  { action: 'command', command: 'stand', duration: 2 },
  { action: 'command', command: 'stop', duration: 0.5 },
  // First circle (clockwise)
  { action: 'move', vx: 0.15, vy: 0, vz: -0.4, duration: 10 },
  // Second circle (counter-clockwise)  
  { action: 'move', vx: 0.15, vy: 0, vz: 0.4, duration: 10 },
  { action: 'command', command: 'sit', duration: 2 }
];
```

---

## Important Notes

### Movement Mode Activation
**CRITICAL:** The `stop` command is actually the command that **enables** movement mode. This is counterintuitive but correct:
- Commands like `stand`, `sit`, `hello`, `dance` **deactivate** movement mode
- The `stop` command **activates** movement mode
- Always use `{ action: 'command', command: 'stop', duration: 0.5 }` before movement commands

### Command Sequence Best Practices
1. **Start sequences with:** `command: 'stop'` to enable movement
2. **After any gesture/command:** Add `command: 'stop'` before moving again
3. **End sequences with:** `sit` or `damp` for safety
4. **Use waits:** Brief waits between actions help stability

### Safety Limits (Current Configuration)
- Max linear speed (vx, vy): ±0.5 m/s
- Max angular speed (vz): ±1.0 rad/s
- Commands are clamped to these limits automatically

### Coordinate System
- **vx**: Forward/backward (robot's perspective)
- **vy**: Left/right (robot's perspective)  
- **vz**: Rotation (positive = counter-clockwise from above)

---

## Troubleshooting

**Problem:** Robot doesn't move during sequence
- **Solution:** Add `{ action: 'command', command: 'stop', duration: 0.5 }` before move commands

**Problem:** Movement stops after stand/sit command
- **Solution:** Movement mode was deactivated. Add `stop` command to re-enable.

**Problem:** Robot moves erratically
- **Solution:** Reduce speeds (lower vx, vy, vz values)

**Problem:** Sequence doesn't complete
- **Solution:** Check duration values are adequate for each action

---

## Command Summary Table

| Command | API Name | Activates Movement? | Deactivates Movement? | Typical Duration |
|---------|----------|---------------------|----------------------|------------------|
| `stop`  | StopMove | ✓ YES | No | 0.5s |
| `stand` | StandUp | No | ✓ YES | 2s |
| `sit` | Sit | No | ✓ YES | 2s |
| `damp` | Damp | No | ✓ YES | 1s |
| `hello` | Hello | No | ✓ YES | 3s |
| `dance` | Dance1 | No | ✓ YES | 5-8s |
| `move` | Movement (1008) | Requires active mode | No | Variable |
| `wait` | N/A | No change | No change | Variable |
