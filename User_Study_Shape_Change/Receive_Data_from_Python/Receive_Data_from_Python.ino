#include <ESP32Servo.h>

Servo servo;

void setup() {
  // put your setup code here, to run once:
  servo.attach(1);
  servo.write(90);
  
  Serial.begin(9600);
  Serial.setTimeout(10);
}

void loop() {
  // put your main code here, to run repeatedly:
  // Serial.println("10.1");
  // if (Serial.available()>0){
    // int angle = Serial.parseInt();
    String value = Serial.readString();
    if (value.length()>0){
      int angle = value.toInt();
      servo.write(angle);
      // delay(100);
      Serial.println(angle);
    }
    // else Serial.println("No value was tetected");
    // Serial.println(value+" " + String(Serial.available()));
  // }
  

// }
}
