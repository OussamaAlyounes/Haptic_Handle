import numpy as np
import os
import time
import tkinter as tk

    
sigma_T = np.arange(10)*10

text_pose_y_ind = np.where(sigma_T > np.max(sigma_T)*0.7)[0][0]
print(text_pose_y_ind)

