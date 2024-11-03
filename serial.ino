#include <Servo.h>

// Define individual servos
Servo thumbServo;
Servo indexServo;
Servo middleServo;
Servo ringServo;
Servo pinkyServo;
Servo wristServo;

// Pin assignments for each servo (customized)
const int thumbPin = 2;   // Pin for thumb servo
const int indexPin = 3;   // Pin for index finger servo
const int middlePin = 4;  // Pin for middle finger servo
const int ringPin = 5;    // Pin for ring finger servo
const int pinkyPin = 7;   // Pin for pinky finger servo
const int wristPin = 6;   // Pin for wrist servo

void setup() {
  Serial.begin(9600);
  
  // Attach each servo to its corresponding pin
  thumbServo.attach(thumbPin);
  indexServo.attach(indexPin);
  middleServo.attach(middlePin);
  ringServo.attach(ringPin);
  pinkyServo.attach(pinkyPin);
  wristServo.attach(wristPin);
  
  closeAllFingers(); // Start in closed position
}

void loop() {
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n'); // Read the incoming data until newline
    Serial.println(data);
    
    // Check for open or close commands
    if (data.equalsIgnoreCase("11")) {
      closeHand(); // Open the hand
      delay(300);
      movebaseservo();
      delay(300);
      openHand();
      delay(300);
      closeHand();
      delay(300);
      movebaseservoop();
      delay(300);// Close the hand
      openHand(); 
      delay(300);// Return to original position
    } else if (data.equalsIgnoreCase("00")) {
      closeAllFingers(); // Close all fingers
      wristServo.write(0); // Move wrist to closed position
      delay(500); // Allow time for the wrist to reach its position
    }
  }
}

// Function to open the hand
void openHand() {
  thumbServo.write(0);   // Open thumb
  indexServo.write(180); // Open index finger
  middleServo.write(180); // Open middle finger
  ringServo.write(180);   // Open ring finger
  pinkyServo.write(180);  // Open pinky finger   // Adjust wrist position if needed
  delay(500); // Allow time for the servos to reach their positions
}

// Function to close the hand
void closeHand() {
  thumbServo.write(180);  // Close thumb
  indexServo.write(0);    // Close index finger
  middleServo.write(0);   // Close middle finger
  ringServo.write(0);     // Close ring finger
  pinkyServo.write(0);    // Close pinky finger
  wristServo.write(0);    // Move wrist to closed position
  delay(500); // Allow time for the servos to reach their positions
}

// Function to return to the original position
void returnToOriginal() {
  thumbServo.write(90);   // Move thumb to original position
  indexServo.write(90);   // Move index finger to original position
  middleServo.write(90);  // Move middle finger to original position
  ringServo.write(90);    // Move ring finger to original position
  pinkyServo.write(90);   // Move pinky finger to original position
  wristServo.write(180);    // Move wrist to original position
  delay(500); // Allow time for the servos to reach their positions
}

// Function to close all fingers
void closeAllFingers() {
  thumbServo.write(180);  // Close thumb
  indexServo.write(0);    // Close index finger
  middleServo.write(0);   // Close middle finger
  ringServo.write(0);     // Close ring finger
  pinkyServo.write(0);    // Close pinky finger
 ;    // Move wrist to closed position
  delay(500); // Allow time for the servos to reach their positions
}
void movebaseservo() {
  wristServo.write(180);  // Open pinky finger   // Adjust wrist position if needed
  delay(500); // Allow time for the servos to reach their positions
}
void movebaseservoop() {
  wristServo.write(180);  // Open pinky finger   // Adjust wrist position if needed
  delay(500); // Allow time for the servos to reach their positions
}
