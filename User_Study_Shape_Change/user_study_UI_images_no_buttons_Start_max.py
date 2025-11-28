import numpy as np
import serial
import time
import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import font
import threading
from PIL import Image, ImageTk
import os, sys

class User_Study:
    def __init__(self):
        #######################
        # identifying window, frames, entries, options, buttons and labels
        #######################
        # window
        self.my_window = tk.Tk()
        self.my_window.title("Experiment: Haptic Interface")
        self.window_width = 650
        self.window_height = 350
        self.my_window.geometry(f"{self.window_width}x{self.window_height}")
        
        # frames in the window for different stages
        self.frame_opening = tk.Frame(self.my_window, width=self.window_width, height=self.window_height)
        self.frame_testing = tk.Frame(self.my_window, width=self.window_width, height=self.window_height)
        self.frame_commanding = tk.Frame(self.my_window, width=self.window_width, height=self.window_height)
        self.frame_responding = tk.Frame(self.my_window, width=self.window_width, height=self.window_height)

        # labels
        my_font = 20
        self.label_command_text = tk.StringVar(value="Name")
        self.label_command = tk.Label(self.my_window, textvariable=self.label_command_text, font=my_font) # a changing label starts with name
        self.label_starting_point = tk.Label(self.frame_opening, text="Experiment", font=my_font) # label of te starting point
        self.label_sex = tk.Label(self.frame_opening, text= "Sex", font=my_font)
        self.label_dominant_hand = tk.Label(self.frame_opening, text= "Dominant Hand", font = my_font)
        self.label_hand_length = tk.Label(self.frame_opening, text= "Hand Length", font=my_font)
        self.label_finger_length = tk.Label(self.frame_opening, text= "Finger Length", font=my_font)

        # texts (instead of labels)
        self.text_command = tk.Text(self.my_window, height=10, width=70, bd = 0, font=my_font) # bd =0 to remove the boarder
        self.text_command.tag_configure("red", foreground="red")
        self.text_command.tag_configure("blue", foreground="blue")
        self.text_command.config(background=self.my_window.cget("bg")) # to make it the same background of the window

        # entries
        self.entry_name = tk.Entry(self.frame_opening, width= 20, font=my_font-10)
        self.entry_hand_length = tk.Entry(self.frame_opening, width= 5, font=my_font-10)
        self.entry_finger_length = tk.Entry(self.frame_opening, width= 5, font=my_font-10)

        # options
        options = ["1", "2"]
        self.option_starting_position_selected = tk.StringVar(value=options[0])
        self.option_starting_position = tk.OptionMenu(self.frame_opening, self.option_starting_position_selected, *options)
        self.option_starting_position.config(font=my_font-5)

        options = ["male", "female"]
        self.option_sex_selected = tk.StringVar(value=options[0])
        self.option_sex = tk.OptionMenu(self.frame_opening, self.option_sex_selected, *options)
        self.option_sex.config(font=my_font-5)
        
        options = ["right", "left"]
        self.option_dominant_hand_selected = tk.StringVar(value=options[0])
        self.option_dominant_hand = tk.OptionMenu(self.frame_opening, self.option_dominant_hand_selected, *options)
        self.option_dominant_hand.config(font=my_font-5)

        # buttons and bindings
        self.button_save = tk.Button(self.frame_opening, text= "Save", command=self.action_save, font=my_font, bg="skyblue")
        self.button_start = tk.Button(self.frame_opening, text= "Start", command=self.action_start, font = my_font, bg="green")
        
        # self.button_test_noise = tk.Button(self.frame_testing, text = "Test", command= self.action_test_noise, font=font)
        self.frame_testing.bind('t', lambda event: self.action_test_noise())

        # self.button_continue = tk.Button(self.frame_testing, text= "Continue", command=self.action_continue, font=font)
        self.frame_testing.bind('<space>', lambda event: self.action_continue())

        # self.button_go = tk.Button(self.frame_commanding, text= "Go", command=self.action_trial, font=font)
        self.frame_commanding.bind('<space>', lambda event: self.action_trial()) # go

        # self.button_yes = tk.Button(self.frame_responding, text = "Yes", command= lambda: self.action_yes_no('y'), font=font)
        self.frame_responding.bind('a', lambda event: self.action_yes_no('y')) # bind yes with key letter 'a'

        # self.button_no = tk.Button(self.frame_responding, text = "No", command= lambda: self.action_yes_no('n'), font=font)
        self.frame_responding.bind('d', lambda event: self.action_yes_no('n')) # bind yes with key letter 'd'

        # self.button_repeat = tk.Button(self.frame_responding, text = "Repeat", command= self.action_repeat, font=font)
        self.frame_responding.bind('r', lambda event: self.action_repeat())

        # importing keyboard letters images
        size = 40
        self.im_keyboard_d = ImageTk.PhotoImage(Image.open("images/keyboard_key_d.png").resize((size,size))) # no
        self.im_keyboard_a = ImageTk.PhotoImage(Image.open("images/keyboard_key_a.png").resize((size,size))) # yes
        self.im_keyboard_r = ImageTk.PhotoImage(Image.open("images/keyboard_key_r.png").resize((size,size))) # repeat
        self.im_keyboard_t = ImageTk.PhotoImage(Image.open("images/keyboard_key_t.png").resize((size,size)))
        self.im_keyboard_space = ImageTk.PhotoImage(Image.open("images/keyboard_key_space3.png").resize((60,size)))

        ################################
        #identifying variables for the trial
        self.directory = os.path.dirname(os.path.abspath(sys.argv[0]))+"\Data"
        self.iterations = 0
        self.iterations_max = 12

        self.gear_diameter = 15
        self.step_distance_init = 8/360*(np.pi*self.gear_diameter) # 1.0472 mm for each side (correspond to exactly 8 degrees)
        self.step_distance_min = 1/360*(np.pi*self.gear_diameter) # 1/360*(np.pi*self.gear_diameter)=0.13 mm minimum distance that corresponds to 1 deg (motor reolution)

        self.ora_counter = 0 # out of range counter, specially useful in the beginning of the experiment

        # self.pose_motor_base = 0 # motor baseline which is 0 mm displacement
        self.pose_motor_base = 6 # motor baseline which is 6 mm displacement
        self.pose_motor_max = 6 # mm
        self.pose_motor_min = 0
        self.step_distance = self.step_distance_init
        self.repeated_request = False # repeated request to retry the position (it's allowed only once)

        self.repeated_go = 0
        ##########################
        # saved data
        self.time_start = datetime.datetime.now() # save the starting time of the experiment
        self.step_distance_array = []
        self.pose_motor_array = []
        self.times_array = []
        self.answers_array = []
        self.name = ""
        self.sex = ""
        self.dominant_hand = "right"
        self.hand_length = 0
        self.finger_length = 0
        self.successful = True # to check if the user data is helpful
        ##########################
        # open the window UI
        self.window_open()

    def send_motor(self, distance):
        ser = serial.Serial("COM5", 9600)
        angle = distance/(np.pi*self.gear_diameter)*360 + 30 # we operate with a minimum angle of 30, so in the range 30-91.11 deg
        ser.write(f"{round(angle)}".encode())
        while True:
            if ser.in_waiting > 0:
                print(ser.readline().decode(errors='ignore')) # sometimes the returned value causes some error so it's better to ignore it
                break 
        ser.close()

    def terminate(self, Fail = False):
        messagebox.showinfo("Congrats!", message="Thank you for completing the experiment!")
        # change the successfulness if necessary
        if Fail:
            self.successful = False
        # Save the data in a file
        np.savez(file = f"{self.directory}\{self.name}_{self.option_experiment}.npz", name = self.name, experiment = self.option_experiment,
                 time_start = self.time_start, time_end = datetime.datetime.now(), 
                 hand_length = self.hand_length, finger_length = self.finger_length, sex = self.sex, successful = self.successful,
                 dominant_hand = self.dominant_hand, answers = self.answers_array, iterations = self.iterations, 
                 steps_time = self.times_array, poses_motor = self.pose_motor_array, steps_distance = self.step_distance_array)
        self.my_window.destroy()

    def window_open(self):
        # show the opening window
        self.frame_opening.place(x=0,y=0)
        # change the text of the label
        self.label_command_text.set("Name")
        # place everything on the window
        rows = [self.window_height//4-50, self.window_height//4, self.window_height//2-30]
        # Name
        self.label_command.place(x=self.window_width//2-100, y=rows[0])
        self.entry_name.place(x=self.window_width//2-50, y=rows[0]-3, height= 30)
        # Experiment
        self.label_starting_point.place(x=self.window_width//4-100, y=rows[1])
        self.option_starting_position.place(x=self.window_width//4-15, y=rows[1]-5)
        # sex
        self.label_sex.place(x=self.window_width//2-85, y=rows[1])
        self.option_sex.place(x=self.window_width//2-50, y=rows[1]-5)
        # dominant hand
        self.label_dominant_hand.place(x=self.window_width*3//4-100, y=rows[1])
        self.option_dominant_hand.place(x=self.window_width*3//4+20, y=rows[1]-5)
        # hand length
        self.label_hand_length.place(x=self.window_width//4-100, y= rows[2])
        self.entry_hand_length.place(x=self.window_width//4, y=rows[2]-5, height= 30)
        # finger length
        self.label_finger_length.place(x=self.window_width//2-100, y=rows[2])
        self.entry_finger_length.place(x=self.window_width//2+10, y=rows[2]-5, height= 30)
        # buttons
        self.button_save.place(x=(self.window_width-self.button_save.winfo_reqwidth())//2, y=self.window_height-self.button_save.winfo_reqheight()-100)
        self.button_start.place(x=(self.window_width-self.button_start.winfo_reqwidth())//2, y=self.window_height-self.button_start.winfo_reqheight()-50)

        position_x = (self.my_window.winfo_screenwidth()- self.window_width)//2
        position_y = self.my_window.winfo_screenheight()//2- self.window_height*3//4
        self.my_window.geometry('%dx%d+%d+%d' % (self.window_width, self.window_height, position_x, position_y))
        # start the window
        self.my_window.mainloop()

    def change_text(self, text1_arr, text2_arr, image_arr):
        self.text_command.config(state=tk.NORMAL) # make the text editable
        self.text_command.delete("1.0", tk.END) # delete the old content
        for text1, text2, image in zip(text1_arr, text2_arr, image_arr):
            # check if the word "OPEN" or "CLOSE" exists and make bold and colorful
            pose_open = text1.find("OPEN")
            pose_close = text1.find("CLOSE")
            if pose_open !=-1:
                self.text_command.insert(tk.END, text1[:pose_open])
                self.text_command.insert(tk.END, text1[pose_open:pose_open+4], 'red') # OPEN is 4 letters
                self.text_command.insert(tk.END, text1[pose_open+4:])
            elif pose_close !=-1:
                self.text_command.insert(tk.END, text1[:pose_close])
                self.text_command.insert(tk.END, text1[pose_close:pose_close+5], "red") # CLOSE is 5 letters
                self.text_command.insert(tk.END, text1[pose_close+5:])
            else:
                self.text_command.insert(tk.END, text1) # add the first part of the text before the image
            
            self.text_command.image_create(tk.END, image=image) # add the image to the text
            self.text_command.insert(tk.END, text2) # add the second part of the text after the image
        
        self.text_command.place(x=(self.text_command.winfo_reqwidth())//15, y=(self.window_height-self.text_command.winfo_reqheight())//2-70) # place the text
        self.text_command.config(state=tk.DISABLED) # disable editing the text again

    def action_save(self):
        # save data
        if self.option_starting_position_selected.get() == '1':
            self.option_experiment = "min"
            self.direction = 1
            self.pose_motor = self.pose_motor_min # we start from the minimum position
            self.answer_prev = "y" # opposite from the norm to prevent reversing the direction and halfing the distance on the first step
        else:
            self.option_experiment = "max"
            self.direction = -1
            self.pose_motor = self.pose_motor_max # we start from the maximum position
            self.answer_prev = "n" # opposite from the norm to prevent reversing the direction and halfing the distance on the first step

        self.name = self.entry_name.get()
        self.dominant_hand = self.option_dominant_hand_selected.get()
        self.sex = self.option_sex_selected.get()
        self.hand_length = self.entry_hand_length.get()
        self.finger_length = self.entry_finger_length.get()

    def action_start(self):
        # destroy the old frame and the label_command
        for widget in self.frame_opening.winfo_children():
            widget.destroy()
        self.label_command.place_forget() # remove the label for this action start
        # add the new frame
        self.frame_testing.place(x=0, y=0)
        self.frame_testing.focus_set() # to allow the frame to receive commands from the keyboard
        # self.frame_testing.config(background = "red")
        # place new frame (Testing)
        self.change_text(["OPEN your hand and press Test 't' "], [" to test the noise cancelation."], [self.im_keyboard_t])

    def test_motors(self):
        # time.sleep(2)
        self.send_motor(self.pose_motor_max/2) # 5 mm
        time.sleep(1)
        self.send_motor(self.pose_motor_min) # 0 mm, minimum displacement or completely closed
        time.sleep(1)
        self.send_motor(self.pose_motor_max) # 8 mm
        time.sleep(1)
        self.send_motor(self.pose_motor_min) # 0 mm, minimum displacement or completely closed
        time.sleep(1)
        # show the button continue
        self.change_text(["If you heard the motors, adjust the volume manually and then press Test 't' ", "If you couldn't hear anything, press <Space> "], 
                         [" again.\n", " ."], [self.im_keyboard_t, self.im_keyboard_space])
        
    def action_test_noise(self):
        # each tooth is 15 deg and corresonds to 1.98 mm in linear displacement. We work between 0-8 mm
        # remove the text
        self.text_command.place_forget()
        # add the label
        self.label_command_text.set("Now listen carefully, can you hear the motors moving?\n") # Adjusted to be label (DONE!)
        self.label_command.place(x=(self.window_width-self.label_command.winfo_reqwidth())//2, y=(self.window_height-self.label_command.winfo_reqheight())//2-50)
        # self.button_continue.place_forget()
        # self.button_test_noise.place_forget()            
        # open a thread since it's a long function
        threading.Thread(target=self.test_motors).start()

    def action_continue(self, from_testing = True):
        # remove the old frame (it could be 'testing' or 'responding' depending on which state we come from)
        if from_testing:
            for widget in self.frame_testing.winfo_children():
                widget.destroy()
        else:
            self.frame_responding.place_forget() # hide the old frame (responding) without destroying it
        # place new frame (Command)
        self.frame_commanding.place(x=0, y=0)
        self.frame_commanding.focus_set() # to allow the frame to receive commands from the keyboard
        self.change_text(["Please OPEN your hand and then press <Space> "], [" ."], [self.im_keyboard_space])
        # self.button_go.place(x=(self.window_width-self.button_go.winfo_reqwidth())//2, y=(self.window_height-self.button_go.winfo_reqheight())//2)

    def action_trial(self):
        if self.repeated_go == 0: # move motor to baseline and ask to close the hand
            if not self.repeated_request: # print only in the beginning of the iteration
                print("Iteration # : ", self.iterations)

            self.text_command.place_forget() # remove the text at this stage only
            self.label_command_text.set("Please wait!!") # Step 1: we move to the baseline (always)
            self.label_command.place(x=(self.window_width-self.label_command.winfo_reqwidth())//2, y=(self.window_height-self.label_command.winfo_reqheight())//2-50)
            # self.button_go.place_forget()

            self.my_window.update()
            self.send_motor(self.pose_motor_base) # always to baseline

            self.change_text(["Now, CLOSE your hand and then press <Space> "], [" ."], [self.im_keyboard_space])
            # self.button_go.place(x=(self.window_width-self.button_go.winfo_reqwidth())//2, y=(self.window_height-self.button_go.winfo_reqheight())//2)

        elif self.repeated_go == 1: # ask to open the hand
            self.change_text(["Remember how it feels... OPEN your hand and then press <Space> "], [" ."], [self.im_keyboard_space])

        else: # move to the next frame (responding)
            # hide the old frame (commanding) without destroying it and the text_command
            self.frame_commanding.place_forget()
            self.text_command.place_forget()
            # change the label content
            self.label_command_text.set("Please wait!!")
            self.label_command.place(x=(self.window_width-self.label_command.winfo_reqwidth())//2, y=(self.window_height-self.label_command.winfo_reqheight())//2-50)
            self.my_window.update() # to force change the window content
            # move motor
            self.send_motor(self.pose_motor) # Step 2: we move to the new position
            # time.sleep(1)
            
            # show new frame
            self.frame_responding.place(x=0, y=0)
            self.frame_responding.focus_set() # to allow the frame to receive commands from the keyboard
            self.change_text(["CLOSE your hand again to feel the new position.\n"+"Was the position different from the previous one?\n"+
                                        "If Yes, press 'A' ","If No, Press 'D' ", "If you wish to Repeat, press 'R' "], 
                             [" .\n", " .\n", " ."], [self.im_keyboard_a, self.im_keyboard_d, self.im_keyboard_r])

            # button_pose_height = (self.window_height-self.button_yes.winfo_reqheight())//2
            # self.button_yes.place(x=self.window_width//4 - self.button_yes.winfo_reqheight()//2, y=button_pose_height)
            # self.button_no.place(x=(self.window_width - self.button_no.winfo_reqwidth())//2, y=button_pose_height)
            # self.button_repeat.place(x=3*self.window_width//4 - self.button_repeat.winfo_reqwidth()//2, y=button_pose_height)
            
            # End of conditions if else
        self.repeated_go = (self.repeated_go + 1) % 3
    
    def save_data(self, answer):
        # save the new data in the arrays
        self.step_distance_array.append(self.step_distance)
        self.pose_motor_array.append(self.pose_motor)
        self.times_array.append(datetime.datetime.now())
        self.answers_array.append(answer)

    def action_repeat(self):
        if self.repeated_request: # repeated request to retry the position (it's allowed only once)
            messagebox.showwarning("Repeated Request!", message="You've already repeated this, you must choose an answer!")
        else:
            self.save_data('r') # save before repeating the procedure
            self.repeated_request = True
            messagebox.showwarning("Watch out your hand!", message="Please OPEN the handle and then press OK to repeat the process.")
            self.action_continue(from_testing=False)
        
    def action_yes_no(self, answer):
        # save data before changing the values
        self.save_data(answer)

        # check if the user has abnormal sensation
        if (answer == 'y' and self.pose_motor == self.pose_motor_max) or (answer == 'n' and self.pose_motor == self.pose_motor_min): 
            self.ora_counter += 1
            if self.ora_counter == 3:
                self.terminate(Fail = True)
                return # end the function if the program was terminated (this avoids continuing in the function and might cause printing some erros)
        
        else:
            self.ora_counter = 0
            # only if the answer changed from the previous answer, the direction is flipped and the step is halfed
            # taking into account that the pose is not on the limits, otherwise it will make the step smaller while we shouldn't change the step at all
            if answer != self.answer_prev: # only if we have passed the first movement, this condition is achieved
                self.step_distance /=2
                self.direction = -self.direction
                self.answer_prev = answer
                if self.step_distance < self.step_distance_min:
                    self.terminate()
                    return # end the function if the program was terminated (this avoids continuing in the function and might cause printing some erros)
        
            # calculate the new position if only there is no sensitive case
            pose_motor_new = self.pose_motor + self.direction*self.step_distance # calculate the new position
            self.pose_motor = np.clip(pose_motor_new, self.pose_motor_min, self.pose_motor_max) # whatever the new position is, it doesn't exceed the limits

        # move to the next iteration
        self.repeated_request = False
        self.iterations += 1
        if self.iterations > self.iterations_max:
            self.terminate()
            return # end the function if the program was terminated (this avoids continuing in the function and might cause printing some erros)
        # move back to previous frame to start the new iteration
        self.action_continue(from_testing=False)

if __name__=="__main__":
    user = User_Study()