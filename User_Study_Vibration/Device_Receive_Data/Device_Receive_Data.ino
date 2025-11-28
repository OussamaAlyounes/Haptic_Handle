#include <ESP32Servo.h>

Servo servo1, servo2;
int vibro_pin1 = 18;
int vibro_pin2 = 19;
int vibro_pin3 = 7;
int vibro_pin4 = 6;


void setup() {
  // put your setup code here, to run once:
  pinMode(vibro_pin1, OUTPUT);
  pinMode(vibro_pin2, OUTPUT);
  pinMode(vibro_pin4, OUTPUT);
  pinMode(vibro_pin3, OUTPUT);

  servo1.attach(1);
  servo2.attach(2);
  
  servo1.write(30);
  servo2.write(30);
  
  Serial.begin(115200);
  Serial.setTimeout(10);
}

void loop() {
  // put your main code here, to run repeatedly:
    String reading = Serial.readString();
    // String reading = "fo,50";
    if (reading.length()>0){
      // get the coma position to split
      int comma_ind = reading.indexOf(",");
      String vibration = reading.substring(0, comma_ind);
      String angle_str = reading.substring(comma_ind+1);
      int angle = angle_str.toInt();
      
      // write the angle to the servos
      servo1.write(angle);
      servo2.write(angle);
      delay(500);

      // apply the vibration
      vibrate(vibration);
      // delay(100);
      // Serial.print(vibration);
      // Serial.println(angle);
      Serial.println("DONE!");
    }

}

void vibrate(String vibration){
  if(vibration == "lr") left_right(4);
  if(vibration == "ud") up_down(4);
  if(vibration == "ci") circular(2);

  // vibration_all_off
  digitalWrite(vibro_pin1, LOW);
  digitalWrite(vibro_pin2, LOW);
  digitalWrite(vibro_pin3, LOW);
  digitalWrite(vibro_pin4, LOW);
}

void up_down(int amount){
  for(int i = 0; i < amount; i ++){
    // Up Down
    digitalWrite(vibro_pin1, HIGH);
    digitalWrite(vibro_pin2, HIGH);
    digitalWrite(vibro_pin3, LOW);
    digitalWrite(vibro_pin4, LOW);
    delay(500);

    digitalWrite(vibro_pin1, LOW);
    digitalWrite(vibro_pin2, LOW);
    digitalWrite(vibro_pin3, HIGH);
    digitalWrite(vibro_pin4, HIGH);
    delay(500);
  }
}

void left_right(int amount){
  for(int i = 0; i < amount; i ++){
    // Left Right
    digitalWrite(vibro_pin1, LOW);
    digitalWrite(vibro_pin2, HIGH);
    digitalWrite(vibro_pin3, HIGH);
    digitalWrite(vibro_pin4, LOW);
    delay(500);

    digitalWrite(vibro_pin1, HIGH);
    digitalWrite(vibro_pin2, LOW);
    digitalWrite(vibro_pin3, LOW);
    digitalWrite(vibro_pin4, HIGH);
    delay(500);
  }
}

void circular(int amount) {
  for(int i = 0; i < amount; i ++){
      // Circular
    digitalWrite(vibro_pin1, HIGH);
    digitalWrite(vibro_pin2, LOW);
    digitalWrite(vibro_pin3, LOW);
    digitalWrite(vibro_pin4, LOW);
    delay(500);

    digitalWrite(vibro_pin1, LOW);
    digitalWrite(vibro_pin2, HIGH);
    digitalWrite(vibro_pin3, LOW);
    digitalWrite(vibro_pin4, LOW);
    delay(500);

    digitalWrite(vibro_pin1, LOW);
    digitalWrite(vibro_pin2, LOW);
    digitalWrite(vibro_pin3, HIGH);
    digitalWrite(vibro_pin4, LOW);
    delay(500);

    digitalWrite(vibro_pin1, LOW);
    digitalWrite(vibro_pin2, LOW);
    digitalWrite(vibro_pin3, LOW);
    digitalWrite(vibro_pin4, HIGH);
    delay(500);
  }
}
