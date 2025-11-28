#include "esp32-hal-gpio.h"
#include <c++/14.2.0/bits/utility.h>
// #include "esp32-hal.h"

#ifndef VIBROMOTORS_H
#define VIBROMOTORS_H

class Vibros {
  public:
    int vibro_pin1, vibro_pin2, vibro_pin3, vibro_pin4;
    unsigned long time_change_vibration = millis();
    int time_pattern = 500;
    int time_squence = 2000;
    String vibration_command = "";
    // define a state counter to jump between states of each pattern (or of each sequence)
    int state_counter = 0;
    int state_amount = 8;
    bool command_is_valid = false;

  // constructor of the class
  Vibros(int vibro_pin1, int vibro_pin2, int vibro_pin3, int vibro_pin4): // initializer to make it easier
    vibro_pin1 (vibro_pin1),
    vibro_pin2 (vibro_pin2),
    vibro_pin3 (vibro_pin3),
    vibro_pin4 (vibro_pin4)
    {
      
    }

  void begin(){
    pinMode(vibro_pin1, OUTPUT);
    pinMode(vibro_pin2, OUTPUT);
    pinMode(vibro_pin4, OUTPUT);
    pinMode(vibro_pin3, OUTPUT);
    // set all pins low
    digitalWrite(vibro_pin1, LOW);
    digitalWrite(vibro_pin2, LOW);
    digitalWrite(vibro_pin3, LOW);
    digitalWrite(vibro_pin4, LOW);
  }

  void set_vibration(String vibration){
    // zero the state counter as it should be zero when we start the sequence of states, the same for the time
    state_counter = 0;
    time_change_vibration = millis();
    command_is_valid = true;
    // store the vibration and then activate it
    vibration_command = vibration;
    // check if received a sequence that is valid
    if(vibration_command.length() == 4){
      is_valid_binary_mask(vibration_command); 
      if(!command_is_valid) return;
    }
    else if(vibration_command != "lr" and vibration_command != "ud" and vibration_command != "ci"){
      command_is_valid = false;
      return;
    }
    activate_pattern(); // only of the sequence is valid or there is a pattern
  }

  void is_valid_binary_mask(String str) { // checks if the message received has digits of zeros and ones
      if (str == ""){
          command_is_valid = false; // Null or empty string is invalid
          return;
      }
      // Iterate through every character until the null terminator ('\0')
      for (int i = 0; i<str.length(); i++) {
          // Check if the character is NOT '0' AND NOT '1'
          if (str[i] != '0' && str[i] != '1') {
              command_is_valid = false; // Found an invalid character (like 'a' or '2')
              return;
          }
      }
      // If we reach the end, the string only contained '0's and '1's
      command_is_valid = true; 
  }

  void activate_pattern(){
    // check the patter or the sequence and apply it
    if(vibration_command == "lr") left_right();
    else if(vibration_command == "ud") up_down();
    else if(vibration_command == "ci") circular();
    // if the command is a sequesnce of the shape 1001
    else if(vibration_command.length() == 4) sequence();

    // when the counter finishes the pattern, stop checking
    if(state_counter>=state_amount){
      command_is_valid = false;
      // turn off all the vibromotors
      digitalWrite(vibro_pin1, LOW);
      digitalWrite(vibro_pin2, LOW);
      digitalWrite(vibro_pin3, LOW);
      digitalWrite(vibro_pin4, LOW);
    }
  }

  void sequence(){
    if(state_counter%2==0){ // state0
      digitalWrite(vibro_pin1, vibration_command[0]-'0');
      digitalWrite(vibro_pin2, vibration_command[1]-'0');
      digitalWrite(vibro_pin3, vibration_command[2]-'0');
      digitalWrite(vibro_pin4, vibration_command[3]-'0');
      state_counter++;
    }
    else if(state_counter%2==1){ //state1
    // vibration_all_off
      digitalWrite(vibro_pin1, LOW);
      digitalWrite(vibro_pin2, LOW);
      digitalWrite(vibro_pin3, LOW);
      digitalWrite(vibro_pin4, LOW);
      state_counter = state_amount; // to stop the sequence completely, ending the checking of state
    }
  }

  void up_down(){
    // for(int i = 0; i < amount; i ++){
      // Up Down
    if(state_counter%2==0 && state_counter<state_amount){ // state0
      digitalWrite(vibro_pin1, HIGH);
      digitalWrite(vibro_pin2, HIGH);
      digitalWrite(vibro_pin3, LOW);
      digitalWrite(vibro_pin4, LOW);
      state_counter++;
    }
    else if(state_counter%2==1 && state_counter<state_amount){ //state1
      digitalWrite(vibro_pin1, LOW);
      digitalWrite(vibro_pin2, LOW);
      digitalWrite(vibro_pin3, HIGH);
      digitalWrite(vibro_pin4, HIGH);
      state_counter++;
    }
  }

  void left_right(){
    // for(int i = 0; i < amount; i ++){
      // Left Right
    if(state_counter%2==0 && state_counter<state_amount){ // state0
      digitalWrite(vibro_pin1, LOW);
      digitalWrite(vibro_pin2, HIGH);
      digitalWrite(vibro_pin3, HIGH);
      digitalWrite(vibro_pin4, LOW);
      state_counter++;
    }
    else if(state_counter%2==1 && state_counter<state_amount){ // state1
      digitalWrite(vibro_pin1, HIGH);
      digitalWrite(vibro_pin2, LOW);
      digitalWrite(vibro_pin3, LOW);
      digitalWrite(vibro_pin4, HIGH);
      state_counter++;
    }
  }

  void circular() {
    // for(int i = 0; i < amount; i ++){
      // Circular
    if(state_counter%4==0 && state_counter<state_amount){ // state0
      digitalWrite(vibro_pin1, HIGH);
      digitalWrite(vibro_pin2, LOW);
      digitalWrite(vibro_pin3, LOW);
      digitalWrite(vibro_pin4, LOW);
      state_counter++;
    }
    else if(state_counter%4==1 && state_counter<state_amount){ // state1
      digitalWrite(vibro_pin1, LOW);
      digitalWrite(vibro_pin2, HIGH);
      digitalWrite(vibro_pin3, LOW);
      digitalWrite(vibro_pin4, LOW);
      state_counter++;
    }
    else if(state_counter%4==2 && state_counter<state_amount){ // state2
      digitalWrite(vibro_pin1, LOW);
      digitalWrite(vibro_pin2, LOW);
      digitalWrite(vibro_pin3, HIGH);
      digitalWrite(vibro_pin4, LOW);
      state_counter++;
    }
    else if(state_counter%4==3 && state_counter<state_amount){ // state3
      digitalWrite(vibro_pin1, LOW);
      digitalWrite(vibro_pin2, LOW);
      digitalWrite(vibro_pin3, LOW);
      digitalWrite(vibro_pin4, HIGH);
      state_counter++;
    }
    // }
  }

  void run(){
    // run if the command was correct in the first place or that we finished the pattern
    if(command_is_valid){
      // pattern is activated: move to the next state
      if(vibration_command.length() == 2 and millis() - time_change_vibration > time_pattern){
        activate_pattern();
        time_change_vibration = millis();
      }
      // sequence is activated: move to the next state
      else if(vibration_command.length() == 4 and millis() - time_change_vibration > time_squence){
        activate_pattern();
        time_change_vibration = millis();
      }
      // update the time to change the pattern
    }
  }
};

#endif