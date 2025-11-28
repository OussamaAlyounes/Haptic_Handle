#include <ESP32Servo.h>

Servo servo1, servo2;

void setup() {
  // put your setup code here, to run once:
  servo1.attach(1);
  servo2.attach(2);
  
  servo1.write(30);
  servo2.write(30);
  delay(1000);
  Serial.begin(11520);
  Serial.setTimeout(10);
}

void move_motors(int angle){
    servo1.write(angle);
    servo2.write(angle);
    delay(2000);
}

void loop() {
  // put your main code here, to run repeatedly:
  move_motors(70);
  move_motors(30);
// }
}