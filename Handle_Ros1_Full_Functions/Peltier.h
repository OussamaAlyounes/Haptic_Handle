#include "WString.h"
#include <Arduino.h>
#include "utility_functions.h"
#include "NTC_Sensor.h"

#ifndef PELTIER_H
#define PELTIER_H

class Peltier {
  private:
    //// set pwm charactarestics pololu
    float pwm_frequency = 80000; // heating 70k is enough
    int pwm_resolution = 7;
    int pwm_range = pow(2, pwm_resolution) -1;
    
    //// set temperature sensor circuit parameters
    int analog_resolution = 12;
    
    //// set exponantial filter variables for current
    float current_previous = 1; // 1 amp to change later
    
    //// set midian filter variables for current
    static constexpr int median_window = 3;
    float current_median_mat[median_window] = {current_previous, current_previous, current_previous};
    int median_mat_index = 0;

  public:
    //// set pololu pins
    int pin_in1;
    int pin_in2;
    int pin_temperature;
    int pin_fault;
    int pin_current;
    float current = 0;
    float fault_not = 0;
    int pin_pwm;
    int pin_high;
    float resistor_ref; // 33k ohm measured

    //// current regulator parameter
    float voltage_supply = 5.5; // input voltage from the power supply
    float current_ref = current_previous; // 1000 mA
    float resistor_peltier = 1.9;
    float resistor_rlc1 = 0.1;
    float resistor_rlc2 = 0.1;
    static constexpr int current_mat_window = 25;
    float current_peltier_mat[current_mat_window];
    int current_mat_index = 0;

    //// setting the duty cycle parameters
    float D = current_ref*(resistor_peltier + resistor_rlc1 + resistor_rlc2)/voltage_supply;
    float duty_cycle_on = 1 - D; // 50% is enough for heating
    float duty_cycle_off = 1; // 50% is enough for heating
    // int direction = 1;
    // int direction_prev = 1;

    //// temperature of peltier
    float temperature_sensed;
    float temperature_ambient = 28;
    float temperature_ref = temperature_ambient;
    // String heat_operation = "HEAT";
    String heat_operation_prev = "COOL";
    NTC* ntc; // define a pointer to the object of NTC as we do not have the parameters needed to define a new object (pin, resistor)
    
    /// exponantial smooth factor
    float smooth_factor = 0.5;

    // constructor
    Peltier(int pin_in1, int pin_in2, int pin_temperature, float resistor_ref):// using an initilaizer because the names of the members of the class
    // are the same of the variables.
      // identify the pins and values for this specific sensor
      pin_in1(pin_in1),
      pin_in2(pin_in2),
      pin_temperature(pin_temperature),
      resistor_ref(resistor_ref)
      {
      }
    
    void begin(){
      // attach the ntc to the peltier
      ntc = new NTC(pin_temperature, resistor_ref);

      // set the output and input pins
      pinMode(pin_in1, OUTPUT);
      pinMode(pin_in2, OUTPUT);
      // pinMode(pin_fault, INPUT);
      // pinMode(pin_current, INPUT);

      // analog reading properties
      analogReadResolution(analog_resolution); // it sets and reads the values in 12 bits (not only reading)
      analogSetAttenuation(ADC_11db); // set the maximum input voltage to 2.778 v

      // read and update the sensor temperature several times at the beginning
      // delay(5);
      // int i = 0;
      // while(i < 5) {
      //   read_temperature(); 
      //   i++;
      // }

      // set the initial value of the current matrix
      for (int i = 0; i< current_mat_window; i++){
        current_peltier_mat[i] = current_ref;
      }

      // initiate PWM parameters
      set_controller_pins("HEAT");
    }

    void regulate_current(){
      float current = read_current()/1000;
      current_peltier_mat[current_mat_index] = current;
      float current_peltier = mean(current_peltier_mat, current_mat_window); // mean fun is needed as the current itself has a ripple of more that 0.1 amp which is a bit big
      resistor_peltier = voltage_supply*D/current_peltier - resistor_rlc1 - resistor_rlc2; // according to equation 1 from the calculations I made
      duty_cycle_on = 1 - current_ref*(resistor_peltier + resistor_rlc1 + resistor_rlc2)/voltage_supply; // according to equation 2 from the calculations I made
      
      current_mat_index = (current_mat_index+1)%current_mat_window;
    }

