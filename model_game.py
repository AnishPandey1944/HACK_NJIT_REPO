import cv2
import mediapipe as mp
import numpy as np
import random

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
apple_pos = [random.randint(50, 250), 0]
apple_size = (40, 40)
score = 0
bucket_size = (100, 20)
bucket_pos = [640 - bucket_size[0] - 10, 230 - bucket_size[1] - 10]
is_caught = False

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    hand_results = hands.process(image_rgb)
    black_image = np.zeros(image.shape, dtype=np.uint8)

    if hand_results.multi_hand_landmarks:
        for hand_landmarks in hand_results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(black_image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            for landmark in hand_landmarks.landmark:
                landmark_x = int(landmark.x * image.shape[1])
                landmark_y = int(landmark.y * image.shape[0])

                if (apple_pos[0] < landmark_x < apple_pos[0] + apple_size[0] and 
                    apple_pos[1] < landmark_y < apple_pos[1] + apple_size[1]):
                    is_caught = True
                    apple_pos = [
                        int(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].x * image.shape[1]),
                        int(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y * image.shape[0])
                    ]
                    break

    if is_caught:
        apple_pos[0] = int(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].x * image.shape[1])
        apple_pos[1] = int(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y * image.shape[0])
        
        if (bucket_pos[0] < apple_pos[0] < bucket_pos[0] + bucket_size[0] and
            bucket_pos[1] < apple_pos[1] < bucket_pos[1] + bucket_size[1]):
            score += 1
            apple_pos = [random.randint(50, 250), 0]
            is_caught = False
            
    else:
        if apple_pos[1] < image.shape[0]:
            apple_pos[1] += 3
        else:
            apple_pos = [random.randint(50, 250), 0]

    cv2.rectangle(black_image, (apple_pos[0], apple_pos[1]), 
                  (apple_pos[0] + apple_size[0], apple_pos[1] + apple_size[1]), (0, 0, 255), -1)
    cv2.rectangle(black_image, (bucket_pos[0], bucket_pos[1]), 
                  (bucket_pos[0] + bucket_size[0], bucket_pos[1] + bucket_size[1]), (0, 255, 0), -1)

    cv2.putText(black_image, f'Score: {score}', (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow('Apple Catching Game', black_image)
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
