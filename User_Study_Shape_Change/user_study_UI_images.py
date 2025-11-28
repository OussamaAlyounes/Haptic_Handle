import numpy as np
import serial
import time
import datetime
import tkinter as tk
from tkinter import messagebox
import threading
from PIL import Image, ImageTk

class User_Study:
    def __init__(self):
        #######################
        # identifying window, frames, entries, options, buttons and labels
        #######################
        # window
        self.my_window = tk.Tk()
        self.my_window.title("Experiment: Haptic Interface")
        self.window_width = 600
        self.window_height = 350
        self.my_window.geometry(f"{self.window_width}x{self.window_height}")
        
        # frames in the window for different stages
        self.frame_opening = tk.Frame(self.my_window, width=self.window_width, height=self.window_height)
        self.frame_testing = tk.Frame(self.my_window, width=self.window_width, height=self.window_height)
        self.frame_commanding = tk.Frame(self.my_window, width=self.window_width, height=self.window_height)
        self.frame_responding = tk.Frame(self.my_window, width=self.window_width, height=self.window_height)

        # labels
        font = 20
        self.label_command_text = tk.StringVar(value="Name")
        self.label_command = tk.Label(self.my_window, textvariable=self.label_command_text, font=font) # a changing label starts with name
        self.label_starting_point = tk.Label(self.frame_opening, text="Experiment", font=font) # label of te starting point
        
        # texts (instead of labels)
        self.text_command = tk.Text(self.my_window, height=6, width=50, bd = 0, font=font) # bd =0 to remove the boarder
        self.text_command.config(background=self.my_window.cget("bg")) # to make it the same background of the window

        # entries
        self.entry_name = tk.Entry(self.frame_opening, width= 20)

        # options
        options = ["1", "2"]
        self.option_starting_position_selected = tk.StringVar(value=options[0])
        self.option_starting_position = tk.OptionMenu(self.frame_opening, self.option_starting_position_selected, *options)
        self.option_starting_position.config(font=font-5)

        # buttons and bindings
        self.button_save = tk.Button(self.frame_opening, text= "Save", command=self.action_save, font=font)
        self.button_start = tk.Button(self.frame_opening, text= "Start", command=self.action_start, font = font)
        
        # self.button_test_noise = tk.Button(self.frame_testing, text = "Test", command= self.action_test_noise, font=font)
        self.frame_testing.bind('t', lambda event: self.action_test_noise())

        # self.button_continue = tk.Button(self.frame_testing, text= "Continue", command=self.action_continue, font=font)
        self.frame_testing.bind('c', lambda event: self.action_continue())

        # self.button_go = tk.Button(self.frame_commanding, text= "Go", command=self.action_trial, font=font)
        self.frame_commanding.bind('g', lambda event: self.action_trial())

        # self.button_yes = tk.Button(self.frame_responding, text = "Yes", command= lambda: self.action_yes_no('y'), font=font)
        self.frame_responding.bind('y', lambda event: self.action_yes_no('y'))

        # self.button_no = tk.Button(self.frame_responding, text = "No", command= lambda: self.action_yes_no('n'), font=font)
        self.frame_responding.bind('n', lambda event: self.action_yes_no('n'))

        # self.button_repeat = tk.Button(self.frame_responding, text = "Repeat", command= self.action_repeat, font=font)
        self.frame_responding.bind('r', lambda event: self.action_repeat())

        # importing keyboard letters images
        size = 40
        self.im_keyboard_c = ImageTk.PhotoImage(Image.open("images/keyboard_key_c.png").resize((size,size)))
        self.im_keyboard_g = ImageTk.PhotoImage(Image.open("images/keyboard_key_g.png").resize((size,size)))
        self.im_keyboard_n = ImageTk.PhotoImage(Image.open("images/keyboard_key_n.png").resize((size,size)))
        self.im_keyboard_y = ImageTk.PhotoImage(Image.open("images/keyboard_key_y.png").resize((size,size)))
        self.im_keyboard_r = ImageTk.PhotoImage(Image.open("images/keyboard_key_r.png").resize((size,size)))
        self.im_keyboard_t = ImageTk.PhotoImage(Image.open("images/keyboard_key_t.png").resize((size,size)))

        ################################
        #identifying variables for the trial
        self.iterations = 0
        self.iterations_max = 20

        self.gear_diameter = 15
        self.step_distance_init = 1 # mm for each side
        self.step_distance_min = 1/360*(np.pi*self.gear_diameter) # 1/360*(np.pi*self.gear_diameter)=0.13 mm minimum distance that corresponds to 1 deg (motor reolution)

        self.ora_counter = 0 # out of range counter, specially useful in the beginning of the experiment

        self.pose_motor_base = 0 # motor baseline which is 0 mm displacement
        self.pose_motor_max = 8 # mm
        
        self.step_distance = self.step_distance_init
        self.step_distance_array = []
        self.pose_motor_array = []
        
        self.repeated_request = False # repeated request to retry the position (it's allowed only once)

        self.repeated_go = 0
        ##########################
        # saved data
        self.time_start = datetime.datetime.now() # save the starting time of the experiment
        self.step_distance_array = []
        self.pose_motor_array = []
        self.times_array = []
        self.name = ""
        ##########################
        # open the window UI
        self.window_open()

    def send_motor(self, distance):
        ser = serial.Serial("COM5", 9600)
        angle = distance/(np.pi*self.gear_diameter)*360
        ser.write(f"{round(angle)}".encode())
        while True:
            if ser.in_waiting > 0:
                print(ser.readline().decode(errors='ignore')) # sometimes the returned value causes some error so it's better to ignore it
                break
        ser.close()

    def terminate_error(self):
        print(self.step_distance)
        messagebox.showwarning("Wow", message="That was fast!!\n."+"Thank you!")
        self.my_window.destroy()

    def terminate(self):
        messagebox.showinfo("Congrats!", message="Thank you for completing the experiment successfully")
        # Save the data in a file
        np.savez(file = f"{self.name}_{self.option_experiment}.npz", time_start = self.time_start, time_end = datetime.datetime.now(), 
                 iterations = self.iterations, steps_time = self.times_array, poses_motor = self.pose_motor_array, steps_distance = self.step_distance_array)
        self.my_window.destroy()

    def window_open(self):
        # show the opening window
        self.frame_opening.place(x=0,y=0)
        # change the text of the label
        self.label_command_text.set("Name")
        # place everything on the window
        self.label_command.place(x=self.window_width//2-80, y=self.window_height//4-50)
        self.entry_name.place(x=self.window_width//2, y=self.window_height//4-50, height= 30)
        self.label_starting_point.place(x=self.window_width//2-80, y=self.window_height//4)
        self.option_starting_position.place(x=self.window_width//2+40, y=self.window_height//4-5)
        self.button_save.place(x=(self.window_width-self.button_save.winfo_reqwidth())//2, y=(self.window_height-self.button_save.winfo_reqheight())//4+50)
        self.button_start.place(x=(self.window_width-self.button_start.winfo_reqwidth())//2, y=self.window_height-self.button_start.winfo_reqheight()-50)
        # start the window
        self.my_window.mainloop()
    
    def change_text(self, text1_arr, text2_arr, image_arr):
        self.text_command.config(state=tk.NORMAL) # make the text editable
        self.text_command.delete("1.0", tk.END) # delete the old content
        for text1, text2, image in zip(text1_arr, text2_arr, image_arr):
            self.text_command.insert(tk.END, text1) # add the first part of the text before the image
            self.text_command.image_create(tk.END, image=image) # add the image to the text
            self.text_command.insert(tk.END, text2) # add the second part of the text after the image
        
        # self.text_command.place(x=(self.window_width-self.text_command.winfo_reqwidth())//2+20, y=(self.window_height-self.text_command.winfo_reqheight())//2-90) # place the text
        self.text_command.place(x=(self.text_command.winfo_reqwidth()-self.text_command.winfo_reqwidth()//1.5)//2, y=(self.window_height-self.text_command.winfo_reqheight())//2-90) # place the text
        self.text_command.config(state=tk.DISABLED) # disable editing the text again

    def action_save(self):
        # save data
        if self.option_starting_position_selected.get() == '1':
            self.option_experiment = "min"
            self.direction = 1
            self.pose_motor = self.pose_motor_base # we start from the initial position
            self.answer_prev = "n"
        else:
            self.option_experiment = "max"
            self.direction = -1
            self.pose_motor = self.pose_motor_max # we start from the initial position
            self.answer_prev = "y"

        self.name = self.entry_name.get()

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
        self.change_text(["Put your hand OFF the device and press Test 't' "], [" to test the noise cancelation."], [self.im_keyboard_t])
        self.button_test_noise.place(x=(self.window_width-self.button_test_noise.winfo_reqwidth())//2, y=(self.window_height-self.button_test_noise.winfo_reqheight())//2)
        # self.button_continue.place(x=50, y=50)
        # time.sleep(2)

    def test_motors(self):
        # time.sleep(2)
        self.send_motor(5) # 5 mm
        time.sleep(1)
        self.send_motor(0) # 0 mm, minimum displacement or completely closed
        time.sleep(1)
        self.send_motor(8) # 8 mm
        time.sleep(1)
        self.send_motor(0) # 0 mm, minimum displacement or completely closed
        time.sleep(1)
        # show the button continue
        self.button_continue.place(x=(self.window_width-self.button_continue.winfo_reqwidth())//2, y=self.window_height-self.button_continue.winfo_reqheight()-50)
        self.button_test_noise.place(x=(self.window_width-self.button_test_noise.winfo_reqwidth())//2, y=(self.window_height-self.button_test_noise.winfo_reqheight())//2)
        self.change_text(["Keep adjusting the volume manually and then press Test 't' ", "When you stop hearing anything, press Continue "], 
                         [" again.\n", " ."], [self.im_keyboard_t, self.im_keyboard_c])
        
    def action_test_noise(self):
        # each tooth is 15 deg and corresonds to 1.98 mm in linear displacement. We work between 0-8 mm
        # remove the text
        self.text_command.place_forget()
        # add the label
        self.label_command_text.set("Now listen carefully, can you hear the motors moving?\n") # Adjusted to be label (DONE!)
        self.label_command.place(x=(self.window_width-self.label_command.winfo_reqwidth())//2, y=(self.window_height-self.label_command.winfo_reqheight())//2-50)
        self.button_continue.place_forget()
        self.button_test_noise.place_forget()            
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
        self.change_text(["Please open your hand and then press Go "], [" ."], [self.im_keyboard_g])
        self.button_go.place(x=(self.window_width-self.button_go.winfo_reqwidth())//2, y=(self.window_height-self.button_go.winfo_reqheight())//2)

    def action_trial(self):
        if self.repeated_go == 0: # move motor to baseline and ask to close the hand
            if not self.repeated_request: # print only in the beginning of the iteration
                print("Iteration # : ", self.iterations)

            self.text_command.place_forget() # remove the text at this stage only
            self.label_command_text.set("Please wait!!") # Step 1: we move to the baseline (always)
            self.label_command.place(x=(self.window_width-self.label_command.winfo_reqwidth())//2, y=(self.window_height-self.label_command.winfo_reqheight())//2-50)
            self.button_go.place_forget()

            self.my_window.update()
            self.send_motor(self.pose_motor_base)

            self.change_text(["Please hold the device and then press Go "], [" ."], [self.im_keyboard_g])
            self.button_go.place(x=(self.window_width-self.button_go.winfo_reqwidth())//2, y=(self.window_height-self.button_go.winfo_reqheight())//2)

        elif self.repeated_go == 1: # ask to open the hand
            self.change_text(["Remember how it feels... open your hand and then press Go "], [" ."], [self.im_keyboard_g])

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
            self.change_text(["Close your hand again to feel the new position.\n"+"Was the position different from the previous one?\n"+
                                        "Press Yes ",", No ", " or Repeate"], [" ", " ", " ."], [self.im_keyboard_y, self.im_keyboard_n, self.im_keyboard_r])

            button_pose_height = (self.window_height-self.button_yes.winfo_reqheight())//2
            self.button_yes.place(x=self.window_width//4 - self.button_yes.winfo_reqheight()//2, y=button_pose_height)
            self.button_no.place(x=(self.window_width - self.button_no.winfo_reqwidth())//2, y=button_pose_height)
            self.button_repeat.place(x=3*self.window_width//4 - self.button_repeat.winfo_reqwidth()//2, y=button_pose_height)
            
            # End of conditions if else
        self.repeated_go = (self.repeated_go + 1) % 3

    def action_repeat(self):
        if self.repeated_request: # repeated request to retry the position (it's allowed only once)
            messagebox.showwarning("Repeated Request!", message="You've already repeated this, you must choose an answer!")
        else:
            self.repeated_request = True
            messagebox.showwarning("Watch out your hand!", message="Please take your hand off the handle and then press OK to repeat the process.")
            self.action_continue(from_testing=False)
        
    def action_yes_no(self, answer):
        # only if the answer changed rom the previous answer, the direction is flipped and the step is halfed
        # taking into account that the pose is not on the limits, otherwise it will make the step smaller while we shouldn't change the step at all
        if answer != self.answer_prev and self.pose_motor != self.pose_motor_max and self.pose_motor != self.pose_motor_base:
            self.step_distance /=2
            self.direction = -self.direction
            self.answer_prev = answer
            if self.step_distance < self.step_distance_min:
                self.terminate()
                return # end the function if the program was terminated (this avoids continuing in the function and might cause printing some erros)
        
        # check if the user has abnormal sensation
        # print(f"answer: {answer}, {self.pose_motor}, {self.pose_motor_base}, {self.pose_motor_max}")
        if (answer == 'y' and self.pose_motor == self.pose_motor_base) or (answer == 'n' and self.pose_motor == self.pose_motor_max): 
            self.ora_counter += 1
            if self.ora_counter == 3:
                self.terminate_error()
                return # end the function if the program was terminated (this avoids continuing in the function and might cause printing some erros)
        
        else:
            self.ora_counter = 0
            # calculate the new position if only there is no sensitive case
            pose_motor_new = self.pose_motor + self.direction*self.step_distance # calculate the new position
            self.pose_motor = np.clip(pose_motor_new, self.pose_motor_base, self.pose_motor_max) # whatever the new position is, it doesn't exceed the limits
        
        # save the new data in the arrays
        self.step_distance_array.append(self.step_distance)
        self.pose_motor_array.append(self.pose_motor)
        self.times_array.append(datetime.datetime.now())
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