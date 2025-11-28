//// define a sign function
int sign(float x) {
  return (x > 0) - (x < 0);
}

//// define a mean function
float mean(float values[], int numValues) {
  float sum = 0.0;
  for (int i = 0; i < numValues; i++) {
    sum += values[i];
  }
  return sum / numValues;
}

//// set pololu pins
int pin_in1 = 18;
int pin_in2 = 19;
// int pin_fault = 5;
// int pin_current = 4;
float current = 0;
float fault_not = 0;
int pin_pwm = 0;

//// set pwm charactarestics pololu
float pwm_frequency = 80000; // heating 70k is eough
int pwm_resolution = 8;
int pwm_range = pow(2, pwm_resolution) -1;

//// set temperature sensor pins
int temperature_pin1 = 4;
int temperature_pin2 = 0;

//// set temperature sensor circuit parameters
float voltage_ref = 5.5; // 3.3v from esp
float resistor_ref1 = 32450; // 33k ohm measured
float resistor_ref2 = 32190; // 33k ohm measured
int analog_resolution = 12;

//// set exponantial filter variables
float smooth_factor = 0.55;
// ..... for temperature
float resistor_previous1 = 10000; // 10k ohm around 25 celicious
float resistor_previous2 = 10000; // 10k ohm around 25 celicious
// ..... for current
float current_previous = 1; // 1 amp to change later

//// set midian filter variables
#define median_window 3
// ..... for temperature
float temperature_median_mat1[median_window] = {resistor_previous1, resistor_previous1, resistor_previous1};
float temperature_median_mat2[median_window] = {resistor_previous2, resistor_previous2, resistor_previous2};
// ..... for current
float current_median_mat[median_window] = {current_previous, current_previous, current_previous};
int median_mat_index = 0;

//// set the temperature sensor charactaristics
float resistor_ref = 10000; // 10 k at 25 deg celsius
int cel2kelv = 273;
float temperature_ref = 25 + cel2kelv;
int beta = 3910; // got this value from plotting the data from the datasheet of NTC (in google sheet)
float temperature_sensed_first = 23;
float temperature_sensed_second = 23;

//// set the controller parameters
int temperature_reference = 40; //42 and 15.... 35 and 20
float temperature_boundry = 0.2;
int temperature_ambient = 25;
int direction = sign(temperature_reference - temperature_ambient);
float temperature_reference_max = temperature_reference;// + direction*temperature_boundry;
float temperature_reference_min = temperature_reference;// - direction*temperature_boundry;

//// current regulator parameter
float voltage_supply = 5.5; // input voltage from the power supply
float current_ref = current_previous; // 1000 mA
float resistor_peltier = 1.8;
float resistor_rlc1 = 0.1;
float resistor_rlc2 = 0.1;
#define current_mat_window 25
float current_peltier_mat[current_mat_window];
int current_mat_index = 0;

//// setting the duty cycle parameters
// float duty_cycle_on = 1 - 0.28; // 50% is enough for heating
float D = current_ref*(resistor_peltier + resistor_rlc1 + resistor_rlc2)/voltage_supply;
float duty_cycle_on = 1 - D; // 50% is enough for heating
float duty_cycle_off = 1; // 50% is enough for heating
float duty_cycle = duty_cycle_on; // 5%
bool flag_flipped = false;
float time_stamp = micros();

void setup() {
  // set the output and input pins
  pinMode(pin_in1, OUTPUT);
  pinMode(pin_in2, OUTPUT);
  // pinMode(pin_fault, INPUT);
  // pinMode(pin_current, INPUT);

  // analog reading properties
  analogReadResolution(analog_resolution); // it sets and reads the values in 12 bits (not only reading)
  analogSetAttenuation(ADC_11db); // set the maximum input voltage to 2.778 v

  // set the initial value of the current matrix
  for (int i = 0; i<current_mat_window; i++){
    current_peltier_mat[i] = current_ref;
  }
  
  // set initial values of the in1/in2
  if(direction < 0) { // cooling
    digitalWrite(pin_in1, HIGH); // set the direction of the current according to the sign of the direction
    ledcAttach(pin_in2, pwm_frequency, pwm_resolution);
    pin_pwm = pin_in2;
  }
  else{ // heating
    digitalWrite(pin_in2, HIGH); // set the direction of the current according to the sign of the direction
    ledcAttach(pin_in1, pwm_frequency, pwm_resolution);
    pin_pwm = pin_in1;
    }

  // start serial
  Serial.begin(115200);
}

