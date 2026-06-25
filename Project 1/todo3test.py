#!/usr/bin/python3
# test_todo3.py  —  Tests the obstacle avoidance movement sequence in isolation
# Run from Project_1 folder:  python3 test_todo3.py
#
# ⚠️  WARNING: The robot WILL move through a full avoidance sequence.
#     Clear a space of at least 1 m wide × 1.5 m long before running.

import sys
import os
sys.path.insert(0, os.path.join(os.path.expanduser('~' + os.environ.get('SUDO_USER', '')), 'mse112-ws-student', 'MasterPi'))

import time
import HiwonderSDK.mecanum as mecanum

chassis = mecanum.MecanumChassis()

# ── Run the test ────────────────────────────────────────────────────────────
print("=" * 55)
print("TODO 3 TEST: Obstacle avoidance movement sequence")
print("=" * 55)
print("\nThis runs: stop → left → forward → right → stop")
print("Clear at least 1 m × 1.5 m of space.\n")
input("Press ENTER to begin the sequence...\n")

print("STOP (pre-sequence)...")
chassis.set_velocity(0, 0, 0)
time.sleep(0.5)

print("Step 1/3: Moving LEFT  (direction=90°, speed=50, 1.5 s)...")
chassis.set_velocity(50, 90, 0)
time.sleep(1.5)
print("          ✔  Robot should have moved to the LEFT.\n")

print("Step 2/3: Moving FORWARD  (direction=0°, speed=50, 1.5 s)...")
chassis.set_velocity(50, 0, 0)
time.sleep(1.5)
print("          ✔  Robot should have moved FORWARD.\n")

print("Step 3/3: Moving RIGHT  (direction=270°, speed=50, 1.5 s)...")
chassis.set_velocity(50, 270, 0)
time.sleep(1.5)
print("          ✔  Robot should have moved to the RIGHT.\n")

print("STOP.")
chassis.set_velocity(0, 0, 0)

print("\nTEST COMPLETE.\n")
print("── If directions are wrong, try swapping the angles: ──────────────────")
print("   Left  → change  90  to  270")
print("   Right → change  270 to   90")
print("\n── If the robot doesn't clear the obstacle in the demo: ────────────────")
print("   Increase time.sleep(1.5) to time.sleep(2.0) or time.sleep(2.5)")
print("   in main.py TODO 3.\n")