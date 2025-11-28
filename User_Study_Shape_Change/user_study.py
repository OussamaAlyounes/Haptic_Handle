import numpy as np
import serial
import time
import datetime

def send_motor(distance):
    ser = serial.Serial("COM5", 9600)
    angle = displacement2deg(distance)
    ser.write(f"{angle}".encode())
    while True:
        if ser.in_waiting > 0:
            print(ser.readline().decode(errors='ignore')) # sometimes the returned value causes some error so it's better to ignore it
            break
    ser.close()

def displacement2deg(distance, gear_diameter = 15):
    # each tooth is 15 deg and corresonds to 1.98 mm in linear displacement. We work between 0-8 mm which correspnds to 0-60.61 deg
    distance_tooth = np.pi*gear_diameter/24 # a gear with 24 teeth and diameter of 15 mm
    return distance/distance_tooth*15 + 30 # we operate with a minimum angle of 30, so in the range 30-91.11 deg

# Part1: Testing
def test_noise():
    # each tooth is 15 deg and corresonds to 1.98 mm in linear displacement. We work between 0-8 mm
    print("Please remove your hand off the device and press continue.")
    answer = 'c'
    while answer != 'c':
        answer = 'cc' # Adjusted: change to read from keyboard
    
    print("Now listen carefully, can you hear the motors moving?")
    time.sleep(3)
    send_motor(5) # 5 mm
    time.sleep(1)
    send_motor(0) # 0 mm, minimum displacement or completely closed
    time.sleep(1)
    send_motor(8) # 8 mm
    time.sleep(1)
    send_motor(0) # 0 mm, minimum displacement or completely closed
    time.sleep(1)
    # print("Can you hear the motors moving?")

def experiment(name, pose_motor_init, gear_diameter = 15): # direction is the starting point of the study, from minimum displacement (0) or from maximum one (1)
    iterations = 0
    iterations_max = 30

    step_distance_init = 0.5 # mm
    step_distance_min = 2/360*(np.pi*gear_diameter) # minimum distance that corresponds to 2 deg (motor reolution)

    ora_counter = 0 # out of range counter, specially useful in the beginning of the experiment

    pose_motor_base = 0 # motor baseline which is 0 mm displacement
    pose_motor_max = 8 # mm
    
    direction = 1 # 1 or -1 (always)
    if pose_motor_init == pose_motor_max: # change the direction if we start from the highest value
        direction = -1
    
    step_distance = step_distance_init
    pose_motor = pose_motor_init # we start from the initial position
    step_distance_array = []
    pose_motor_array = []
    
    repeated = False # repeated request to retry the position (it's allowed only once)
    time_start = datetime.datetime.now() # save the starting time of the experiment

    while iterations < iterations_max:
        if not repeated:
            print("Iteration # : ", iterations)
        
        # Step 1: we move to the baseline (always)
        send_motor(pose_motor_base)
        time.sleep(1)
        print("Grasp the handle, please!") # ask the participant to try the baseline

        # ask to release the handle
        print("Remove your hand, please!")
        time.sleep(1) # adjusted to dontinue only after pressing a button

        # Step 2: we move to the new position
        send_motor(pose_motor)
        time.sleep(1)
        print("Grasp the handle, please!") # ask the participant to try the new position
        time.sleep(1)
        print("Do you feel a difference with the previous position?")
        
        answer = 'y' # Adjusted: to get answer from keyboard
        if answer == 'r':
            if repeated:
                print("You've already repeated this, please choose an answer!")
                while answer != 'y' or answer != 'n': # wait till you get "yes" or "no" answer
                    print(" ") # Adjusted: read the new letter
            else:
                repeated = True
                print("Please take your hand off the handle and then press continue!")
                answer = 'y' # Adjusted: to get answer from keyboard
                while answer != 'c': # wait until the user press continue
                    print(" ") # Adjusted: read the new letter
                continue
        
        # if answer == 'y' or answer == 'n':
        repeated = False
        answer_prev = 'n' # adjusted to vale from the user
        if answer != answer_prev:
            step_distance /=2
            direction = -direction
            if step_distance < step_distance_min:
                break
                    
        # Ask to release the handle
        print("Remove your hand, please!")
        time.sleep(1) # adjusted to continue only after pressing a button

        # we check if the new position is outside the range
        pose_motor_new = pose_motor + direction*step_distance # calculate the new position
        if pose_motor_new > pose_motor_max or pose_motor < pose_motor_base: 
            ora_counter += 1
            if ora_counter == 3:
                print("The experiment was terminated! You were outside the range 3 times.") # we break the program
                break
        
        else: 
            pose_motor = pose_motor_new
            ora_counter = 0
        
        iterations += 1
        step_distance_array.append(step_distance)
        pose_motor_array.append(pose_motor)
        # End of the loop

    # Save the data in a file
    np.savez(file = name + ".npz", time_start = time_start, time_end = datetime.datetime.now(), iterations = iterations, poses_motor = pose_motor_array, steps_distance = step_distance_array)

    print("THANK YOU for your participation in our experiment ;)")

if __name__=="__main__":
    name = "" # Adjusted: to read the name from the screen
    pose_motor_init = 0 # Adjust: read from the interface. motor starting comparison point: 0 mm (minimum dislacement) or 8 mm
    
    answer = 't'
    while answer !='t': # Adusted: wait to read from the keyboard
        test_noise()
        answer = 't' # Adusted: wait to read from the keyboard
    
    experiment(name = name, pose_motor_init = pose_motor_init) # Adjust: read pose_motor_init