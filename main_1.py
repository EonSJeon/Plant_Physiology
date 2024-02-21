import ADS1115
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import smbus2
import RPi.GPIO as GPIO
import datetime
import csv

# Button Event Setting
__GPIO_BUTTON_START__ = 11
__GPIO_BUTTON_FINISH__ = 13

GPIO.setmode(GPIO.BOARD)
GPIO.setup([__GPIO_BUTTON_START__, __GPIO_BUTTON_FINISH__], GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize placeholders
save_data = False  # Flag to control data saving
data = []  # List to hold the data

# Callback functions for GPIO button events
def startDataCollecting(channel):
    global save_data
    print("Starting to save data")
    save_data = True


def finishDataCollecting(channel):
    global save_data, data
    filename = "data_{0}.csv".format(datetime.date.today())
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Time (ms)", "Voltage (mV)"])  # Write header
        writer.writerows(data)
    print("Saved data")
    data = []  # Clear data after saving
    save_data = False

# Setup GPIO event detection
GPIO.add_event_detect(__GPIO_BUTTON_START__, GPIO.RISING, callback=startDataCollecting, bouncetime=200)
GPIO.add_event_detect(__GPIO_BUTTON_FINISH__, GPIO.RISING, callback=finishDataCollecting, bouncetime=200)

# Initialize the ADS1115 ADC
ads = ADS1115.ADS1115()
ads.setADCConfig(sps=860)

# Plotting setup
x_len = 30
y_range = [0, 5000]
fig, ax = plt.subplots()
xs = list(range(0, x_len))
ys = [0] * x_len
ax.set_ylim(y_range)
line, = ax.plot(xs, ys)
start_time = time.time()
interval=1000

# Animation function
def animate(i, ys):
    global data
    ys=[]
    t0=time.time()
    while(time.time()-t0<=1e-3*interval):
        volt = ads.read()
        x_val = (time.time() - start_time) * 1000
        
        if save_data:
            data.append([x_val, volt])
            
        ys.append(volt)
        
    xs = list(range(0, len(ys)))
    line.set_xdata(xs)
    line.set_ydata(ys)
    ax.relim()  # Recalculate limits
    ax.autoscale_view(True,True,True)  # Rescale the view based on the current data
    return line,



ani = animation.FuncAnimation(fig, animate, fargs=(ys,), interval=interval, blit=True)
plt.show()

# Create FuncAnimation as before but remove fargs as it's not needed
ani = animation.FuncAnimation(fig, animate, interval=interval, blit=True)

plt.show()


##############################################################################


#############################################################################

# while True:
#     t0=time.time()
#     volt=ads.readADC()
#     print(1/(time.time()-t0))

# while True:
#     animate(ys)


# import ADS1115
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
# import time
# import pandas as pd
# import smbus2
# import RPi.GPIO as GPIO
# import datetime
# import csv

# # Button Event Setting
# __GPIO_BUTTON_START__=11
# __GPIO_BUTTON_FINISH__=13

# GPIO.setmode(GPIO.BOARD)
# GPIO.setup([__GPIO_BUTTON_START__,__GPIO_BUTTON_FINISH__], GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.add_event_detect(__GPIO_BUTTON_START__, GPIO.RISING, callback=startDataCollecting)
# GPIO.add_event_detect(__GPIO_BUTTON_FINISH__, GPIO.RISING, callback=finishDataCollecting)

# def startDataCollecting():
#     global save_data
#     print("starting to save data")
#     save_data=True

# def finishDataCollecting():
#     global save_data
#     global df
#     df = pd.DataFrame.from_dict(data)
#     df.to_csv("data_{0}.csv".format(datetime.date.today()),index=False)
#     print("Saved data")
#     save_data=False
        


# # are we saving data right now
# save_data=False

# # Initialize the ADS1115 ADC
# ads = ADS1115.ADS1115()
# ads.setADCConfig(sps=860)

# # Number of data points
# x_len = 30
# y_range = [0, 5000]

# # Create figure for plotting
# fig, ax = plt.subplots()
# xs = list(range(0, x_len))
# ys = [0] * x_len
# ax.set_ylim(y_range)

# # Create a line, which we will update with new data
# line, = ax.plot(xs, ys)
# start_time = time.time()

# #create pandas object
# data={"Time":[],"Voltage (mV)":[]}


# # Set up plot to call animate() function periodically (every 1 ms, this is probably limiting our sampling frequency as well)
# ani = animation.FuncAnimation(fig, animate, fargs=(ys,), interval=.01, blit=True)
# plt.show()

# def animate(i, ys):
#     # Read voltage from ADS1115
#     volt = ads.readADC()
#     x_val=start_time-time.time()

#     # Add y to list
#     ys.append(volt)
#     if(save_data):
#         data["Time"].append(x_val)
#         data["Voltage (mV)"].append(volt)

#     # Limit y list to set number of items
#     ys = ys[-x_len:]

#     # Update line with new Y values
#     line.set_ydata(ys)
#     print(save_data)
#     return line,





    
    
    
    

