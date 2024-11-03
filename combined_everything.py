import cv2
import mediapipe as mp
import numpy as np
import random
import serial
import tkinter as tk
from PIL import Image, ImageTk
import threading
import time

# Bluetooth setup for servo control
bluetooth_port = 'COM11'
baud_rate = 9600
arduino = serial.Serial(bluetooth_port, baud_rate, timeout=1)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Constants for hand tracking
FINGER_TIP_LANDMARKS = [4, 8, 12, 16, 20]
WRIST_LANDMARK = 0

open_distances = np.zeros(5)
close_distances = np.zeros(5)
initial_wrist_x = None  # Store initial wrist x-coordinate for lateral movement calibration

# Apple Catching Game Class
class AppleCatchingGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Apple Catching Game")
        self.canvas = tk.Canvas(master, width=640, height=480)
        self.canvas.pack()
        self.apple_image = Image.open("apple.png").resize((60, 60))
        self.bucket_image = Image.open("bucket.png").resize((150, 30))
        self.apple_pos = [random.randint(50, 580), 0]
        self.bucket_pos = [245, 450]
        self.score = 0
        self.is_caught = False
        self.cap = cv2.VideoCapture(0)
        self.frame = None
        self.thread = threading.Thread(target=self.video_capture)
        self.thread.daemon = True
        self.thread.start()
        self.update()
        self.stage = 'calibration_open'
        self.start_time = time.time()

    def video_capture(self):
        while True:
            success, image = self.cap.read()
            if success:
                self.frame = image

    def update(self):
        if self.frame is None:
            self.master.after(30, self.update)
            return

        image_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        hand_results = hands.process(image_rgb)

        # Hand openness calibration and control
        self.handle_hand_openness(hand_results)

        # Draw the game visuals
        self.draw_game(image_rgb)

        if hand_results.multi_hand_landmarks:
            self.check_hand_collision(hand_results)

        self.update_apple()
        self.master.after(30, self.update)

    def handle_hand_openness(self, hand_results):
        global initial_wrist_x

        if hand_results.multi_hand_landmarks:
            hand_landmarks = hand_results.multi_hand_landmarks[0]
            wrist = hand_landmarks.landmark[WRIST_LANDMARK]
            current_distances = np.array([self.calc_distance(hand_landmarks.landmark[tip], wrist) for tip in FINGER_TIP_LANDMARKS])

            # Store initial wrist x-coordinate for lateral movement
            if initial_wrist_x is None:
                initial_wrist_x = wrist.x

            if self.stage == 'calibration_open':
                if time.time() - self.start_time > 5:
                    close_distances[:] = current_distances
                    self.stage = 'calibration_close'
                    self.start_time = time.time()

            elif self.stage == 'calibration_close':
                if time.time() - self.start_time > 5:
                    open_distances[:] = current_distances
                    self.stage = 'operational'

            elif self.stage == 'operational':
                openness_percentage = self.calculate_openness(current_distances)
                servo_angles = self.openness_to_servo_angle(openness_percentage)
                self.send_servo_angles(servo_angles, wrist.x)

    def calc_distance(self, landmark1, landmark2):
        return np.sqrt((landmark1.x - landmark2.x) ** 2 + (landmark1.y - landmark2.y) ** 2 + (landmark1.z - landmark2.z) ** 2)

    def calculate_openness(self, current_distances):
        return np.clip(100 * (current_distances - close_distances) / (open_distances - close_distances), 0, 100)

    def openness_to_servo_angle(self, openness_percentage):
        return np.clip((openness_percentage / 100) * 180, 0, 180)

    def send_servo_angles(self, servo_angles, current_wrist_x):
        # Calculate wrist servo angle based on lateral movement
        wrist_movement = (current_wrist_x - initial_wrist_x) * 500  # Scale factor for x-movement
        wrist_servo_angle = np.clip(90 + wrist_movement, 0, 180)  # Base wrist servo angle at 90 degrees
        
        # Prepare data to send to Arduino
        data = ','.join([str(int(angle)) for angle in servo_angles]) + f',{int(wrist_servo_angle)}\n'
        arduino.write(data.encode())

    def draw_game(self, frame):
        frame_image = Image.fromarray(frame)
        self.tk_image = ImageTk.PhotoImage(frame_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        apple_tk_image = ImageTk.PhotoImage(self.apple_image)
        self.canvas.create_image(self.apple_pos[0], self.apple_pos[1], anchor=tk.NW, image=apple_tk_image)
        self.canvas.image_apple = apple_tk_image
        bucket_tk_image = ImageTk.PhotoImage(self.bucket_image)
        self.canvas.create_image(self.bucket_pos[0], self.bucket_pos[1], anchor=tk.NW, image=bucket_tk_image)
        self.canvas.image_bucket = bucket_tk_image
        self.canvas.create_text(10, 10, text=f'Score: {self.score}', fill="white", anchor=tk.NW)

    def check_hand_collision(self, hand_results):
        for hand_landmarks in hand_results.multi_hand_landmarks:
            for landmark in hand_landmarks.landmark:
                landmark_x = int(landmark.x * 640)
                landmark_y = int(landmark.y * 480)
                if (self.apple_pos[0] < landmark_x < self.apple_pos[0] + 60 and
                        self.apple_pos[1] < landmark_y < self.apple_pos[1] + 60):
                    self.apple_pos[0] = landmark_x - 30
                    self.apple_pos[1] = landmark_y - 30
                    self.is_caught = True
                    break

    def update_apple(self):
        if self.is_caught:
            if (self.bucket_pos[0] < self.apple_pos[0] < self.bucket_pos[0] + 150 and
                    self.apple_pos[1] + 60 >= self.bucket_pos[1]):
                self.score += 1
                self.apple_pos = [random.randint(50, 580), 0]
                self.is_caught = False
            else:
                self.apple_pos[1] += 3
        else:
            if self.apple_pos[1] < 480:
                self.apple_pos[1] += 3
            else:
                self.apple_pos = [random.randint(50, 580), 0]

    def on_closing(self):
        self.cap.release()
        arduino.close()
        self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    game = AppleCatchingGame(root)
    root.protocol("WM_DELETE_WINDOW", game.on_closing)
    root.mainloop()
