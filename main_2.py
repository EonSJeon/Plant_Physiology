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


# Initialize placeholders
save = False  # Flag to control data saving
saved_t = np.array([])  # List to hold the data
saved_y = np.array([])
sampled_t = np.array([])
sampled_y=np.array([])

# Initialize the ADS1115 ADC
ads = ADS1115.ADS1115()
ads.setADCConfig(sps=860)

# Plotting setup
display_len = 30
fig, ax = plt.subplots()
displayed_t = list(range(0, display_len))
displayed_y = [0] * display_len
ax.set_ylim([0, 5000])
line, = ax.plot(displayed_t, displayed_y)

prog_start_time = time.time()
record_start_time=0

interval=200

ani = animation.FuncAnimation(fig, animate, interval=interval, blit=False)
plt.show()

# Thread for collecting data from ADC
def collect_data():
    global save, sampled_t, sampled_y, saved_t, saved_y
    while True:  # Replace this with a more appropriate condition if needed
        ct= time.time()
        y = ads.read()
        sampled_t=np.append(sampled_t, (ct-prog_start_time)*1000)
        sampled_y=np.append(sampled_y, y)
        if save:
            saved_t=np.append(saved_t, (ct-record_start_time)*1000)
            saved_y=np.append(saved_y, y)


# Initialize and start the data collection thread
data_collection_thread = threading.Thread(target=collect_data, daemon=True)
data_collection_thread.start()

# Animation function modified to pull data from the queue


# Create FuncAnimation as before but remove fargs as it's not needed



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