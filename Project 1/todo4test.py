#!/usr/bin/python3
# test_todo4.py  —  Tests the sonar sensor and obstacle detection logic
# Run from Project_1 folder:  python3 test_todo4.py
#
# No robot movement in this test — it only reads the sonar and prints output.
# Wave your hand in front of the sonar to simulate an obstacle.

import sys
import os
sys.path.insert(0, os.path.join(os.path.expanduser('~' + os.environ.get('SUDO_USER', '')), 'mse112-ws-student', 'MasterPi'))

import time
import numpy as np
import HiwonderSDK.Sonar as Sonar
import HiwonderSDK.mecanum as mecanum

HWSONAR = Sonar.Sonar()
chassis = mecanum.MecanumChassis()

Threshold = 10   # Same value as main.py — adjust here to match your main.py

# ── Run the test ────────────────────────────────────────────────────────────
print("=" * 55)
print("TODO 4 TEST: Sonar obstacle detection")
print("=" * 55)
print(f"\nCurrent threshold: {Threshold} cm  (edit Threshold in this file to match main.py)")
print("Wave your hand in front of the sonar sensor to trigger detection.")
print("Press Ctrl+C to stop.\n")

obstacle      = False
distance_data = []
triggers      = 0

try:
    while True:
        # ── Exact logic from your run() function ──────────────────────────
        dist = HWSONAR.getDistance() / 10.0          # convert mm → cm

        distance_data.append(dist)
        if len(distance_data) > 5:
            distance_data.pop(0)
        distance = np.mean(distance_data)            # smoothed average

        # TODO 4 logic (using smoothed 'distance' — more reliable than raw 'dist')
        if 0 < distance < Threshold:
            if not obstacle:                         # only trigger once per event
                chassis.set_velocity(0, 0, 0)
                obstacle = True
                triggers += 1
                print(f"\n  ⚠️  OBSTACLE DETECTED!  dist={distance:.1f} cm  "
                      f"(threshold={Threshold} cm)  — motors stopped, flag=True  "
                      f"[trigger #{triggers}]")
        else:
            obstacle = False

        # Live readout
        bar_len   = int(min(distance, 100) / 2)     # scale to 50 chars
        bar_fill  = "█" * bar_len
        bar_empty = "░" * (50 - bar_len)
        flag_str  = "OBSTACLE" if obstacle else "clear   "
        print(f"  dist={distance:5.1f} cm  [{bar_fill}{bar_empty}]  flag={flag_str}", end="\r")

        time.sleep(0.1)

except KeyboardInterrupt:
    print(f"\n\nTEST COMPLETE.  Total obstacle triggers: {triggers}")
    print(f"\nNotes:")
    print(f"  • Your main.py uses raw 'dist' — consider changing to 'distance' for")
    print(f"    smoother detection (the averaged value is more reliable).")
    print(f"  • Your main.py has Threshold = 10 at the top — make sure TODO 4 uses")
    print(f"    that variable:  if 0 < distance < Threshold:")
    print(f"  • Adjust Threshold in main.py if detection fires too early or too late.\n")