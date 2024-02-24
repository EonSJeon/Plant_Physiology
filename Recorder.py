import ADS1115
import time
import RPi.GPIO as GPIO
import datetime
import csv
import numpy as np
import UI
import tkinter as tk
from tkinter import simpledialog
import datetime
import csv

class Recorder():
    def __init__(self):
        print("Init Recorder")
        self.adc=ADS1115.ADS1115()
        self.adc.setADCConfig(sps=860)
        
        self.max_sampled=5000

        self.sampled_t = np.array([])
        self.sampled_y = np.array([])
        
        self.saved_t = np.array([])
        self.saved_y = np.array([])
        self.record_start_time = 0
        self.saving = False
        
        self.ui=UI.UI(self)
        print("Recorder Init Ends")
        
    def collect_data(self):
        while True:
            
            ct = time.time()
            y = self.adc.read()
            
            self.sampled_t = np.append(self.sampled_t, ct*1000)
            self.sampled_y = np.append(self.sampled_y, y)
            if self.saving:
                self.saved_t = np.append(self.saved_t, (ct-self.record_start_time)*1000)
                self.saved_y = np.append(self.saved_y, y)
            
    
    def start_saving(self):
        self.record_start_time = time.time()
        self.saving = True
        self.saved_t = np.array([])
        self.saved_y = np.array([])
        
        print("Starting to save data")

    def end_saving(self):
        self.saving = False
        self.save(self.saved_t, self.saved_y)
        
        self.saved_t = np.array([])
        self.saved_y = np.array([])
        
        print(f"Saved data to {filename}")
        
    def save(self, ts, ys):
        # Generate the default filename
        default_filename = "data_{}.csv".format(datetime.datetime.now().strftime("%Y-%m-%d"))
        
        ts=ts-min(ts)
        
        # Initialize Tkinter root widget
        root = tk.Tk()
        root.withdraw()  # Hide the root window

        is_valid = False
        
        while not is_valid:
            # Ask the user for a filename, with the default name pre-filled
            filename = simpledialog.askstring("Save File", "Enter filename:", initialvalue=default_filename)
            
            # Check if the dialog was canceled
            if not filename:
                print("Save operation canceled.")
                return
            
            # Check for invalid characters and length
            invalid_chars = '<>:"/\\|?*'
            if any(char in invalid_chars for char in filename):
                tk.messagebox.showerror("Invalid Filename", "Filename contains invalid characters. Please try again.")
            elif len(filename) > 255:  # Adjust based on your OS constraints
                tk.messagebox.showerror("Invalid Filename", "Filename is too long. Please try again.")
            else:
                # Ensure filename ends with .csv
                if not filename.lower().endswith(".csv"):
                    filename += ".csv"
                is_valid = True

        if is_valid:
            # Proceed with file saving
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Time (ms)", "Voltage (mV)"])
                writer.writerows(np.column_stack((ts, ys)))
                print(f"Data successfully saved to {filename}.")


