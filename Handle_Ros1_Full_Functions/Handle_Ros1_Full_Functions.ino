#include <ros.h>
#include <std_msgs/String.h>
#include <std_msgs/Float32.h>
#include <std_msgs/Int32.h>

#include <Peltier.h>
#include <Temperature_H_Control.h>
#include <Servos.h>
#include <Vibromotors.h>

//// defining all the variables for the peltier and Peltier objects to assign them to the temperature controller
// peltier 1
int peltier1_pin_in1 = 12; // 12
int peltier1_pin_in2 = 13; // 13
int peltier1_pin_temperature = 35;
int peltier1_resistor_ref = 32300; //32450
Peltier peltier1(peltier1_pin_in1, peltier1_pin_in2, peltier1_pin_temperature, peltier1_resistor_ref);

// peltier 2
int peltier2_pin_in1 = 27; // 27
int peltier2_pin_in2 = 14; // 14
int peltier2_pin_temperature = 34;
int peltier2_resistor_ref = 32530; //32300
Peltier peltier2(peltier2_pin_in1, peltier2_pin_in2, peltier2_pin_temperature, peltier2_resistor_ref);

// peltier 3
int peltier3_pin_in1 = 25; // 17
int peltier3_pin_in2 = 26; // 16
int peltier3_pin_temperature = 39;
int peltier3_resistor_ref = 32620; //32160
Peltier peltier3(peltier3_pin_in1, peltier3_pin_in2, peltier3_pin_temperature, peltier3_resistor_ref);

// peltier 4
int peltier4_pin_in1 = 32; // 32
int peltier4_pin_in2 = 33; // 33
int peltier4_pin_temperature = 36;
int peltier4_resistor_ref = 32300; //32530 32190
Peltier peltier4(peltier4_pin_in1, peltier4_pin_in2, peltier4_pin_temperature, peltier4_resistor_ref);

// Temperature Controller
Temperature_h_control peltier_cells(peltier1, peltier2, peltier3, peltier4);

// define the vibromotors
int vibro_pin1 = 17;
int vibro_pin2 = 5;
int vibro_pin3 = 18;
int vibro_pin4 = 19;
Vibros vibros(vibro_pin1, vibro_pin2, vibro_pin3, vibro_pin4);

//// define the servo mtors
int servo_pin1 = 22;
int servo_pin2 = 23;
Servos servos(servo_pin1, servo_pin2);

//// define a publisher
std_msgs::String vibration_msg;
std_msgs::String temperature_msg;
std_msgs::Float32 servo_msg;
ros::Publisher vibration_status("handle/vibration_status", &vibration_msg);
ros::Publisher temperature_status("handle/temperature_status", &temperature_msg);
ros::Publisher servo_status("handle/servo_status", &servo_msg);

void vibraion_call_back(const std_msgs:String* msg) this is also correct as it is
a pointer to the message that holds its address and we thn must use msg->data instead of
msg.data but to pass a reference (a copy of the msg) is simpler allowing to use "."

void servo_call_back(const std_msgs::Float32& msg){
  /*
  the message should be a double indicating the distance (mm) that the servo should move
  */
  // servos.set_position(msg.data);

  servo_msg.data = msg.data;
  servo_status.publish(&servo_msg);
}

void vibration_call_back(const std_msgs::String& msg){
  /*
  the message should be either a sequence of commands like "1001" activating the first 
  and the fourth vibromotors, or to be one of the patterns "LR", "UD", "CI"
  */ 
  const char* command = msg.data; // the data of the message in the rosserial library has
                                  // a pointer to the data insted of the data itself, just
                                  // in order to save the RAM (it's how rosserial is designed)
  
  vibros.set_vibration(command);
  // String test = String(vibros.state_counter);
  // publish that vibration was received
  // vibration_msg.data = test.c_str();
  String test = String(vibros.time_change_vibration);
  vibration_msg.data = test.c_str();
  vibration_status.publish(&vibration_msg);
}

void temperature_call_back(const std_msgs::String& msg){
  /*
  the message should be either a sequence of commands like "hcnh" meaning 
  "hot, cold, neutral, hot" or to be one of the patterns "LR", "UD", "CI"
  */ 
  // assigning each temperature to its peltier
  const char* temps = msg.data;
  peltier_cells.set_temperatures(temps);

  // publish that vibration was received
  // temperature_msg.data = temps;
  String test = String(peltier_cells.peltier_cells[0]->temperature_ref) + " " + 
                String(peltier_cells.peltier_cells[1]->temperature_ref) + " " + 
                String(peltier_cells.peltier_cells[2]->temperature_ref) + " " + 
                String(peltier_cells.peltier_cells[3]->temperature_ref) + " ";
  temperature_msg.data = test.c_str();
  temperature_status.publish(&temperature_msg);
}

// define the node handle
// ros::NodeHandle nh;
// ros::NodeHandle_<ArduinoHardware> nh;
ros::NodeHandle_<ArduinoHardware, 25, 25, 512, 512> nh; // the declaration in this way is better as the buffer size
                                                        // gets bigger to 512 and only with this we can listen
                                                        // to this topics published
// define 3 subscribers (servos, vibros, peltiers)
ros::Subscriber<std_msgs::Float32> servo_cmd("handle/servo_distance", &servo_call_back);
ros::Subscriber<std_msgs::String> vibration_cmd("handle/vibration_pattern", &vibration_call_back);
ros::Subscriber<std_msgs::String> temperature_cmd("handle/temperature_pattern", &temperature_call_back);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(57600); // simply na NOT be any other value!!!

  delay(500); // just to see if it will fix the connection issue

  nh.initNode();
  delay(500);

  // initialize all pins of each object
  // for(int i=0; i<10; i++)Serial.print(0);
  servos.begin();
  // for(int i=0; i<10; i++)Serial.print(1);
  vibros.begin();
  // for(int i=0; i<10; i++)Serial.print(2);
  peltier_cells.begin();
  // for(int i=0; i<10; i++)Serial.print(3);
  
  // initializing the subscribers and publishers
  nh.subscribe(servo_cmd);
  nh.subscribe(vibration_cmd);
  nh.subscribe(temperature_cmd);
  nh.advertise(servo_status);
  nh.advertise(vibration_status);
  nh.advertise(temperature_status);
}

void loop() {
  // put your main code here, to run repeatedly:
  // read the ros topics and check call_backs and stuff
  nh.spinOnce();
  // check on the status of the actutor so that each command is actuated for a specific time, and to keep the 
  // temperature closed loop working fine
  vibros.run();
  peltier_cells.run();
  delay(10);
  Serial.println(10);

}
