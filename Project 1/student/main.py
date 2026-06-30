#!/usr/bin/python3
# coding=utf8
import sys
import os
sys.path.insert(0,os.path.join(os.path.expanduser('~' + os.environ.get('SUDO_USER', '')), 'mse112-ws-student', 'MasterPi'))
import cv2
import time
import math
import signal
import Camera
import threading
import numpy as np
import yaml_handle
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Sonar as Sonar
import HiwonderSDK.Misc as Misc
import HiwonderSDK.Board as Board
import HiwonderSDK.mecanum as mecanum
from HiwonderSDK.PID import PID
import pandas as pd

# initialization
chassis = mecanum.MecanumChassis()
AK = ArmIK()
pitch_pid = PID(P=0.28, I=0.16, D=0.18)

HWSONAR = Sonar.Sonar()
distance = 0 

range_rgb = {
    'red': (0, 0, 255),
    'blue': (255, 0, 0),
    'green': (0, 255, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
}
img_centerx = 320
# Variable for distance obstacle avoidance
distance_data = []
stopMotor = False
Threshold = 25  # Set threshold for obstacle distance

# line tracking
roi = [ # [ROI, weight]
        (240, 280,  0, 640, 0.1), 
        (340, 380,  0, 640, 0.3), 
        (430, 460,  0, 640, 0.6)
       ]

roi_h1 = roi[0][0]
roi_h2 = roi[1][0] - roi[0][0]
roi_h3 = roi[2][0] - roi[1][0]

roi_h_list = [roi_h1, roi_h2, roi_h3]
size = (640, 480)

# Line patrol
if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

def servo_init():
    # Set the PWM of the Servos appropriately to position arm for line-tracking
    Board.setPWMServoPulse(1, 2000, 500)  # Base servo — center/straight ahead
    Board.setPWMServoPulse(2, 1000, 500)  # Shoulder — tilt forward and down
    Board.setPWMServoPulse(3, 300, 500)   # Elbow — fold arm down
    Board.setPWMServoPulse(4, 2000, 500)  # Wrist — neutral position
    Board.setPWMServoPulse(5, 2000, 500)  # End effector — neutral
    time.sleep(0.5)                       # Wait for servos to reach position

# Set the detection color
def setTargetColor(target_color):
    global __target_color

    print("COLOR", target_color)
    __target_color = target_color
    return (True, ())

lab_data = None

def load_config():
    global lab_data
    lab_data = yaml_handle.get_yaml_data(yaml_handle.lab_file_path)

# initial position
def initMove():
    servo_init()
    MotorStop()
    
line_centerx = -1

# Variable reset
def reset():
    global line_centerx
    global __target_color
    
    line_centerx = -1
    __target_color = ()
    
# app initialization call
def init():
    print("VisualPatrol Init")
    load_config()
    initMove()

__isRunning = False

# app starts playing method call
def start():
    reset()

    global __isRunning
    global stopMotor
    global forward
    global turn
    global obstacle
    obstacle = False
    turn = True
    forward = True
    stopMotor = True
    __isRunning = True

    print("Line tracker 1.1 Start")

# app stops playing method calls
def stop():
    global __isRunning
    __isRunning = False
    MotorStop()
    print("Line tracker 1.1 Stop")

# app exit gameplay call
def exit():
    global __isRunning
    __isRunning = False
    MotorStop()
    print("Line tracker 1.1 Exit")

def setBuzzer(timer):
    Board.setBuzzer(0)
    Board.setBuzzer(1)
    time.sleep(timer)
    Board.setBuzzer(0)

def MotorStop():
    Board.setMotor(1, 0) 
    Board.setMotor(2, 0)
    Board.setMotor(3, 0)
    Board.setMotor(4, 0)

#Close before processing
def Stop(signum, frame):
    global __isRunning
    
    __isRunning = False
    print('Closing...')
    MotorStop()  # Turn off all motors
    
# Find the contour with the largest area
def getAreaMaxContour(contours):
    contour_area_temp = 0
    contour_area_max = 0
    area_max_contour = None

    for c in contours:  
        contour_area_temp = math.fabs(cv2.contourArea(c))  
        if contour_area_temp > contour_area_max:
            contour_area_max = contour_area_temp
            if contour_area_temp >= 5:  
                area_max_contour = c

    return area_max_contour, contour_area_max  

def move():
    global line_centerx
    global obstacle

    while True:
        if __isRunning:
            if line_centerx != -1 and not obstacle:
                num = (img_centerx - line_centerx)
                if abs(num) <= 5:  
                    pitch_pid.SetPoint = num
                else:
                    pitch_pid.SetPoint = 0
                
                pitch_pid.update(num) 
                tmp = pitch_pid.output    
                tmp = 100 if tmp > 100 else tmp   
                tmp = -100 if tmp < -100 else tmp
                base_speed = Misc.map(tmp, -100, 100, -30, 30)
                #SPEED
                Board.setMotor(1, int(25 + base_speed))  
                Board.setMotor(2, int(25 + base_speed))  
                Board.setMotor(3, int(-25 + base_speed))  
                Board.setMotor(4, int(-25 + base_speed)) 
                
            else:
                MotorStop()

                if obstacle:
                    time.sleep(0.01)
                    print("Obstacle Detected! Starting evasion sequence.\n")
                    
                    # Full stop to kill forward momentum
                    MotorStop()
                    time.sleep(0.3) 
                    #OBSTACLE
                    # 1. Move RIGHT (Using your tested RIGHT_WHEELS values)
                    print("Moving RIGHT...")
                    Board.setMotor(1, 40)   # FL
                    Board.setMotor(2, -50)  # FR
                    Board.setMotor(3, -50)  # RL
                    Board.setMotor(4, 40)   # RR
                    time.sleep(0.8)         # TUNE THIS for ~8cm
                    
                    # CRITICAL FIX: Hard stop to kill sideways momentum so rollers settle
                    MotorStop()
                    time.sleep(0.3)         

                    # 2. Move FORWARD (Using your tested FORWARD_WHEELS values)
                    print("Moving FORWARD...")
                    Board.setMotor(1, 60)
                    Board.setMotor(2, 60)
                    Board.setMotor(3, - 60)
                    Board.setMotor(4, - 60)
                    time.sleep(1)         # TUNE THIS for ~5cm
                    
                    # CRITICAL FIX: Hard stop to kill forward momentum
                    MotorStop()
                    time.sleep(0.3)         

                    # 3. Move LEFT (Using your tested LEFT_WHEELS values)
                    print("Moving LEFT...")
                    Board.setMotor(1, -40)
                    Board.setMotor(2, 40)
                    Board.setMotor(3, 40)
                    Board.setMotor(4, -40)
                    time.sleep(1)         # TUNE THIS for ~8cm
                    
                    print("Evasion complete. Resuming tracking.\n")
                    MotorStop()
                    
                    # Reset the obstacle flag so it looks for the line again
                    obstacle = False
                    time.sleep(0.5)
            
            # CRITICAL FIX: Add a small delay to prevent I2C bus flooding
            time.sleep(0.01)
        else:
            time.sleep(0.01)
 
# Run child thread for movement
th = threading.Thread(target=move)
th.setDaemon(True)
th.start()

def line_tracking(img, __target_color):
    global line_centerx
    global lab_data

    # Camera line tracking
    img_copy = img.copy()
    img_h, img_w = img.shape[:2]
    
    if not __isRunning or __target_color == ():
        return img
     
    frame_resize = cv2.resize(img_copy, size, interpolation=cv2.INTER_NEAREST)
    frame_gb = cv2.GaussianBlur(frame_resize, (3, 3), 3)         
    centroid_x_sum = 0
    weight_sum = 0
    center_ = []
    n = 0

    # Split the image into three parts: upper, middle and lower.
    for r in roi:
        roi_h = roi_h_list[n]
        n += 1       
        blobs = frame_gb[r[0]:r[1], r[2]:r[3]]
        frame_lab = cv2.cvtColor(blobs, cv2.COLOR_BGR2LAB)  # Convert the image to LAB space
        dilated = None  

        # Look for our specified target colors in the lab data map
        for color_name in __target_color:
            if lab_data and color_name in lab_data:
                # apply mask using lab space color parameters, to only detect specified color
                frame_mask = cv2.inRange(
                    frame_lab,
                    (lab_data[color_name]['min'][0], lab_data[color_name]['min'][1], lab_data[color_name]['min'][2]),
                    (lab_data[color_name]['max'][0], lab_data[color_name]['max'][1], lab_data[color_name]['max'][2])
                )
                
                # Perform bitwise operations on the original image to smooth out noise
                eroded = cv2.erode(frame_mask, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))) # corrosion
                dilated = cv2.dilate(eroded, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
                break # Process the first matched color

        # Skip contour search for this ROI band if no target color was matched
        if dilated is None:
            continue

        cnts = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)[-2]  
        cnt_large, area = getAreaMaxContour(cnts)  
        
        if cnt_large is not None:  
            rect = cv2.minAreaRect(cnt_large)         
            box  = np.int0(cv2.boxPoints(rect))       
            for i in range(4):
                box[i, 1] = box[i, 1] + (n - 1)*roi_h + roi[0][0]
                box[i, 1] = int(Misc.map(box[i, 1], 0, size[1], 0, img_h))
            for i in range(4):                
                box[i, 0] = int(Misc.map(box[i, 0], 0, size[0], 0, img_w))

            cv2.drawContours(img, [box], -1, (0, 0, 255, 255), 2)  
        
            pt1_x, pt1_y = box[0, 0], box[0, 1]
            pt3_x, pt3_y = box[2, 0], box[2, 1]            
            center_x, center_y = (pt1_x + pt3_x) / 2, (pt1_y + pt3_y) / 2  
            cv2.circle(img, (int(center_x), int(center_y)), 5, (0, 0, 255), -1)
            center_.append([center_x, center_y])
            
            centroid_x_sum += center_x * r[4]
            weight_sum += r[4]

    if weight_sum != 0:
        line_centerx = int(centroid_x_sum / weight_sum)
        cv2.circle(img, (line_centerx, int(center_y)), 10, (0, 255, 255), -1)
    else:
        line_centerx = -1
        
    return img

