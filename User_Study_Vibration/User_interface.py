import numpy as np
import tkinter as tk
from tkinter import messagebox
import serial
import time
import os
import threading

class User_Study:
    def __init__(self):
        # directory of the data to be saved
        self.directory = os.path.dirname(os.path.abspath(__file__))+"\\Data"
        # about the text
        self.font = 14
        self.font_title = 17
        # responses and references to be recorded
        self.time_responses = []
        self.vibration_responses = []
        self.vibration_references = []
        self.cover_references = []
        # define 3 states of the cover positions
        self.cover_positions = ["fc", "ho", "fo"] # fully-closed, half-open, fully-open
        self.cover_postion_ind = 0
        # define 3 vibration patterns
        self.vibration_patterns_ref = ["lr", "ud", "ci"] # left-right, up-down, circular
        # define a random list of the three vibration patterns, each repeated twice
        self.vibration_patterns = self.vibration_patterns_ref*2
        np.random.shuffle(self.vibration_patterns)
        self.vibration_command_ind = 0

        # define the window and it geometry
        self.window_width = 500
        self.window_height = 300
        self.my_window = tk.Tk()
        # Get screen width and height
        screen_width = self.my_window.winfo_screenwidth()
        screen_height = self.my_window.winfo_screenheight()
        # Calculate position
        x = (screen_width // 2) - (self.window_width // 2)
        y = (screen_height // 2) - (self.window_height // 2)-100
        self.my_window.title("User Study: Vibration Perception")
        self.my_window.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
        
        ############################
        # define the frames
        ############################
        self.frame_start = tk.Frame(self.my_window,) # record user's data
        self.frame_test = tk.Frame(self.my_window) # test the vibrations
        self.frame_vibrate = tk.Frame(self.my_window) # start the vibration in the beginning
        self.frame_respond = tk.Frame(self.my_window) # get the user's response

        ############################
        ############################
        # define the components of each frame
        ############################
        ############################

        # start frame
        ############################
        # message of the frame
        self.message_frame_start = tk.Label(self.frame_start, text="Please, Enter Your Data!")
        self.write_frame_message(self.message_frame_start)
        # labels
        self.label_name = tk.Label(self.frame_start, text="name", font= self.font)
        self.label_age = tk.Label(self.frame_start, text="age", font= self.font)
        self.label_sex = tk.Label(self.frame_start, text="sex", font= self.font)
        self.label_hand = tk.Label(self.frame_start, text= "dominant hand", font= self.font)
        # texts
        self.entry_name = tk.Entry(self.frame_start, background="white", font= self.font)
        self.entry_age = tk.Entry(self.frame_start, background="white", font= self.font)
        # buttons
        self.button_save = tk.Button(self.frame_start, text="Save", command=self.action_save_data, 
                                     background="lightsalmon", font= self.font)
        self.button_continue_start = tk.Button(self.frame_start, text="Continue", command=self.action_continue_start, 
                                         background="dodgerblue", font= self.font)
        # menus
        self.options_sex_list = ["male", "female"]
        self.option_sex_selected = tk.StringVar(value=self.options_sex_list[0])
        self.option_menu_sex = tk.OptionMenu(self.frame_start, self.option_sex_selected, *self.options_sex_list) 
        self.option_menu_sex.config(font= self.font)
        
        self.options_hand_list = ["left", "right"]
        self.option_hand_selected = tk.StringVar(value=self.options_hand_list[1])      
        self.option_menu_hand = tk.OptionMenu(self.frame_start, self.option_hand_selected, *self.options_hand_list)
        self.option_menu_hand.config(font= self.font)

        # placing all the components in the frame
        self.frame_start_place()

        # test frame
        ############################
        # message of the frame
        self.message_frame_test = tk.Label(self.frame_test, 
                                           text="Try out the patterns.\nPress continue when you finish them all!")
        self.write_frame_message(self.message_frame_test)
        # labels
        self.label_vibrate_lr = tk.Label(self.frame_test, text="1", font=self.font_title)
        self.label_vibrate_ud = tk.Label(self.frame_test, text="2", font=self.font_title)
        self.label_vibrate_ci = tk.Label(self.frame_test, text="3", font=self.font_title)
        self.label_continue = tk.Label(self.frame_test, text="<Enter>", font=self.font_title)
        # buttons
        self.button_vibrate_lr = tk.Button(self.frame_test, text="Left-Right", command=lambda: self.action_vibrate("lr"), 
                                           font= self.font, background="lightgreen")
        self.button_vibrate_ud = tk.Button(self.frame_test, text="Up-Down", command=lambda: self.action_vibrate("ud"), 
                                           font= self.font, background="lightgreen")
        self.button_vibrate_ci = tk.Button(self.frame_test, text="Circular", command=lambda: self.action_vibrate("ci"), 
                                           font= self.font, background="lightgreen")
        self.button_continue_test = tk.Button(self.frame_test, text="Continue", command=self.action_continue_test, 
                                         font= self.font, background="dodgerblue")
        # keyboard (for binding with a keyboard key, lambda event is a must unlike the buttons)
        self.frame_test.bind("1", func=lambda event: self.action_vibrate("lr")) 
        self.frame_test.bind("2", func=lambda event: self.action_vibrate("ud"))
        self.frame_test.bind("3", func=lambda event : self.action_vibrate("ci"))
        self.frame_test.bind("<Return>", func=lambda event:self.action_continue_test())
        # placing all the components in the frame
        self.frame_test_place()

        # vibrate frame
        ############################
        # message of the frame
        self.message_frame_vibrate = tk.Label(self.frame_vibrate, text="Sense the vibration!")
        self.write_frame_message(self.message_frame_vibrate)
        self.frame_vibrate.place(relheight=1, relwidth=1)

        # response frame
        ############################
        # message of the frame
        self.message_frame_response = tk.Label(self.frame_respond, text="How did the vibration feel like?", 
                                                     font=self.font_title)
        self.write_frame_message(self.message_frame_response)
        # labels
        self.label_response_lr = tk.Label(self.frame_respond, text="1", font=self.font_title)
        self.label_response_ud = tk.Label(self.frame_respond, text="2", font=self.font_title)
        self.label_response_ci = tk.Label(self.frame_respond, text="3", font=self.font_title)
        # buttons
        self.button_response_lr = tk.Button(self.frame_respond, text="Left-Right", command=lambda: self.action_save_response("lr"),
                                            font= self.font, background="yellow")
        self.button_response_ud = tk.Button(self.frame_respond, text="Up-Down", command=lambda: self.action_save_response("ud"), 
                                            font= self.font, background="yellow")
        self.button_response_ci = tk.Button(self.frame_respond, text="Circular", command=lambda: self.action_save_response("ci"), 
                                            font= self.font, background="yellow")
        # keyboard (for binding with a keyboard key, lambda event is a must unlike the buttons)
        self.frame_respond.bind("1", func=lambda event: self.action_save_response("lr")) 
        self.frame_respond.bind("2", func=lambda event: self.action_save_response("ud"))
        self.frame_respond.bind("3", func=lambda event : self.action_save_response("ci"))
        # placing all the components in the frame
        self.frame_response_place()

        # start the window and the first frame
        self.frame_start.tkraise()
        self.my_window.mainloop()

    def write_frame_message(self, label):
        label.config(font=("", self.font_title, "bold"))
        label.place(x=self.window_width//2 - label.winfo_reqwidth()//2, y=10)
        
    def frame_start_place(self):
        x1 = self.window_width//8
        x2 = 4*self.window_width//8
        y1 = self.window_height//8 + 30
        y2 = 2*self.window_height//8 + 30
        self.label_name.place(x=x1, y=y1)
        self.entry_name.place(x=x1+50, y=y1, height=26, width=120)
        self.label_age.place(x=x1, y=y2)
        self.entry_age.place(x=x1+50, y=y2, height=26, width=120)
        self.label_sex.place(x=x2, y = y1)
        self.option_menu_sex.place(x=x2+110, y = y1-6)
        self.label_hand.place(x=x2, y = y2)
        self.option_menu_hand.place(x=x2+110, y = y2-6)
        self.button_save.place(x = self.window_width//2 - self.button_save.winfo_reqwidth()//2, 
                               y = self.window_height//2 - self.button_save.winfo_reqheight()//2+15)
        self.button_continue_start.place(x = self.window_width//2 - self.button_continue_start.winfo_reqwidth()//2, 
                               y = 3*self.window_height//4 - self.button_continue_start.winfo_reqheight()//2)
        # add the frame to the window
        self.frame_start.place(relheight=1, relwidth=1)

    def frame_test_place(self):
        x_label1 = 2*self.window_width//8 - self.label_vibrate_lr.winfo_reqwidth()//2
        x_label2 = 4*self.window_width//8 - self.label_vibrate_ud.winfo_reqwidth()//2
        x_label3 = 6*self.window_width//8 - self.label_vibrate_lr.winfo_reqwidth()//2
        x_label4 = 4*self.window_width//8 - self.label_continue.winfo_reqwidth()//2        
        x1 = 2*self.window_width//8 - self.button_vibrate_lr.winfo_reqwidth()//2
        x2 = 4*self.window_width//8 - self.button_vibrate_ud.winfo_reqwidth()//2
        x3 = 6*self.window_width//8 - self.button_vibrate_ci.winfo_reqwidth()//2
        y1 = 3*self.window_height//8 - self.label_vibrate_lr.winfo_reqheight()//2+10
        y2 = 4*self.window_height//8 - self.button_vibrate_ci.winfo_reqheight()//2
        y3 = 6*self.window_height//8 - self.button_vibrate_ci.winfo_reqheight()//2
        self.label_vibrate_lr.place(x = x_label1, y = y1)
        self.label_vibrate_ud.place(x = x_label2, y = y1)
        self.label_vibrate_ci.place(x = x_label3, y = y1)
        self.label_continue.place(x = x_label4, y = y3-23)
        self.button_vibrate_lr.place(x = x1, y = y2)
        self.button_vibrate_ud.place(x = x2, y = y2)
        self.button_vibrate_ci.place(x = x3, y = y2)
        self.button_continue_test.place(x = x2, y = y3)
        # add the frame to the window
        self.frame_test.place(relheight=1, relwidth=1)

    def frame_response_place(self):
        x_label1 = 2*self.window_width//8 - self.label_response_lr.winfo_reqwidth()//2
        x_label2 = 4*self.window_width//8 - self.label_response_lr.winfo_reqwidth()//2
        x_label3 = 6*self.window_width//8 - self.label_response_lr.winfo_reqwidth()//2
        x1 = 2*self.window_width//8 - self.button_response_lr.winfo_reqwidth()//2
        x2 = 4*self.window_width//8 - self.button_response_ud.winfo_reqwidth()//2
        x3 = 6*self.window_width//8 - self.button_response_ci.winfo_reqwidth()//2
        y1 = 3*self.window_height//8 - self.label_response_lr.winfo_reqheight()//2+10
        y2 = 4*self.window_height//8 - self.button_response_ci.winfo_reqheight()//2
        y3 = 6*self.window_height//8 - self.button_response_ci.winfo_reqheight()//2
        self.label_response_lr.place(x = x_label1, y = y1)
        self.label_response_ud.place(x = x_label2, y = y1)
        self.label_response_ci.place(x = x_label3, y = y1)
        self.button_response_lr.place(x = x1, y = y2)
        self.button_response_ud.place(x = x2, y = y2)
        self.button_response_ci.place(x = x3, y = y2)
        # add the frame to the window
        self.frame_respond.place(relheight=1, relwidth=1)

    def action_save_data(self):
        # save the user's data
        self.name = self.entry_name.get()
        self.age = self.entry_age.get()
        self.hand = self.option_hand_selected.get()
        self.sex = self.option_sex_selected.get()
        
    def action_continue_start(self):
        # start the next frame
        self.show_frame(self.frame_test)

    def action_vibrate(self, vibration_pattern = None):
        # show the vibrat frame always
        self.show_frame(self.frame_vibrate)
        # if a pattern was received, send it to the device for testing in the half-open position of the covers
        if vibration_pattern:
            threading.Thread(target = lambda: self.send2device(vibration_pattern, "fc", self.frame_test)).start()
        # if no pattern was received, send the random patterns in their order
        else:
            threading.Thread(target = lambda: self.send2device(self.vibration_patterns[self.vibration_command_ind], 
                                                       self.cover_positions[self.cover_postion_ind], self.frame_respond)).start()
            
    def action_continue_test(self):
        # start the next frame
        self.show_frame(self.frame_vibrate)
        # start the experiment
        self.action_vibrate()

    def action_save_response(self, response):
        # save new data
        self.vibration_responses.append(response)
        self.cover_references.append(self.cover_positions[self.cover_postion_ind])
        self.vibration_references.append(self.vibration_patterns[self.vibration_command_ind])
        
        # save the response time
        self.time_responses.append(time.time() - self.time_waiting_start)

        # move to the next pattern in the vibration patterns
        self.vibration_command_ind = (self.vibration_command_ind + 1)%len(self.vibration_patterns)
        # once we finished the list of vibrations for one cover level, move to the next
        if self.vibration_command_ind == 0:
            self.cover_postion_ind +=1
            # check if the experiment is done
            if self.cover_postion_ind == 3:
                self.terminate()
                return # so we do not proceed in the function
        
        # move to the next frame
        self.show_frame(self.frame_vibrate)
        self.action_vibrate()

    def show_frame(self, frame):
        frame.tkraise()
        frame.focus_set()
        # update the window before the end of the function
        self.my_window.update()

    def send2device(self, vibration, position, frame_previous):
        # send to the device and recieve when it is done
        print("vibrating")
        time.sleep(0.5)
        # calc the position based on the state chosen fc, ho, fo
        angle = self.calc_angle(position)+30 # send with an offset +30 not to operate on the edge of the servo motor (angle = 0)
        # send data by serial
        ser = serial.Serial("COM9", 115200)
        ser.write(f"{vibration},{round(angle)}".encode())
        while True:
            if ser.in_waiting > 0:
                print("finished")
                break
        ser.close()
        # print(angle)
        # save the time when the pattern was stopped
        self.time_waiting_start = time.time()
        # returning back to the past frame
        self.show_frame(frame_previous)

    def calc_angle(self, position):
        gear_diameter = 13 #mm
        distance_max = 6 #mm for each cover
        scale = self.cover_positions.index(position)/(len(self.cover_positions) - 1) # gives either 0, 0.5 or 1
        distance = distance_max * scale
        angle = distance/(gear_diameter/2) # in rad
        angle = angle*180/np.pi # in deg

        return angle

    def terminate(self):
        # save data
        np.savez(f"{self.directory}\\{self.name}_{time.time()}.npz", 
                 name = self.name, age = self.age, hand = self.hand, sex = self.sex, 
                 cover_references = self.cover_references,
                 vibration_references = self.vibration_references, 
                 vibration_responses = self.vibration_responses, 
                 time_responses = self.time_responses)
        
        # close the window
        messagebox.showinfo("DONE!", "Thank you for participating in the experiment!")
        self.my_window.destroy()


if __name__=="__main__":
    user = User_Study()
