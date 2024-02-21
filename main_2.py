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
        
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup([START_BTN, END_BTN], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(START_BTN, GPIO.RISING, callback=lambda channel: self.startDataCollecting(), bouncetime=200)
        GPIO.add_event_detect(END_BTN, GPIO.RISING, callback=lambda channel: self.finishDataCollecting(), bouncetime=200)
        
        self.saving = False
        self.displaying=False
        
        self.saved_t = np.array([])
        self.saved_y = np.array([])

    def startDataCollecting(self):
        self.record_start_time = time.time()
        print("Starting to save data")
        self.saving = True
        self.saved_t = np.array([])
        self.saved_y = np.array([])

    def finishDataCollecting(self):
        self.saving = False
        filename = input("Enter the file name: ")+".csv"
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Time (ms)", "Voltage (mV)"])
            writer.writerows(np.column_stack((self.saved_t, self.saved_y)))
        print("Saved data")
        self.saved_t = np.array([])
        self.saved_y = np.array([])

    def display(self):
        pass
    
    def replay(self, fileName):
        pass
    
    def collect_data(self):
        while True:  # Replace this with a more appropriate condition if needed
            ct= time.time()
            y = ads.read()
            displayed_t=np.append(displayed_t, (ct-prog_start_time)*1000)
            displayed_y=np.append(displayed_y, y)
            if self.saving:
                saved_t=np.append(saved_t, (ct-record_start_time)*1000)
                saved_y=np.append(saved_y, y)

    

                
        




# Initialize placeholders
save = False  # Flag to control data saving
saved_t = np.array([])  # List to hold the data
saved_y = np.array([])
displayed_t = np.array([])
displayed_y=np.array([])

# Initialize the ADS1115 ADC
ads = ADS1115.ADS1115()
ads.setADCConfig(sps=860)

# Plotting setup
display_len = 30
fig, ax = plt.subplots()
xs = list(range(0, display_len))
ys = [0] * display_len
ax.set_ylim([0, 5000])
line, = ax.plot(xs, ys)

prog_start_time = time.time()
record_start_time=0

interval=200

# Thread for collecting data from ADC
def collect_data():
    global save, displayed_t, displayed_y, saved_t, saved_y
    while True:  # Replace this with a more appropriate condition if needed
        ct= time.time()
        y = ads.read()
        displayed_t=np.append(displayed_t, (ct-prog_start_time)*1000)
        displayed_y=np.append(displayed_y, y)
        if save:
            saved_t=np.append(saved_t, (ct-record_start_time)*1000)
            saved_y=np.append(saved_y, y)


# Initialize and start the data collection thread
data_collection_thread = threading.Thread(target=collect_data, daemon=True)
data_collection_thread.start()

# Animation function modified to pull data from the queue
def animate(i):
    global displayed_t, displayed_y, line
    
    # Ensure there's enough data to display
    if len(displayed_y) >= display_len:
        # Select the most recent 'display_len' data points
        display_xs = displayed_t[-display_len:]
        display_ys = displayed_y[-display_len:]
        
        # Update the line data
        line.set_xdata(display_xs)
        line.set_ydata(display_ys)
        
        # Dynamically update xlim with the new range of display_xs
        ax.set_xlim(min(display_xs), max(display_xs))
        
        # Since we're manually setting xlim, we only need to autoscale the y-axis
        # ax.relim()  # Recalculate the limits based on the current data
        ax.autoscale_view(scalex=False, scaley=True)  # Apply autoscaling to y-axis only
        
        
    return line,



# Plotting setup remains the same...

# Create FuncAnimation as before but remove fargs as it's not needed
ani = animation.FuncAnimation(fig, animate, interval=interval, blit=False)
plt.show()


################################################################################
# Buttons
# Button Event Setting
START_BTN = 11
END_BTN = 13

GPIO.setmode(GPIO.BOARD)
GPIO.setup([START_BTN, END_BTN], GPIO.IN, pull_up_down=GPIO.PUD_UP)

def startDataCollecting(channel):
    global save, record_start_time
    record_start_time=time.time()
    print("Starting to save data")
    save = True
    saved_t = np.array([]) 
    saved_y = np.array([])


def finishDataCollecting(channel):
    global save, saved_t, saved_y
    save = False
    filename = "data_{0}.csv".format(datetime.date.today())
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Time (ms)", "Voltage (mV)"])  # Write header
        writer.writerows(np.column_stack((saved_t, saved_y)))
    print("Saved data")
    saved_t = np.array([]) 
    saved_y = np.array([])
    

GPIO.add_event_detect(START_BTN, GPIO.RISING, callback=startDataCollecting, bouncetime=200)
GPIO.add_event_detect(END_BTN, GPIO.RISING, callback=finishDataCollecting, bouncetime=200)
################################################################################