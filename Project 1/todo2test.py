#!/usr/bin/python3
# test_todo2.py  —  Tests TODO 2 motor speed logic in isolation
# Run from Project_1 folder:  python3 test_todo2.py
#
# ⚠️  WARNING: The robot WILL move. Either:
#     (a) Elevate the robot so the wheels spin freely in the air, OR
#     (b) Place it on the floor in a clear 1 m² open space.

#sudo python3 todo2test.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.expanduser('~' + os.environ.get('SUDO_USER', '')), 'mse112-ws-student', 'MasterPi'))

import time
import HiwonderSDK.Board as Board
import HiwonderSDK.Misc as Misc

def set_motors(speed1, speed2, speed3, speed4):
    """Exact copy of your TODO 2 code."""
    Board.setMotor(1, int(-50 + speed1))  # Rear Right (in perspective of the ultrasonic sensor.)
    Board.setMotor(2, int(50 + speed2))  # Front Right
    Board.setMotor(3, int(50 + speed3))  # Front left
    Board.setMotor(4, int(-50 + speed4))  # Rear left

def stop_motors():
    Board.setMotor(1, 0)
    Board.setMotor(2, 0)
    Board.setMotor(3, 0)
    Board.setMotor(4, 0)

# ── Run the test ────────────────────────────────────────────────────────────
print("=" * 55)
print("TODO 2 TEST: Motor speed control (PID differential)")
print("=" * 55)
print("\n⚠️  Make sure the robot is elevated OR in open space!\n")
input("Press ENTER to start the test sequence...\n")

# Test 1: Straight forward (base_speed = 0)
print("Test 1/3: base_speed =  0  →  all motors at speed 50 → STRAIGHT FORWARD")
print(f"          Motor 1={50+0}, Motor 2={50-0}, Motor 3={50+0}, Motor 4={50-0}")
set_motors(0, 0, 0 ,0)
time.sleep(2)
stop_motors()
print("          ✔  Robot should have moved STRAIGHT FORWARD.\n")
time.sleep(0.5)

# Test 2: Turn right (base_speed > 0)
print("Test 2/3: base_speed = +20  →  left motors faster → STEER RIGHT")
print(f"          Motor 1={50+20}, Motor 2={50-20}, Motor 3={50+20}, Motor 4={50-20}")
set_motors(100, -50, 0, 50)
time.sleep(2)
stop_motors()
print("          ✔  Robot should have curved to the RIGHT.\n")
print("          ✗  If it curved LEFT instead, swap + and - in main.py TODO 2:\n")
print("               Board.setMotor(1, int(50 - base_speed))")
print("               Board.setMotor(2, int(50 + base_speed))")
print("               Board.setMotor(3, int(50 - base_speed))")
print("               Board.setMotor(4, int(50 + base_speed))\n")
time.sleep(0.5)

# Test 3: Turn left (base_speed < 0)
print("Test 3/3: base_speed = -20  →  right motors faster → STEER LEFT")
print(f"          Motor 1={50-20}, Motor 2={50+20}, Motor 3={50-20}, Motor 4={50+20}")
set_motors(50, 0, -50, 100)
time.sleep(2)
stop_motors()
print("          ✔  Robot should have curved to the LEFT.\n")

print("TEST COMPLETE.")
print("If directions are correct, TODO 2 is working.\n")