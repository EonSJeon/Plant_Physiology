import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import UI
import threading
import time



class Recorder():
    def __init__(self):
        self.A=100
        self.num_points = 1000
        self.sampled_t = np.linspace(0, 100 * np.pi, self.num_points)
        self.sampled_y = self.A*np.sin(self.sampled_t)
        self.step_size = 0.1  # Amount to increment time by in each frame of the animation
    
    def update_data(self):
        # Shift the time axis by step_size to create the moving effect
        self.sampled_t += self.step_size
        # Recalculate the sine wave values
        self.sampled_y = self.A*np.sin(self.sampled_t)
        # Ensure sampled_t remains within 0 to 2*pi range
        

def data_updater(recorder):
    while True:
        recorder.update_data()
        time.sleep(0.01)  # Adjust sleep time as needed for desired update rate

# Usage

testRec = Recorder()
ui = UI.UI(testRec)
ui.autoscale()

# Create a separate thread for continuously updating the data
update_thread = threading.Thread(target=data_updater, args=(testRec,))
update_thread.daemon = True  # Set the thread as daemon so it stops when the main program ends
update_thread.start()

plt.show()  # This blocks until the plot window is closed


    
    


# # Prepare the sine wave plot
# x = np.linspace(0, 2 * np.pi, 100)
# y = np.sin(x)

# fig, ax = plt.subplots()
# ax.plot(x, y)

# click_count = 0  # To track the number of clicks
# lines = []       # To store line positions

# def on_click(event):
#     global click_count, lines
#     if event.inaxes is not None:
#         click_count += 1
#         color = 'red' if click_count % 2 != 0 else 'blue'
#         line = ax.axvline(x=event.xdata, color=color)
#         lines.append((event.xdata, line))

#         # When two lines are present, shade the area between them
#         if len(lines) == 2:
#             x_values = [lines[0][0], lines[1][0]]
#             y_values = [np.sin(x_value) for x_value in x_values]
#             poly = Polygon([(x_values[0], 0), *zip(x_values, y_values), \
    # (x_values[1], 0)], color='0.9', alpha=0.5)
#             ax.add_patch(poly)
#             fig.canvas.draw()

#             # Reset for the next pair of lines
#             lines = []
#     else:
#         print('Clicked outside axes bounds but inside plot window')

# fig.canvas.mpl_connect('button_press_event', on_click)

# plt.show()
