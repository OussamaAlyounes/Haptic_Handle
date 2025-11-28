#include "Peltier.h"
#include "NTC_Sensor.h"
#include "utility_functions.h"

// peltier 1
int peltier1_pin_in1 = 18;
int peltier1_pin_in2 = 19;
int peltier1_pin_temperature = 4;
// int peltier1_pin_fault = xxx;
// int peltier1_pin_current = xxx;
int peltier1_resistor_ref = 32450;
float peltier1_temperature_ref = 40;
Peltier peltier1(peltier1_pin_in1, peltier1_pin_in2, peltier1_pin_temperature, peltier1_resistor_ref);

// peltier 2
int peltier2_pin_in1 = 8;
int peltier2_pin_in2 = 9;
int peltier2_pin_temperature = 3;
// int peltier2_pin_fault = xxx;
// int peltier2_pin_current = xxx;
int peltier2_resistor_ref = 32300;
float peltier2_temperature_ref = 20;
Peltier peltier2(peltier2_pin_in1, peltier2_pin_in2, peltier2_pin_temperature, peltier2_resistor_ref);

// peltier 3
int peltier3_pin_in1 = 7;
int peltier3_pin_in2 = 10;
int peltier3_pin_temperature = 2;
// int peltier3_pin_fault = xxx;
// int peltier3_pin_current = xxx;
int peltier3_resistor_ref = 32160;
float peltier3_temperature_ref = 20;
Peltier peltier3(peltier3_pin_in1, peltier3_pin_in2, peltier3_pin_temperature, peltier3_resistor_ref);

// peltier 4
int peltier4_pin_in1 = 5;
int peltier4_pin_in2 = 6;
int peltier4_pin_temperature = 1;
// int peltier4_pin_fault = xxx;
// int peltier4_pin_current = xxx;
int peltier4_resistor_ref = 32530;
float peltier4_temperature_ref = 20;
Peltier peltier4(peltier4_pin_in1, peltier4_pin_in2, peltier4_pin_temperature, peltier4_resistor_ref);

// extra ntc sensor
int sensor_pin = 0;
int sensor_resistor_ref = 32190;
NTC ntc_hot(sensor_pin, sensor_resistor_ref);

// controller signal
int signal_control = 42;

// start of the of program for recording the data easily
float time_start = micros();
float time_step = micros();

// core parallel task
TaskHandle_t TaskPeltierControl;

void setup() {
  Serial.begin(115200);

  // read at least one time all the temperatures as the initial value of temperature_sense is 25
  peltier1.read_temperature();
  peltier2.read_temperature();
  peltier3.read_temperature();
  peltier4.read_temperature();
  ntc_hot.read_temperature();

  delay(1000);

  xTaskCreatePinnedToCore(
  controlPeltiers,   // Function to implement the task
  "Peltier Control", // Name of the task
  4096,              // Stack size
  NULL,              // Parameter to pass
  1,                 // Priority (1=low)
  &TaskPeltierControl, // Task handle
  0                  // Core 0
);
}

void loop() {
// put your main code here, to run repeatedly:
  
  // temperature_ref = Serial.read(); // read the new value from the serial

  // if(micros() - time_start > 5*1e6){
  //   hysteresis_controller(peltier1, peltier1_temperature_ref);
  //   hysteresis_controller(peltier2, peltier2_temperature_ref);
  //   // hysteresis_controller(peltier3, peltier3_temperature_ref);
  //   hysteresis_controller(peltier4, peltier4_temperature_ref);
  // }
  
  if (micros() - time_step > 2*1e5){ //0.2 sec
    // Serial.print(50); Serial.print(" ");
    // Serial.print(50); Serial.print(" ");
    // Serial.print(18); Serial.print(" ");

    Serial.print(peltier1.temperature_sensed); Serial.print(" ");
    Serial.print(peltier2.temperature_sensed); Serial.print(" ");
    Serial.print(peltier3.temperature_sensed); Serial.print(" ");
    Serial.print(peltier4.temperature_sensed); Serial.print(" ");

    Serial.print(ntc_hot.temperature_sensed); Serial.print(" ");

    // Serial.print(50); Serial.print(" ");
    // Serial.print(50); Serial.print(" ");

    Serial.println();
    time_step = micros();
  
    // end the loop
    delay(1);
  }
}

void controlPeltiers(void * parameter){
  while(1){
    if(micros() - time_start > 5*1e6){
      hysteresis_controller(peltier1, peltier1_temperature_ref);
      hysteresis_controller(peltier2, peltier2_temperature_ref);
      hysteresis_controller(peltier3, peltier3_temperature_ref);
      hysteresis_controller(peltier4, peltier4_temperature_ref);
      ntc_hot.read_temperature();
    }
    else {
      peltier1.read_temperature();
      peltier2.read_temperature();
      peltier3.read_temperature();
      peltier4.read_temperature();
      ntc_hot.read_temperature();
    }
  }
}

// the controller should provide the dutycycle and the direction of the current
// the direction is update to the peltier object and the dutycycle is being passed to the peltier function
void hysteresis_controller(Peltier& peltier, float temperature_ref){ 
  // update the temperature reading
  peltier.read_temperature();

  int direction = sign(temperature_ref - peltier.temperature_ambient);
  // set the controller parameters
  float temperature_boundry = 0.5;
  float temperature_ref_max = temperature_ref;// + direction*temperature_boundry;
  float temperature_ref_min = temperature_ref;// - direction*temperature_boundry;

  // sending the duty_cycle of the peltier itself which is either the full power operation or the off operation
  // for another controller we need to send the calculated dutycycle instead (or exactly 1-dutycycle to be compatible with the definition of pololu)
  if (peltier.temperature_sensed*direction > temperature_ref_max*direction) {
    peltier.send_to_controller(temperature_ref, peltier.duty_cycle_off);
    signal_control = 25;
  }
  else if (peltier.temperature_sensed*direction < temperature_ref_min*direction) {
    peltier.send_to_controller(temperature_ref, peltier.duty_cycle_on);
    signal_control = 42;
  }

  else return;
}









