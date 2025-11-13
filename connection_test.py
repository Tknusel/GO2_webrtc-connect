#!/usr/bin/env python3
"""
Simple connection test for Unitree Go2
Use this to diagnose connection issues
"""

import asyncio
import sys
from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod

ROBOT_IP = "192.168.12.1"

async def test_connection():
    print("="*60)
    print("Unitree Go2 Connection Diagnostic Test")
    print("="*60)
    
    # Step 1: Network connectivity
    print("\n[1/5] Testing network connectivity...")
    import subprocess
    try:
        result = subprocess.run(['ping', '-c', '1', ROBOT_IP], 
                              capture_output=True, timeout=5)
        if result.returncode == 0:
            print(f"✓ Robot is reachable at {ROBOT_IP}")
        else:
            print(f"✗ Cannot ping robot at {ROBOT_IP}")
            print("  → Check WiFi connection")
            print("  → Ensure you're connected to robot's WiFi network")
            return False
    except Exception as e:
        print(f"✗ Ping test failed: {e}")
        return False
    
    # Step 2: Create connection object
    print("\n[2/5] Creating WebRTC connection object...")
    try:
        robot = Go2WebRTCConnection(
            WebRTCConnectionMethod.LocalSTA,
            ip=ROBOT_IP
        )
        print("✓ Connection object created")
    except Exception as e:
        print(f"✗ Failed to create connection: {e}")
        return False
    
    # Step 3: Attempt connection
    print("\n[3/5] Attempting WebRTC connection...")
    print("    (This may take 10-30 seconds...)")
    try:
        await asyncio.wait_for(robot.connect(), timeout=30)
        print("✓ WebRTC connection established!")
    except asyncio.TimeoutError:
        print("✗ Connection timeout after 30 seconds")
        print("  → Robot might be busy with another connection")
        print("  → Close Unitree Go app completely")
        print("  → Try rebooting the robot")
        return False
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print(f"  Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Check data channel
    print("\n[4/5] Waiting for data channel...")
    max_wait = 10
    for i in range(max_wait):
        if hasattr(robot, 'datachannel') and robot.datachannel:
            if hasattr(robot.datachannel, 'pub_sub'):
                print(f"✓ Data channel ready after {i}s")
                break
        await asyncio.sleep(1)
        if i < max_wait - 1:
            print(f"  Waiting... {i+1}s")
    else:
        print("✗ Data channel did not initialize")
        return False
    
    # Step 5: Test simple command
    print("\n[5/5] Testing command channel...")
    try:
        from go2_webrtc_driver.constants import RTC_TOPIC
        
        response = await robot.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["MOTION_SWITCHER"],
            {"api_id": 1001}  # Query motion mode
        )
        print(f"✓ Command response received!")
        print(f"  Response code: {response['data']['header']['status']['code']}")
        
        if response['data']['header']['status']['code'] == 0:
            print("\n" + "="*60)
            print("SUCCESS! Robot connection is working properly")
            print("="*60)
            return True
        else:
            print(f"\n⚠️  Received non-zero response code")
            return False
            
    except Exception as e:
        print(f"✗ Command test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n⚠️  IMPORTANT: Make sure:")
    print("  1. Robot is powered ON")
    print("  2. You're connected to robot's WiFi")
    print("  3. Unitree Go app is CLOSED")
    print()
    input("Press ENTER to start test...")
    
    try:
        result = asyncio.run(test_connection())
        
        if result:
            print("\n✓ All tests passed! Your web interface should work now.")
        else:
            print("\n✗ Connection test failed. See errors above.")
            print("\nCommon solutions:")
            print("  • Restart the robot (power cycle)")
            print("  • Force close Unitree Go app")
            print("  • Reconnect to robot's WiFi")
            print("  • Wait 2 minutes after robot boot")
            
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
