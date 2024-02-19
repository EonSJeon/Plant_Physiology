import ADS1115
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Initialize the ADS1115 ADC
ads = ADS1115.ADS1115()

# Number of data points
x_len = 30
y_range = [0, 5000]

# Create figure for plotting
fig, ax = plt.subplots()
xs = list(range(0, x_len))
ys = [0] * x_len
ax.set_ylim(y_range)

# Create a line, which we will update with new data
line, = ax.plot(xs, ys)

# Define a function for the animation
def animate(i, ys):
    # Read voltage from ADS1115
    volt = ads.readADCSingleEnded()
    print("{:.0f} mV measured on AN0".format(volt))

    # Add y to list
    ys.append(volt)

    # Limit y list to set number of items
    ys = ys[-x_len:]

    # Update line with new Y values
    line.set_ydata(ys)

    return line,

# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(fig, animate, fargs=(ys,), interval=100, blit=True)
plt.show()
