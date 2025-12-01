#include <Peltier.h>

#ifndef TEMPERATURE_H_CONTROL_H
#define TEMPERATURE_H_CONTROL_H

class Temperature_h_control {
  // private:

  public:
    // Peltier* peltier1, *peltier2, *peltier3, *peltier4;
    Peltier* peltier_cells[4];

  /* constructor: we have to pass by reference as we have pointers refering to the objects. 
     If passed by value, then a copy will be made out of them and the pointer to this address is a pointer
     to a temporary address not the main object. */
  Temperature_h_control(Peltier& peltier1, Peltier& peltier2, Peltier& peltier3, Peltier& peltier4){
    // assign the new peltier low-level controller
    peltier_cells[0] = &peltier1;
    peltier_cells[1] = &peltier2;
    peltier_cells[2] = &peltier3;
    peltier_cells[3] = &peltier4;
  }

  void begin(){
    peltier_cells[0]->begin();
    peltier_cells[1]->begin();
    peltier_cells[2]->begin();
    peltier_cells[3]->begin();
  }

  void set_temperatures(String temps){
    if(temps.length() == 4){ // meaning that the message is a single actuation following "hcnh"
      for(int i=0; i<4; i++){
        // set the temperature reference to the peltier object
        if(temps[i] == 'h') peltier_cells[i]->temperature_ref = 40;
        else if(temps[i] == 'c') peltier_cells[i]->temperature_ref = 20;
        else if(temps[i] == 'n') peltier_cells[i]->temperature_ref = peltier_cells[i]->temperature_ambient;
        // start the controller for the peltier after updating its temp_ref
        hysteresis_controller(peltier_cells[i]);
      }
    }
  }

  void hysteresis_controller(Peltier* peltier){ 
    // update the temperature reading
    peltier->read_temperature();
    // check the position of the temperature with respect to the reference
    int direction = sign(peltier->temperature_ref - peltier->temperature_ambient);
    // set the controller parameters
    float temperature_boundry = 0.5;
    float temperature_ref_max = peltier->temperature_ref;// + direction*temperature_boundry;
    float temperature_ref_min = peltier->temperature_ref;// - direction*temperature_boundry;
    // Serial.println(peltier->pin_temperature);
    /*
    sending the duty_cycle of the peltier itself which is either the full power operation or the off operation
    for another controller we need to send the calculated dutycycle instead (or exactly 1-dutycycle to be
    compatible with the definition of pololu)
    */
    if (peltier->temperature_sensed*direction >= temperature_ref_max*direction) {
      // the state where direction == 0 (temp_ref == temp_ambient) is resolved here by sending duty_cycle_off
      peltier->send_to_controller(peltier->duty_cycle_off);
      // Serial.println(peltier->pin_temperature);
    }
    else if (peltier->temperature_sensed*direction < temperature_ref_min*direction) {
      peltier->send_to_controller(peltier->duty_cycle_on);
    }
    else return;
  }

  void run(){
    for(int i=0; i<4; i++){
      // Serial.println(i);
      hysteresis_controller(peltier_cells[i]);
    }
  }
};

#endif