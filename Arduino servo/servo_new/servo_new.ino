#include <Servo.h>    // Use Servo library, included with IDE

Servo servoProbe;        // Create Servo object to control the servo
Servo servoPump;
Servo servoFiber;

int incomingByte;      // a variable to read incoming serial data into
const int ledPin = 13; // the pin that the LED is attached to
const int pumpOff = 0;
const int pumpOn = 90;
const int probeOff = 0;
const int probeOn = 90;
const int fiberOff = 90;
const int fiberOn = 0;
void setup() {
  // initialize serial communication:
  Serial.begin(9600);

  servoProbe.attach(8);  // Servo is connected to digital pin 9
  servoPump.attach(7);
  servoFiber.attach(12);
  digitalWrite(ledPin, HIGH);
}

void loop() {
  // see if there's incoming serial data:
  if (Serial.available() > 0) {
    // read the oldest byte in the serial buffer:
    incomingByte = Serial.read();
    // Turn Pump and Probe off
    if (incomingByte == 'O') {
      servoProbe.write(probeOff);   // Turn servos to off position
      servoPump.write(pumpOff);
    }

    //turn probe on and
    if (incomingByte == 'P') {
      servoProbe.write(probeOn);   // Turn servos to on position
      servoPump.write(pumpOn);
    }

    if (incomingByte == 'U') {
      servoProbe.write(probeOff);   // pump only mode
      servoPump.write(pumpOn);
    }

    if (incomingByte == 'R') {
      servoProbe.write(probeOn);   // probe only mode
      servoPump.write(pumpOff);
    }
    if (incomingByte == 'K') {
      servoFiber.write(fiberOff);   // Fiber OFF
    }
    if (incomingByte == 'F') {
      servoFiber.write(fiberOn);   // Fiber OFF
    }
  }
}
