#include "esp32-hal-gpio.h"
#include <ESP32Servo.h>
#include <math.h>

#ifndef SERVOS_H
#define SERVOS_H
// #define pi 3.14159265

class Servos{
  public:
    // pinion parameter
    float distance_max = 6.0; // 6 mm
    float gear_diameter = 13.0; // 13 mm
    float angle = 0.0;
    float angle_offset = 30.0; // 30 deg offset not to be close to the 0 deg (limit of the servo)
    int servo_pin1, servo_pin2;
    Servo *servo1, *servo2;

  Servos(int servo_pin1, int servo_pin2):
  servo_pin1(servo_pin1), servo_pin2(servo_pin2)
  {
    
  }

  void begin(){
    servo1 = new Servo();
    servo2 = new Servo();
    pinMode(servo_pin1, OUTPUT);
    pinMode(servo_pin2, OUTPUT);
    servo1->attach(servo_pin1);
    servo2->attach(servo_pin2);
  }

  void set_position(float distance){
    if(distance > distance_max) distance = distance_max;
    else if(distance < 0) distance = 0;
    angle = distance/(gear_diameter/2); // in rad
    angle = angle*(180.0/M_PI);// transform to degrees
    servo1->write(angle + angle_offset);
    servo2->write(angle + angle_offset);
    // servo1.write(angle_offset);
    // servo2.write(angle_offset);
  }
  
};

#endif