import cv2
import mediapipe as mp
import numpy as np
import random
import tkinter as tk
from PIL import Image, ImageTk
import threading

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

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
        self.draw_game(image_rgb)
        if hand_results.multi_hand_landmarks:
            self.check_hand_collision(image_rgb, hand_results)
        self.update_apple()
        self.master.after(30, self.update)

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

    def check_hand_collision(self, frame, hand_results):
        for hand_landmarks in hand_results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
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
        self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    game = AppleCatchingGame(root)
    root.protocol("WM_DELETE_WINDOW", game.on_closing)
    root.mainloop()
