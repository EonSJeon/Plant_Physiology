import Devices.ADS1115 as ADS1115
import time
import datetime
import csv
import numpy as np
import UI
import tkinter as tk
from tkinter import simpledialog
import csv

class Recorder():
    def __init__(self):
        print("Init Recorder")
        self.adc=ADS1115.ADS1115()
        self.adc.setADCConfig(sps=860)
        
        self.max_sampled=5000
        
        self.data_stream=np.empty((0,2))
        self.save_stream=np.empty((0,2))
        
        self.record_start_time = 0
        self.saving = False
        
        self.ui=UI.UI(self)
        print("Recorder Init Ends")
        
    def collect_data(self):
        while True:
            
            ct_ms = time.time()*1000
            print(ct_ms)
            y = self.adc.read()
            
            new_sample=np.array([ct_ms, y])
            
            self.data_stream=np.row_stack((self.data_stream, new_sample))
            if self.saving:
                self.save_stream=np.row_stack((self.save_stream, new_sample))

            
    
    def start_saving(self):
        self.record_start_time = time.time()
        self.saving = True
        self.saved_t = np.array([])
        self.saved_y = np.array([])
        
        print("Starting to save data")

    def end_saving(self):
        self.saving = False
        self.save(self.saved_t, self.saved_y)
        
        self.save_stream=np.empty((0,2))

        
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


