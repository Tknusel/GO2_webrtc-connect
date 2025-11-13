#!/usr/bin/env python3
"""
Unitree Go2 Web Interface - Enhanced with Joystick Control and Movement Sequences
FIXED VERSION with extensive debugging and sequence monitoring
"""

from flask import Flask, render_template, Response, jsonify, request
from flask_cors import CORS
import cv2
import asyncio
import threading
import time
from queue import Queue
import logging
import json
import os

# Suppress OpenCV warnings
os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'
cv2.setLogLevel(0)

from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
from go2_webrtc_driver.constants import RTC_TOPIC, SPORT_CMD
from aiortc import MediaStreamTrack

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.WARNING)

# Global variables
robot_connection = None
frame_queue = Queue(maxsize=10)
is_connected = False
channels_ready = False
asyncio_loop = None
asyncio_thread = None
movement_active = False
current_velocity = {'x': 0.0, 'y': 0.0, 'z': 0.0}
sequence_running = False
sequence_abort = False

ROBOT_IP = "192.168.12.1"

# Movement limits
MAX_LINEAR_SPEED = 1.0  # m/s
MAX_ANGULAR_SPEED = 1.5  # rad/s

@app.route('/')
def index():
    return render_template('index_enhanced.html')

@app.route('/connect', methods=['POST'])
def connect():
    global robot_connection, is_connected, channels_ready, asyncio_loop, asyncio_thread
    
    data = request.json
    ip = data.get('ip', ROBOT_IP)
    
    if is_connected:
        return jsonify({'status': 'info', 'message': 'Already connected'})
    
    try:
        print(f"Connecting to robot at {ip}...")
        
        robot_connection = Go2WebRTCConnection(
            WebRTCConnectionMethod.LocalSTA,
            ip=ip
        )
        
        # Async callback for video
        async def recv_camera_stream(track: MediaStreamTrack):
            while True:
                try:
                    frame = await track.recv()
                    img = frame.to_ndarray(format="bgr24")
                    if not frame_queue.full():
                        frame_queue.put(img)
                except Exception as e:
                    print(f"Video stream error: {e}")
                    break
        
        # Enhanced setup with channel waiting
        async def setup():
            global channels_ready
            try:
                # Connect to robot
                print("Establishing WebRTC connection...")
                await robot_connection.connect()
                print("✓ WebRTC connection established")
                
                # Wait for data channel to be ready
                print("Waiting for data channel...")
                max_wait = 10  # seconds
                wait_time = 0
                while wait_time < max_wait:
                    if hasattr(robot_connection, 'datachannel') and robot_connection.datachannel:
                        if hasattr(robot_connection.datachannel, 'pub_sub'):
                            print("✓ Data channel ready!")
                            break
                    await asyncio.sleep(0.5)
                    wait_time += 0.5
                
                if wait_time >= max_wait:
                    raise Exception("Data channel did not initialize in time")
                
                # IMPORTANT: Check and set motion mode to "normal"
                print("Checking motion mode...")
                try:
                    response = await robot_connection.datachannel.pub_sub.publish_request_new(
                        RTC_TOPIC["MOTION_SWITCHER"], 
                        {"api_id": 1001}
                    )
                    
                    print(f"Motion mode response: {response}")
                    
                    if response['data']['header']['status']['code'] == 0:
                        data = json.loads(response['data']['data'])
                        current_mode = data['name']
                        print(f"Current motion mode: {current_mode}")
                        
                        if current_mode != "normal":
                            print(f"Switching from '{current_mode}' to 'normal' mode...")
                            switch_response = await robot_connection.datachannel.pub_sub.publish_request_new(
                                RTC_TOPIC["MOTION_SWITCHER"], 
                                {
                                    "api_id": 1002,
                                    "parameter": {"name": "normal"}
                                }
                            )
                            print(f"Mode switch response: {switch_response}")
                            await asyncio.sleep(3)  # Wait longer for mode switch
                            print("✓ Switched to normal mode")
                        else:
                            print("✓ Already in normal mode")
                    else:
                        print(f"⚠️  Motion mode check returned error code: {response['data']['header']['status']['code']}")
                except Exception as e:
                    print(f"⚠️  Could not set motion mode: {e}")
                    import traceback
                    traceback.print_exc()
                    print("Continuing anyway...")
                
                # Start video
                print("Starting video stream...")
                robot_connection.video.switchVideoChannel(True)
                robot_connection.video.add_track_callback(recv_camera_stream)
                print("✓ Video stream started")
                
                channels_ready = True
                print("✓ All channels ready!")
                
            except Exception as e:
                print(f"Setup error: {e}")
                channels_ready = False
                raise
        
        # Run async in thread
        def run_asyncio_loop(loop):
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(setup())
                loop.run_forever()
            except Exception as e:
                print(f"Asyncio loop error: {e}")
        
        asyncio_loop = asyncio.new_event_loop()
        asyncio_thread = threading.Thread(target=run_asyncio_loop, args=(asyncio_loop,))
        asyncio_thread.daemon = True
        asyncio_thread.start()
        
        # Wait for channels to be ready
        print("Waiting for initialization...")
        for i in range(15):  # Wait up to 15 seconds
            if channels_ready:
                break
            time.sleep(1)
            print(f"Waiting... {i+1}s")
        
        if not channels_ready:
            raise Exception("Failed to initialize channels")
        
        is_connected = True
        print("✓ Connection complete and ready!")
        
        return jsonify({
            'status': 'connected', 
            'message': 'Successfully connected to robot and channels ready'
        })
    
    except Exception as e:
        is_connected = False
        channels_ready = False
        print(f"Connection failed: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/disconnect', methods=['POST'])
def disconnect():
    global robot_connection, is_connected, channels_ready, asyncio_loop, asyncio_thread, movement_active
    
    try:
        is_connected = False
        channels_ready = False
        movement_active = False
        
        if asyncio_loop:
            asyncio_loop.call_soon_threadsafe(asyncio_loop.stop)
        
        if asyncio_thread:
            asyncio_thread.join(timeout=2)
        
        robot_connection = None
        asyncio_loop = None
        asyncio_thread = None
        
        while not frame_queue.empty():
            frame_queue.get()
        
        print("Disconnected from robot")
        return jsonify({'status': 'disconnected', 'message': 'Disconnected from robot'})
    
    except Exception as e:
        print(f"Disconnect error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/status')
def status():
    return jsonify({
        'connected': is_connected,
        'channels_ready': channels_ready,
        'ip': ROBOT_IP,
        'movement_active': movement_active,
        'velocity': current_velocity
    })

@app.route('/command', methods=['POST'])
def execute_command():
    global robot_connection, asyncio_loop
    
    if not is_connected or not channels_ready:
        return jsonify({
            'status': 'error', 
            'message': 'Not connected or channels not ready'
        }), 400
    
    if not robot_connection or not asyncio_loop:
        return jsonify({'status': 'error', 'message': 'Robot connection not available'}), 400
    
    data = request.json
    command = data.get('command')
    
    try:
        print(f"Executing command: {command}")
        
        # Map commands
        command_mapping = {
            'stand': 'StandUp',
            'sit': 'Sit',
            'lie': 'Damp',
            'damp': 'Damp',
            'stop': 'StopMove',
            'hello': 'Hello',
            'dance': 'Dance1'
        }
        
        sport_cmd = command_mapping.get(command)
        
        if not sport_cmd or sport_cmd not in SPORT_CMD:
            return jsonify({
                'status': 'error',
                'message': f"Unknown command: {command}"
            }), 400
        
        # Check datachannel is available
        if not hasattr(robot_connection, 'datachannel') or not robot_connection.datachannel:
            return jsonify({
                'status': 'error',
                'message': 'Data channel not available'
            }), 500
        
        # Send command
        async def send_command():
            try:
                print(f"Sending sport command API ID: {SPORT_CMD[sport_cmd]}")
                response = await robot_connection.datachannel.pub_sub.publish_request_new(
                    RTC_TOPIC["SPORT_MOD"],
                    {"api_id": SPORT_CMD[sport_cmd]}
                )
                print(f"Command response: {response}")
                print(f"✓ Command {sport_cmd} sent successfully")
            except Exception as e:
                print(f"Command send error: {e}")
                raise
        
        future = asyncio.run_coroutine_threadsafe(send_command(), asyncio_loop)
        future.result(timeout=5)
        
        return jsonify({'status': 'success', 'command': command})
    
    except Exception as e:
        print(f"Command error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/move', methods=['POST'])
def move():
    """Control robot movement with velocity commands"""
    global robot_connection, asyncio_loop, current_velocity, movement_active
    
    if not is_connected or not channels_ready:
        return jsonify({
            'status': 'error', 
            'message': 'Not connected or channels not ready'
        }), 400
    
    if not robot_connection or not asyncio_loop:
        return jsonify({
            'status': 'error',
            'message': 'Robot connection not available'
        }), 400
    
    data = request.json
    vx = float(data.get('vx', 0.0))  # Forward/backward (m/s)
    vy = float(data.get('vy', 0.0))  # Left/right strafe (m/s)
    vz = float(data.get('vz', 0.0))  # Rotation (rad/s)
    
    # Apply limits
    vx = max(-MAX_LINEAR_SPEED, min(MAX_LINEAR_SPEED, vx))
    vy = max(-MAX_LINEAR_SPEED, min(MAX_LINEAR_SPEED, vy))
    vz = max(-MAX_ANGULAR_SPEED, min(MAX_ANGULAR_SPEED, vz))
    
    current_velocity = {'x': vx, 'y': vy, 'z': vz}
    movement_active = (abs(vx) > 0.01 or abs(vy) > 0.01 or abs(vz) > 0.01)
    
    try:
        async def send_movement():
            try:
                payload = {
                    "api_id": 1008,
                    "parameter": {
                        "x": vx,
                        "y": vy,
                        "z": vz
                    }
                }
                print(f"Sending movement: {payload}")
                response = await robot_connection.datachannel.pub_sub.publish_request_new(
                    RTC_TOPIC["SPORT_MOD"],
                    payload
                )
                print(f"Movement response: {response}")
            except Exception as e:
                print(f"Movement send error: {e}")
                raise
        
        future = asyncio.run_coroutine_threadsafe(send_movement(), asyncio_loop)
        future.result(timeout=1)
        
        return jsonify({
            'status': 'success',
            'velocity': current_velocity
        })
    
    except Exception as e:
        print(f"Movement error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/sequence/execute', methods=['POST'])
def execute_sequence():
    """Execute a sequence of movements"""
    global robot_connection, asyncio_loop, sequence_running, sequence_abort
    
    if not is_connected or not channels_ready:
        return jsonify({
            'status': 'error', 
            'message': 'Not connected or channels not ready'
        }), 400
    
    if sequence_running:
        return jsonify({
            'status': 'error',
            'message': 'Sequence already running. Use stop endpoint first.'
        }), 400
    
    data = request.json
    sequence = data.get('sequence', [])
    
    if not sequence:
        return jsonify({'status': 'error', 'message': 'Empty sequence'}), 400
    
    print(f"\n{'='*60}")
    print(f"SEQUENCE EXECUTION STARTED - {len(sequence)} steps")
    print(f"{'='*60}")
    
    try:
        sequence_running = True
        sequence_abort = False
        
        async def run_sequence():
            global sequence_running, sequence_abort
            try:
                print("▶️  Starting sequence execution in async loop...")
                
                # CRITICAL: Send StopMove command to activate movement mode
                # This is essential for movement commands to work
                print("🔧 Activating movement mode (sending StopMove)...")
                await robot_connection.datachannel.pub_sub.publish_request_new(
                    RTC_TOPIC["SPORT_MOD"],
                    {"api_id": SPORT_CMD["StopMove"]}
                )
                await asyncio.sleep(0.5)  # Wait for mode activation
                print("✓ Movement mode activated")
                
                for i, step in enumerate(sequence):
                    if sequence_abort:
                        print("\n⛔ SEQUENCE ABORTED BY USER")
                        await robot_connection.datachannel.pub_sub.publish_request_new(
                            RTC_TOPIC["SPORT_MOD"],
                            {
                                "api_id": 1008,
                                "parameter": {"x": 0.0, "y": 0.0, "z": 0.0}
                            }
                        )
                        break
                    
                    action = step.get('action')
                    duration = step.get('duration', 1.0)
                    
                    print(f"\n[Step {i+1}/{len(sequence)}] Action: {action}, Duration: {duration}s")
                    
                    if action == 'move':
                        vx = float(step.get('vx', 0.0))
                        vy = float(step.get('vy', 0.0))
                        vz = float(step.get('vz', 0.0))
                        
                        vx = max(-MAX_LINEAR_SPEED, min(MAX_LINEAR_SPEED, vx))
                        vy = max(-MAX_LINEAR_SPEED, min(MAX_LINEAR_SPEED, vy))
                        vz = max(-MAX_ANGULAR_SPEED, min(MAX_ANGULAR_SPEED, vz))
                        
                        print(f"  Moving: vx={vx:.2f}, vy={vy:.2f}, vz={vz:.2f}")
                        
                        end_time = time.time() + duration
                        iteration = 0
                        while time.time() < end_time:
                            if sequence_abort:
                                break
                            
                            try:
                                payload = {
                                    "api_id": 1008,
                                    "parameter": {
                                        "x": vx,
                                        "y": vy,
                                        "z": vz
                                    }
                                }
                                if iteration == 0:  # Log first command details
                                    print(f"    First movement payload: {payload}")
                                
                                response = await robot_connection.datachannel.pub_sub.publish_request_new(
                                    RTC_TOPIC["SPORT_MOD"],
                                    payload
                                )
                                
                                if iteration == 0:  # Log first response
                                    print(f"    First movement response: {response}")
                                
                                iteration += 1
                                if iteration % 10 == 0:
                                    print(f"    ...movement command sent ({iteration} iterations)")
                            except Exception as e:
                                print(f"  ⚠️  Movement command failed: {e}")
                                import traceback
                                traceback.print_exc()
                            
                            await asyncio.sleep(0.1)
                        
                        print(f"  ✓ Movement complete ({iteration} commands sent)")
                        
                        print("  Stopping movement...")
                        await robot_connection.datachannel.pub_sub.publish_request_new(
                            RTC_TOPIC["SPORT_MOD"],
                            {
                                "api_id": 1008,
                                "parameter": {"x": 0.0, "y": 0.0, "z": 0.0}
                            }
                        )
                    
                    elif action == 'command':
                        command = step.get('command')
                        command_mapping = {
                            'stand': 'StandUp',
                            'sit': 'Sit',
                            'damp': 'Damp',
                            'stop': 'StopMove',
                            'hello': 'Hello',
                            'dance': 'Dance1'
                        }
                        
                        sport_cmd = command_mapping.get(command)
                        if sport_cmd and sport_cmd in SPORT_CMD:
                            print(f"  Sending command: {command} ({sport_cmd})")
                            try:
                                await robot_connection.datachannel.pub_sub.publish_request_new(
                                    RTC_TOPIC["SPORT_MOD"],
                                    {"api_id": SPORT_CMD[sport_cmd]}
                                )
                                print(f"  ✓ Command sent successfully")
                            except Exception as e:
                                print(f"  ✗ Command failed: {e}")
                            await asyncio.sleep(duration)
                            
                            # CRITICAL FIX: Re-activate movement mode after commands that disable it
                            # Commands like StandUp, Sit, Damp, etc. deactivate movement mode
                            if command != 'stop':  # Don't re-send StopMove after StopMove
                                print(f"  Re-activating movement mode after {command}...")
                                try:
                                    await robot_connection.datachannel.pub_sub.publish_request_new(
                                        RTC_TOPIC["SPORT_MOD"],
                                        {"api_id": SPORT_CMD["StopMove"]}
                                    )
                                    await asyncio.sleep(0.3)
                                    print(f"  ✓ Movement mode re-activated")
                                except Exception as e:
                                    print(f"  ⚠️  Failed to re-activate movement mode: {e}")
                        else:
                            print(f"  ⚠️  Unknown command: {command}")
                    
                    elif action == 'wait':
                        print(f"  Waiting {duration}s...")
                        end_time = time.time() + duration
                        while time.time() < end_time:
                            if sequence_abort:
                                break
                            await asyncio.sleep(0.1)
                        print(f"  ✓ Wait complete")
                    
                    else:
                        print(f"  ⚠️  Unknown action: {action}")
                
                if not sequence_abort:
                    print(f"\n{'='*60}")
                    print("✓ SEQUENCE COMPLETED SUCCESSFULLY")
                    print(f"{'='*60}\n")
                    
            except Exception as e:
                print(f"\n{'='*60}")
                print(f"✗ SEQUENCE EXECUTION ERROR: {e}")
                print(f"{'='*60}\n")
                import traceback
                traceback.print_exc()
                raise
            finally:
                sequence_running = False
                sequence_abort = False
                print("Sequence state reset\n")
        
        future = asyncio.run_coroutine_threadsafe(run_sequence(), asyncio_loop)
        
        return jsonify({
            'status': 'success',
            'message': 'Sequence started',
            'steps': len(sequence)
        })
    
    except Exception as e:
        sequence_running = False
        sequence_abort = False
        print(f"Sequence startup error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/sequence/stop', methods=['POST'])
def stop_sequence():
    """Stop currently running sequence"""
    global sequence_abort, sequence_running
    
    if not sequence_running:
        return jsonify({
            'status': 'info',
            'message': 'No sequence is currently running'
        })
    
    sequence_abort = True
    print("⛔ Sequence stop requested")
    
    return jsonify({
        'status': 'success',
        'message': 'Sequence stop signal sent'
    })

@app.route('/sequence/status')
def sequence_status():
    """Check if sequence is currently running"""
    return jsonify({
        'running': sequence_running,
        'abort_requested': sequence_abort
    })

def generate_video():
    """Generator for video streaming"""
    while True:
        if is_connected and not frame_queue.empty():
            try:
                frame = frame_queue.get(timeout=1)
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            except Exception as e:
                pass
        else:
            time.sleep(0.033)

@app.route('/video_feed')
def video_feed():
    return Response(generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("=" * 60)
    print("Unitree Go2 Web Interface - Enhanced with Joystick Control")
    print("=" * 60)
    print(f"Default Robot IP: {ROBOT_IP}")
    print("\n⚠️  IMPORTANT: Close the Unitree Go app before connecting!")
    print("\nFeatures:")
    print("  • Virtual joystick controls for movement")
    print("  • Movement sequence programming")
    print("  • Real-time video streaming")
    print("  • Basic command buttons")
    print("\nStarting web server...")
    print("Open your browser and go to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
