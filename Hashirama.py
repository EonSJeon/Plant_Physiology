import ADS1115
import MCP4725
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import RPi.GPIO as GPIO
import datetime
import csv
import threading
import numpy as np

__all__=['Hashirama']

START_BTN = 11
END_BTN = 13

class Hashirama:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Hashirama, cls).__new__(cls)
            # Initialization only happens once
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        self.adc = ADS1115.ADS1115()  
        self.adc.setADCConfig(sps=860)
        self.dac = MCP4725.MCP4725()  
        
        self.saving = False
        self.running = False
        self.record_start_time = 0
        
        self.saved_t = np.array([])
        self.saved_y = np.array([])
        
        self.sampled_t = np.array([])
        self.sampled_y = np.array([])
        
        self.display_len = 30
        self.fig, self.ax = plt.subplots()
        self.ax.set_ylim([0, 5000])
        self.line, = self.ax.plot(list(range(0, self.display_len)), [0] * self.display_len)
        
        interval = 200  # Define the interval for animation update
        animation.FuncAnimation(self.fig, self.animate, interval=interval, blit=False)
        plt.show()
        
        data_collection_thread = threading.Thread(target=self.collect_data, daemon=True)
        data_collection_thread.start()
        

    def animate(self, i):
        if len(self.sampled_y) >= self.display_len and self.running:
            display_xs = self.sampled_t[-self.display_len:]
            display_ys = self.sampled_y[-self.display_len:]
            
            self.line.set_xdata(display_xs)
            self.line.set_ydata(display_ys)
            
            self.ax.set_xlim(min(display_xs), max(display_xs))
            self.ax.autoscale_view(scalex=False, scaley=True) 
        
        return self.line,
    
    #Something
    def collect_data(self):
        while True:  # Use a condition to make this stoppable
            ct = time.time()
            y = self.adc.read()
            self.sampled_t = np.append(self.sampled_t, (ct-self.record_start_time)*1000)
            self.sampled_y = np.append(self.sampled_y, y)
            if self.saving:
                self.saved_t = np.append(self.saved_t, (ct-self.record_start_time)*1000)
                self.saved_y = np.append(self.saved_y, y)
            
    def initButton(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup([START_BTN, END_BTN], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(START_BTN, GPIO.RISING, callback=lambda channel: self.start_saving(), bouncetime=200)
        GPIO.add_event_detect(END_BTN, GPIO.RISING, callback=lambda channel: self.end_saving(), bouncetime=200)
        
    def start_saving(self):
        self.record_start_time = time.time()
        print("Starting to save data")
        self.saving = True
        self.saved_t = np.array([])
        self.saved_y = np.array([])

    def end_saving(self):
        self.saving = False
        filename = "data_{}.csv".format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))  # Programmatically generate filename
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Time (ms)", "Voltage (mV)"])
            writer.writerows(np.column_stack((self.saved_t, self.saved_y)))
        print(f"Saved data to {filename}")
        self.saved_t = np.array([])
        self.saved_y = np.array([])