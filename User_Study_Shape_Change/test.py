import os
import sys
import time
import numpy as np
import datetime
import tkinter as tk
from tkinter import Entry
import matplotlib.pyplot as plt
import serial

ser = serial.Serial("COM5", 9600)