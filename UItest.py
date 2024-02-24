import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import time
import UI
from math import sin, pi


class Recorder():
    def __init__(self):
        self.A = 100
        self.num_points = 10000
        self.data_stream = np.empty((0, 2))

    def start_saving(self):
        print("start saving")
        
    def update_data(self):
        

        # Generate new sample based on sine wave
        t=time.time()
        new_sample_y = self.A * sin(2 * pi * t)  # Example: sine wave with period of 1 second
        new_sample = np.array([t*10, new_sample_y])

        # Update sampled_data with new_sample
        self.data_stream = np.row_stack((self.data_stream, new_sample))


def data_updater(recorder):
    while True:
        recorder.update_data()
        #time.sleep(0.00001)



testRec = Recorder()
ui = UI.UI(testRec)

update_thread = threading.Thread(target=data_updater, args=(testRec,))
update_thread.daemon = True  # This ensures the thread stops when the main program ends
update_thread.start()

plt.show()



    


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
