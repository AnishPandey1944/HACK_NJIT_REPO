import cv2
import mediapipe as mp
import time
import numpy as np
import serial

# Arduino Bluetooth setup
bluetooth_port = 'COM11'  
baud_rate = 9600
arduino = serial.Serial(bluetooth_port, baud_rate, timeout=1)

# MediaPipe hands and drawing setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Constants for landmarks and calibration
FINGER_TIP_LANDMARKS = [4, 8, 12, 16, 20]
WRIST_LANDMARK = 0

# Arrays to store distances for calibration
open_distances = np.zeros(5)
close_distances = np.zeros(5)

# Variables for wrist x-coordinate calibration
central_x_position = None
max_deviation = 0.2  # Adjust if needed based on observed hand movement range

# Calculate Euclidean distance between two landmarks
def calc_distance(landmark1, landmark2):
    return np.sqrt((landmark1.x - landmark2.x)**2 + (landmark1.y - landmark2.y)**2 + (landmark1.z - landmark2.z)**2)

# Calculate openness percentage
def calculate_openness(current_distances, open_distances, close_distances):
    return np.clip(100 * (current_distances - close_distances) / (open_distances - close_distances), 0, 100)

# Map openness percentage to servo angles
def openness_to_servo_angle(openness_percentage):
    return np.clip((openness_percentage / 100) * 180, 0, 180)

# Convert x deviation to wrist servo angle
def x_deviation_to_wrist_angle(x_position):
    deviation = (x_position - central_x_position) / max_deviation
    return np.clip(90 + (deviation * 90), 0, 180)

# Send angles to Arduino
def send_servo_angles(servo_angles, wrist_angle):
    data = ','.join([str(int(angle)) for angle in servo_angles] + [str(int(wrist_angle))]) + '\n'
    arduino.write(data.encode())

# Capture video
cap = cv2.VideoCapture(0)

# Calibration stages
stage = 'calibration_open'
start_time = time.time()
finger_names = ["Thumb", "Index", "Middle", "Ring", "Pinky"]

with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7) as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # Process image
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            wrist = hand_landmarks.landmark[WRIST_LANDMARK]
            current_distances = np.array([
                calc_distance(hand_landmarks.landmark[tip], wrist) for tip in FINGER_TIP_LANDMARKS
            ])

            # Calibration stages
            if stage == 'calibration_open':
                cv2.putText(image, "Open your palm! Calibrating 100% openness...", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                if time.time() - start_time > 5:
                    close_distances = current_distances
                    central_x_position = hand_landmarks.landmark[WRIST_LANDMARK].x  # Record central x-position
                    stage = 'calibration_close'
                    start_time = time.time()

            elif stage == 'calibration_close':
                cv2.putText(image, "Close your hand! Calibrating 0% openness...", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                if time.time() - start_time > 5:
                    open_distances = current_distances
                    stage = 'operational'

            elif stage == 'operational':
                # Calculate openness and convert to servo angles
                openness_percentage = calculate_openness(current_distances, open_distances, close_distances)
                servo_angles = openness_to_servo_angle(openness_percentage)

                # Calculate wrist angle based on x deviation
                current_x_position = hand_landmarks.landmark[WRIST_LANDMARK].x
                wrist_angle = x_deviation_to_wrist_angle(current_x_position)

                for i, finger_name in enumerate(finger_names):
                    text = f"{finger_name}: {int(openness_percentage[i])}% (Servo: {int(servo_angles[i])}°)"
                    cv2.putText(image, text, (10, 30 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                
                # Display wrist angle
                wrist_text = f"Wrist Angle: {int(wrist_angle)}°"
                cv2.putText(image, wrist_text, (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

                # Send servo angles including wrist angle to Arduino
                send_servo_angles(servo_angles, wrist_angle)

        # Display result
        cv2.imshow('Finger Openness Calibration with Wrist Control', image)

        if cv2.waitKey(5) & 0xFF == 27:
            break

# Clean up
cap.release()
cv2.destroyAllWindows()
arduino.close()
