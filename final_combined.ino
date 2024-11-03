#include <Servo.h>

Servo thumbServo, indexServo, middleServo, ringServo, pinkyServo, wristServo;

void setup() {
  Serial.begin(9600);
  thumbServo.attach(2);    // Pin for thumb servo
  indexServo.attach(7);    // Pin for index finger servo
  middleServo.attach(4);   // Pin for middle finger servo
  ringServo.attach(5);     // Pin for ring finger servo
  pinkyServo.attach(3);    // Pin for pinky finger servo
  wristServo.attach(6);    // Pin for wrist servo

  // Start in closed position
  closeAllFingers();
  wristServo.write(90);    // Set wrist to neutral position
}

void loop() {
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');  // Read the incoming data until newline
    Serial.println(data);

    // Check for open or close commands
    if (data.equalsIgnoreCase("11")) {
      openAllFingers();
    } else if (data.equalsIgnoreCase("00")) {
      closeAllFingers();
    } else {
      // Handle angle data if any
      handleAngleData(data);
    }
  }
}

void openAllFingers() {
  thumbServo.write(0);     // Open thumb
  indexServo.write(180);   // Open index finger
  middleServo.write(180);  // Open middle finger
  ringServo.write(180);    // Open ring finger
  pinkyServo.write(180);   // Open pinky finger
  wristServo.write(90);    // Set wrist to neutral position
}

void closeAllFingers() {
  thumbServo.write(180);   // Close thumb
  indexServo.write(0);     // Close index finger
  middleServo.write(0);    // Close middle finger
  ringServo.write(0);      // Close ring finger
  pinkyServo.write(0);     // Close pinky finger
  wristServo.write(90);    // Set wrist to neutral position
}

void handleAngleData(String data) {
  int commaIndex[5];         // To store positions of commas
  int angles[6] = {0};       // Array to store angles including wrist angle

  // Extract angles from the received data
  for (int i = 0; i < 6; i++) {
    commaIndex[i] = data.indexOf(',', i == 0 ? 0 : commaIndex[i - 1] + 1);
    if (commaIndex[i] == -1) {
      angles[i] = data.substring(i == 0 ? 0 : commaIndex[i - 1] + 1).toInt();
      break;
    } else {
      angles[i] = data.substring(i == 0 ? 0 : commaIndex[i - 1] + 1, commaIndex[i]).toInt();
    }
  }

  // Move servos to the received angles
  thumbServo.write(180 - angles[0]);
  indexServo.write(angles[1]);
  middleServo.write(angles[2]);
  ringServo.write(angles[3]);
  pinkyServo.write(angles[4]);
  wristServo.write(angles[5]);  // Move wrist based on received wrist angle
}
