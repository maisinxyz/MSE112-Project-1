#!/usr/bin/python3
# test_todo1.py  —  Tests servo_init() in isolation
# Run from Project_1 folder:  python3 test_todo1.py

#sudo python3 todo1tesst.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.expanduser('~' + os.environ.get('SUDO_USER', '')), 'mse112-ws-student', 'MasterPi'))

import time
import HiwonderSDK.Board as Board

def servo_init():
    Board.setPWMServoPulse(1, 2000, 500)  # Base servo — center/straight ahead
    Board.setPWMServoPulse(2, 1800, 500)  # Shoulder — tilt forward and down
    Board.setPWMServoPulse(3, 800, 500)  # Elbow — fold arm down
    Board.setPWMServoPulse(4, 2000, 500)  # Wrist — neutral position
    Board.setPWMServoPulse(5, 2000, 500)  # End effector — neutral
    time.sleep(0.5)                       # Wait for servos to reach position

# ── Run the test ────────────────────────────────────────────────────────────
print("=" * 50)
print("TODO 1 TEST: servo_init()")
print("=" * 50)
print("\nStep 1/3  Moving arm to DEFAULT (all servos centred at 1500)...")
for servo_id in range(1, 6):
    Board.setPWMServoPulse(servo_id, 1500, 500)
time.sleep(2)
print("         ✔  Look at the arm now — this is the BEFORE position.\n")

input("         Press ENTER to call servo_init() and move to tracking position...")
print("\nStep 2/3  Calling servo_init()...")
servo_init()
print("         ✔  Look at the arm now — this is the AFTER position.")
print("         ✔  The camera should be pointing at the floor ~20-30 cm ahead.\n")

# ── Tuning guide ────────────────────────────────────────────────────────────
print("         If the arm is NOT in the right position, adjust these values:")
print("           Servo 2 (shoulder): try 1700, 1900, or 2000  (higher = more forward)")
print("           Servo 3 (elbow)   : try  800,  900, or 1100  (lower  = more folded down)\n")

input("         Press ENTER to run a sweep so you can compare positions...")

print("\nStep 3/3  Sweeping servo 2 (shoulder) so you can find the best angle:")
for pulse in [1500, 1600, 1700, 1800, 1900, 2000]:
    print(f"           Servo 2 = {pulse}")
    Board.setPWMServoPulse(2, pulse, 400)
    time.sleep(1.0)

print("\n         Returning to servo_init() values...")
servo_init()
print("\nTEST COMPLETE.")
print("Record the best servo 2 and servo 3 values and update servo_init() in main.py.\n")