void loop() {
// put your main code here, to run repeatedly:
  // set initial values of the in1/in2
  // Serial.print(micros() - time_stamp);
  // Serial.print(" ");
  // time_stamp = micros();

  // if(micros() - time_stamp > 10*1e6 && flag_flipped == false){
  //   temperature_reference = 20;
  //   direction = sign(temperature_reference - temperature_ambient);
  //   temperature_reference_max = temperature_reference + direction*temperature_boundry;
  //   temperature_reference_min = temperature_reference - direction*temperature_boundry;
  
  //   if(direction < 0) { // cooling
  //   ledcDetach(pin_pwm);
  //   pinMode(pin_in2, OUTPUT);
  //   digitalWrite(pin_in2, HIGH); // set the direction of the current according to the sign of the direction
  //   ledcAttach(pin_in1, pwm_frequency, pwm_resolution);
  //   pin_pwm = pin_in1;
  //   }
  //   else{ // heating
  //   ledcDetach(pin_pwm);
  //   pinMode(pin_in1, OUTPUT);
  //   digitalWrite(pin_in1, HIGH); // set the direction of the current according to the sign of the direction
  //   ledcAttach(pin_in2, pwm_frequency, pwm_resolution);
  //   pin_pwm = pin_in2;
  //   }

  //   flag_flipped = true;
  // }

  // start the PWM
  ledcWrite(pin_pwm, int(duty_cycle*pwm_range));
  
  // read fault and current pins
  // fault_not = digitalRead(pin_fault);
  // Serial.print(fault_not, 5);
  // Serial.print(" ");

  //////////////////////////////
  //////////////////////////////
  // if (duty_cycle != duty_cycle_off) regulate_current(); //only when the system is on the duty cycle should be updated
  //////////////////////////////
  //////////////////////////////

  // print current and fault pins values
  // Serial.print(current, 5);
  // Serial.print(" ");
  // Serial.print(duty_cycle_on*100);
  // Serial.print(" ");

  // Serial.print(analogReadMilliVolts(pin_current)/1.1, 5);
  // Serial.print(" ");
  // Serial.println();

  // read the real first value of the ntc
  read_temperature(temperature_pin1, resistor_ref1, temperature_median_mat1, resistor_previous1, temperature_sensed_first);
  Serial.print(temperature_sensed_first);
  Serial.print(" ");

  // print the state of the controller
  if(duty_cycle == duty_cycle_off){ Serial.print(0); Serial.print(" ");}
  else {Serial.print(1); Serial.print(" ");}
  
  // Serial.print(20);
  // Serial.print(" ");
  // Serial.print(50);
  // Serial.print(" ");
  
  // read the real second value of the ntc
  // read_temperature(temperature_pin2, resistor_ref2, temperature_median_mat2, resistor_previous2, temperature_sensed_second);
  // Serial.print(temperature_sensed_second);
  // Serial.print(" ");
  
  // set the duty_cycle to the pin when the passed time is 0.1 sec
  hysteresis_controller(temperature_sensed_first);
  // hysteresis_controller(temperature_estimated_first);
  // Serial.print(" ");
  // end the loop
  median_mat_index = (median_mat_index+1)%median_window; // to change the position of the values in the matrix

  Serial.println();
  delay(10);
}

// void regulate_current(){
//   float current = read_current()/1000;
//   current_peltier_mat[current_mat_index] = current;
//   float current_peltier = mean(current_peltier_mat, current_mat_window); // mean fun is needed as the current itself has a ripple of more that 0.1 amp which is a bit big
//   resistor_peltier = voltage_supply*D/current_peltier - resistor_rlc1 - resistor_rlc2; // according to equation 1 from the calculations I made
//   duty_cycle_on = 1 - current_ref*(resistor_peltier + resistor_rlc1 + resistor_rlc2)/voltage_supply; // according to equation 2 from the calculations I made
  
//   current_mat_index = (current_mat_index+1)%current_mat_window;
// }

// float read_current(){
//   current = analogReadMilliVolts(pin_current);
//   current_median_mat[median_mat_index] = current;
//   float current_filtered = calc_median_outlier_filter(current_median_mat[0], current_median_mat[1], current_median_mat[2]);
//   current_filtered = calc_exponatial_filter(current_filtered, current_previous);
  
//   current_previous /= 1.1;
//   current_previous = current_filtered;
//   return current_filtered/1.1; // as the voltage is 1.1*current according to the datasheet
// }

void read_temperature(int signal_pin, float resistor_ref, float median_mat[], float& resistor_previous, float& temperature_sensed) {
  // reading the analog values
  float time_now = millis();
  float signal_voltage = analogReadMilliVolts(signal_pin);
  signal_voltage /= 1000;

  // calculating the NTC resistor depending on the voltage readings
  float resistor_temp = signal_voltage/(voltage_ref - signal_voltage)*resistor_ref;

  // adding the new values to the median matrix
  median_mat[median_mat_index] = resistor_temp;

  // calculating the resistor according to median filter for outlier values
  float resistor_filtered = calc_median_outlier_filter(median_mat[0], median_mat[1], median_mat[2]);

  // calculating the resistor according to exponatial filter (low pass filter)
  resistor_filtered = calc_exponatial_filter(resistor_filtered, resistor_previous);
  
  // calculating the temperature from the resistor
  temperature_sensed = calc_sensed_temperature(resistor_filtered);

  // raping up the function
  resistor_previous = resistor_filtered;
  // temperature_sensed_prev = temperature_sensed;
  // return(temperature_cel);
}

float calc_median_outlier_filter(float a, float b, float c) {
  if ((a <= b && b <= c) || (c <= b && b <= a)) return b;
  if ((b <= a && a <= c) || (c <= a && a <= b)) return a;

  return c;
}

float calc_exponatial_filter(float value_new, float value_previous){
  float value_filtered = smooth_factor*value_new + (1-smooth_factor)*value_previous;

  return value_filtered;
}

float calc_sensed_temperature(float resistor){
  float temperature = 1/(log(resistor/resistor_ref)/beta + 1/temperature_ref); // the formula of the temperature of NTC

  return (temperature-cel2kelv);
}

void hysteresis_controller(float temperature){
  if (temperature*direction > temperature_reference_max*direction) duty_cycle = duty_cycle_off;
  else if (temperature*direction < temperature_reference_min*direction) duty_cycle = duty_cycle_on;
  else return;
}
