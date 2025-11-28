// set pololu pins
int pin_en = 7;
int pin_ph = 6;
int pin_fault = 5;
int pin_current = 4;
float current = 0;
float fault_not = 0;

// set pwm charactarestics pololu
float pwm_frequency = 100;
int pwm_resolution = 9;
int pwm_range = pow(2, pwm_resolution) -1;
float duty_cycle = 0.1; // 5%

// set temperature sensor pins
int temperature_pin1 = 0;
int temperature_pin2 = 1;

//set temperature sensor circuit parameters
float voltage_ref = 3.29; // 3.3v from esp
float resistor_temp = 0;
float resistor_ref1 = 32500; // 33k ohm measured
float resistor_ref2 = 32200; // 33k ohm measured
int analog_resolution = 12;

// set exponantial filter variables
float smooth_factor = 0.5;
// ..... for temperature
float resistor_previous1 = 10000; // 10k ohm around 25 celicious
float resistor_previous2 = 10000; // 10k ohm around 25 celicious
// ..... for current
float current_previous = 0;

// set midian filter variables
#define median_window 3
// ..... for temperature
float temperature_median_mat1[median_window] = {resistor_previous1, resistor_previous1, resistor_previous1};
float temperature_median_mat2[median_window] = {resistor_previous2, resistor_previous2, resistor_previous2};
// ..... for current
float current_median_mat[median_window] = {current_previous, current_previous, current_previous};

// int median_window = 3;
// float* median_mat1 = new float[median_window]();
// float* median_mat2 = new float[median_window]();

int sample_num = 0;

// set the temperature sensor charactaristics
float resistor_ref = 10000; // 10 k at 25 deg celsius
int cel2kelv = 273;
float temperature_ref = 25 + cel2kelv;
int beta = 3910; // got this value from plotting the data from the datasheet of NTC (in google sheet)
float temperature_first = 0;
float temperature_second = 0;

void setup() {
  // put your setup code here, to run once:
// set the output and input pins
pinMode(pin_en, OUTPUT);
pinMode(pin_ph, OUTPUT);
pinMode(pin_fault, INPUT);
pinMode(pin_current, INPUT);

// analog reading properties
analogReadResolution(analog_resolution); // it sets and reads the values in 12 bits (not only reading)
analogSetAttenuation(ADC_11db); // set the maximum input voltage to 2.778 v

// set initial values of the en/ph
digitalWrite(pin_ph, LOW);
ledcAttach(pin_en, pwm_frequency, pwm_resolution);
ledcWrite(pin_en, int(duty_cycle*pwm_range));

// start serial
Serial.begin(115200);
}

void loop() {
// put your main code here, to run repeatedly:
  fault_not = digitalRead(pin_fault);
  current = read_current(pin_current);
  // current /= 1000;
  // Serial.print(int(duty_cycle*pwm_range));
  // Serial.print(" ");
  // digitalWrite(pin_en, HIGH);

  // print current and fault pins values
  Serial.print(current, 5);
  Serial.print(" ");
  Serial.print(fault_not);
  Serial.print(" ");
  // Serial.println();

  // read the first value of the ntc
  temperature_first = read_temperature(temperature_pin1, resistor_ref1, temperature_median_mat1, resistor_previous1);
  Serial.print(temperature_first);
  Serial.print(" ");
  // read the second value of the ntc
  temperature_second = read_temperature(temperature_pin2, resistor_ref2, temperature_median_mat2, resistor_previous2);
  Serial.print(temperature_second);
  // end the loop
  sample_num = (sample_num+1)%median_window; // to change the position of the values in the matrix
  Serial.println();
  // delay(100);
}

float read_current(int current_pin){
  current = analogReadMilliVolts(pin_current);
  current_median_mat[sample_num] = current;
  float current_filtered = calc_median_outlier_filter(current_median_mat[0], current_median_mat[1], current_median_mat[2]);
  // current_filtered = calc_exponatial_filter(current_filtered, current_previous);
  
  return current_filtered;
}

float read_temperature(int signal_pin, float resistor_ref, float median_mat[], float& resistor_previous) {
  // reading the analog values
  float signal_voltage = analogReadMilliVolts(signal_pin);
  signal_voltage /= 1000;

  // calculating the NTC resistor  depending on the readings
  resistor_temp =  signal_voltage/(voltage_ref - signal_voltage)*resistor_ref;

  // adding the new values to the median matrix
  median_mat[sample_num] = resistor_temp;

  // calculating the resistor according to median filter for outlier values
  float resistor_filtered = calc_median_outlier_filter(median_mat[0], median_mat[1], median_mat[2]);

  // calculating the resistor according to exponatial filter (low pass filter)
  resistor_filtered = calc_exponatial_filter(resistor_filtered, resistor_previous);
  
  // calculating the temperature from the resistor
  float temperature_cel = calc_temperature(resistor_filtered);
  
  // raping up the function
  resistor_previous = resistor_filtered;
  return(temperature_cel);
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

float calc_temperature(float resistor){
  float temperature = 1/(log(resistor/resistor_ref)/beta + 1/temperature_ref); // the formula of the temperature of NTC

  return (temperature-cel2kelv);
}



















