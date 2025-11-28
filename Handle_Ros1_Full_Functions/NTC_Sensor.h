// #include "esp32-hal-gpio.h"
#include "utility_functions.h"

#ifndef NTC_H
#define NTC_H

class NTC {
  // private:

  public:
    int pin_temperature;
    float temperature_sensed;
    float resistor_ref;
    float voltage_ref = 5.5; // 3.3v from esp
    float smooth_factor = 0.5;
    //// set midian filter variables for temperature
    float resistor_previous = 10000; // 10k ohm around 25 celicious
    static constexpr int median_window = 3;
    float temperature_median_mat[median_window] = {resistor_previous, resistor_previous, resistor_previous};
    int median_mat_index = 0;

    //constructor
    NTC(int pin_temperature, float resistor_ref): // using an initilaizer because the names of the members of the class are the same of the variables.
      pin_temperature(pin_temperature),
      resistor_ref(resistor_ref)
    {
      pinMode(pin_temperature, INPUT);
    }
    
    void read_temperature() {
      // reading the analog values
      float signal_voltage = analogReadMilliVolts(pin_temperature);
      signal_voltage /= 1000;

      // calculating the NTC resistor depending on the voltage readings
      float resistor_temp = signal_voltage/(voltage_ref - signal_voltage)*resistor_ref;
      
      // adding the new values to the median matrix
      temperature_median_mat[median_mat_index] = resistor_temp;

      // calculating the resistor according to median filter for outlier values
      float resistor_filtered = calc_median_outlier_filter(temperature_median_mat[0], temperature_median_mat[1], temperature_median_mat[2]);

      // calculating the resistor according to exponatial filter (low pass filter)
      resistor_filtered = calc_exponatial_filter(resistor_filtered, resistor_previous, smooth_factor);
      
      // calculating the temperature from the resistor
      temperature_sensed = calc_sensed_temperature(resistor_filtered);

      // raping up the function
      resistor_previous = resistor_filtered;

      // rap the function
      median_mat_index = (median_mat_index+1)%median_window;
    }

    /// define ntc temperature-resistor function
    float calc_sensed_temperature(float resistor){
      //// set the temperature sensor charactaristics
      float sensor_resistor_ref = 10000; // 10 k at 25 deg celsius
      int cel2kelv = 273;
      float sensor_temperature_ref = 25 + cel2kelv;
      int beta = 3910; // got this value from plotting the data from the datasheet of NTC (in google sheet)

      float temperature = 1/(log(resistor/sensor_resistor_ref)/beta + 1/sensor_temperature_ref); // the formula of the temperature of NTC
      // float temperature = 1/(log(sensor_resistor_ref/sensor_resistor_ref)/beta + 1/sensor_temperature_ref); // the formula of the temperature of NTC
      return (temperature-cel2kelv);
    }
};

#endif