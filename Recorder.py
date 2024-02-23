import ADS1115
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import RPi.GPIO as GPIO
import datetime
import csv
import threading
import numpy as np
import UI

class Recorder():
    def __init__(self):
        self.adc=ADS1115.ADS1115()
        self.adc.setADCConfig(sps=860)
        
        self.sampled_t = np.array([])
        self.sampled_y = np.array([])
        
        self.saved_t = np.array([])
        self.saved_y = np.array([])
        self.record_start_time = 0
        self.saving = False
        
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
        filename = "data_{}.csv".format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))  # Programmatically generate filename
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Time (ms)", "Voltage (mV)"])
            writer.writerows(np.column_stack((self.saved_t, self.saved_y)))
        
        self.saved_t = np.array([])
        self.saved_y = np.array([])
        
        print(f"Saved data to {filename}")