def run(img, __target_color):
    global __isRunning
    global stopMotor
    global distance_data
    global obstacle
    global distance

    dist = HWSONAR.getDistance() / 10.0

    if __isRunning:
        distance_data.append(dist)
        if len(distance_data) > 5:
            distance_data.pop(0)

        distance = np.mean(distance_data)

        # CRITICAL FIX: Add 'and not obstacle' so it doesn't spam the stop command
        # while the robot is trying to execute the evasion maneuver.
        if 0 < distance < Threshold and not obstacle:   
            chassis.set_velocity(0, 0, 0)
            obstacle = True
        
        time.sleep(0.03)
        img = line_tracking(img, __target_color)

        return img

if __name__ == '__main__':
    
    # 1. Initialize robot hardware
    init()
    start()
    
    # 2. Setup safe exit handler
    signal.signal(signal.SIGINT, Stop)
    
    # 3. Initialize camera and target color
    cap = cv2.VideoCapture(0) 
    __target_color = ('green',)  
    
    # 4. Main Unified Loop
    while __isRunning:
        ret, img = cap.read()
        if ret:
            frame = img.copy()
            # 'Frame' contains the image with the tracking circles drawn on it
            Frame = run(frame, __target_color)  
            
            # Diagnostic Console Output
            print(f"Vision Center X: {line_centerx} | Target: {__target_color}")
            
            # --- LIVE CAMERA FEED START ---
            # Resize the frame so it doesn't take up your whole screen
            display_frame = cv2.resize(Frame, (480, 360))
            
            # Show the window
            cv2.imshow('MasterPi Vision - Press ESC to quit', display_frame)
            
            # Listen for the ESC key (ASCII 27) to cleanly exit
            key = cv2.waitKey(1)
            if key == 27:
                print("ESC pressed. Exiting...")
                break
            # --- LIVE CAMERA FEED END ---
            
        else:
            time.sleep(0.01)
            
    # Clean up the video window and camera when the loop ends
    cv2.destroyAllWindows()
    cap.release()
    Stop(signal.SIGINT, None) # Ensure motors stop when script exits