    float read_current(){
      current = analogReadMilliVolts(pin_current);
      current_median_mat[median_mat_index] = current;
      float current_filtered = calc_median_outlier_filter(current_median_mat[0], current_median_mat[1], current_median_mat[2]);
      current_filtered = calc_exponatial_filter(current_filtered, current_previous, smooth_factor);

      current_filtered /= 1.1;
      current_previous = current_filtered;

      //rapping the function
      median_mat_index = (median_mat_index+1)%median_window;
      return current_filtered; // as the voltage is 1.1*current according to the datasheet
      }

    void read_temperature(){
      ntc->read_temperature();
      this->temperature_sensed = ntc->temperature_sensed;
    }

    void set_controller_pins(String heat_operation){
      // the direction of current should change only if the heat_operation was changed from the previous one.
      // this is important so that we do not detach the pins from the PWM everytime and attach them again. It causes
      // unnecessary delay. If the operation is the same of the previous one, then the pins configuration stays the same
      if (heat_operation != heat_operation_prev){
        // reinitialize the controller pins
        ledcDetach(pin_pwm);
        pinMode(pin_pwm, OUTPUT);

        // shorten the two terminals of the load to L-L to allow the inductance of the load to dissipate its energy.
        digitalWrite(pin_high, HIGH);
        digitalWrite(pin_pwm, HIGH);
        
        /* add a small delay to prevent the transistors of the H-Bridge from burning due to any overcurrent,
          since the Peltier is generating an electric voltage due to the Seebeck effect so there is a small current
          that is passing in the opposite direction of the current that caused the differnce in temperature. 
          The inductance of the Peltier is too small to generate a current for a long time (Let's say L= 10 uH).
          We still have the inductance of the buck driver 120 uh. the total resistor R = 2.42 ohms (0.12 ohm for each
          Rdson of the transistors + 2 ohm of the Peltier + 0.15 of the inductance).
          so tau = L/R = 48 usec and the delay should be 5*tau = 240 usec during which the output is a closed-loop to L-L.
        */
        delayMicroseconds(240);
        
        //set the new output pins depending on the command, heat or cool
        if (heat_operation == "HEAT"){ // heating
          pin_pwm = pin_in1;
          pin_high = pin_in2;
        }
        else if (heat_operation == "COOL"){ // cooling
          pin_pwm = pin_in2;
          pin_high = pin_in1;
        }
        // else if (heat_operation == "NEUTRAL") no change on the pins will hapen
        // initiate PWM parameters
        ledcAttach(pin_pwm, pwm_frequency, pwm_resolution);
        // change the last operation value
        heat_operation_prev = heat_operation;
      }
    }

    void send_to_controller(float duty_cycle){
      // update the temperature reading
      // read_temperature();

      // ACTIVE BRAKING: check which direction we should be going as an initial step
      // if(abs(temperature_ref - temperature_sensed) > 3) {
      //   if(temperature_ref > temperature_sensed) set_controller_pins("HEAT");
      //   else set_controller_pins("COOL");
      // // start the PWM for active breaking (full duty cycle) till we reach the required temperature
      //   digitalWrite(pin_high, HIGH); // set the direction of the current according to the sign of the direction
      //   ledcWrite(pin_pwm, int(duty_cycle_on*pwm_range));
      // }
      // if(((temperature_ref < temperature_sensed) && (temperature_ref > temperature_ambient)) ||
      //    ((temperature_ref > temperature_sensed) && (temperature_ref < temperature_ambient))) {
      //   if(temperature_ref > temperature_sensed) set_controller_pins("HEAT");
      //   else set_controller_pins("COOL");
      // // start the PWM for active breaking (full duty cycle) till we reach the required temperature
      //   digitalWrite(pin_high, HIGH); // set the direction of the current according to the sign of the direction
      //   ledcWrite(pin_pwm, int(duty_cycle_on*pwm_range));
      // }
      // NORMAL OPERATION: if the target was reached, we activate the controller based on the reference and ambient temperatures
      // else if(abs(temperature_ref - temperature_sensed) <= 1){
      // else {
        /*
         whether the temp_ref == temp_ambient or not, it will not affect much as it is only assigning the pins pin_high
         and pin_pwm differently but the duty_cycle was sent already as duty_cycle_off so the controller wil be L-L
        */
        if(temperature_ref > temperature_ambient) set_controller_pins("HEAT");
        else set_controller_pins("COOL");
        
        // start the PWM with the duty cycle
        digitalWrite(pin_high, HIGH); // set the direction of the current according to the sign of the direction
        ledcWrite(pin_pwm, int(duty_cycle*pwm_range));

      // }
    }
};

#endif PELTIER_H