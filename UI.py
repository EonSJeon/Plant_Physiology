import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Polygon
import numpy as np
import time

# Should be moved once ready
import tkinter as tk
from tkinter import simpledialog
import datetime
import csv

class UI():
    def __init__(self, recorder):
        self.parent = recorder
        self.paused=False
        self.window_len = 100
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [])
        
        self.t_max_width=1e4
        self.y_max_width=1e5
        
        self.display_ts = np.zeros(self.window_len)
        self.display_ys = np.zeros(self.window_len)
        
        self.click_count=0
        
        self.start_line=None
        self.end_line=None
        self.poly=None
        
        self.anim = animation.FuncAnimation(self.fig, self.animate, interval=200)
        
        
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('button_release_event', self.on_button_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        
        self.prev_x_lim = self.ax.get_xlim()
        self.prev_y_lim = self.ax.get_ylim()
        
        # Connect to axes limit change events
        self.ax.callbacks.connect('xlim_changed', self.on_xlim_changed)
        self.ax.callbacks.connect('ylim_changed', self.on_ylim_changed)
        
        self.dragging = False
    

    def animate(self, i):
        if not self.paused:
            offset_sampled_t = self.parent.sampled_t
            sampled_y = self.parent.sampled_y
            
            display_len=min(len(sampled_y),self.window_len)
             
            sampled_t = np.array(offset_sampled_t) - max(offset_sampled_t)
            self.display_ts = sampled_t[-display_len:]
            self.display_ys = sampled_y[-display_len:]
            self.line.set_data(self.display_ts, self.display_ys)

    def autoscale(self):
        # Check if there's enough data to perform FFT
        if len(self.parent.sampled_t) < 2 or len(self.parent.sampled_y) < 2:
            return

        # Perform FFT on the signal
        fft_result = np.fft.fft(self.parent.sampled_y)
        fft_freq = np.fft.fftfreq(len(self.parent.sampled_y), d=self.parent.sampled_t[1] - self.parent.sampled_t[0])

        # Calculate magnitude spectrum and ignore DC component
        magnitude_spectrum = np.abs(fft_result)
        dominant_frequency_index = np.argmax(magnitude_spectrum[1:]) + 1  # Find index of dominant frequency
        dominant_frequency = np.abs(fft_freq[dominant_frequency_index])  # Get the dominant frequency

        # Adjust scales based on FFT analysis
        if dominant_frequency > 0:
            # Set horizontal scale to show 5 cycles of dominant frequency
            cycle_time = 1 / dominant_frequency
            horizontal_span = 5 * cycle_time
        else:
            # If no dominant frequency, use the entire time range of sampled_t
            horizontal_span = self.parent.sampled_t[-1] - self.parent.sampled_t[0]

        # Set vertical scale based on amplitude range
        amplitude_center = (max(self.parent.sampled_y) + min(self.parent.sampled_y)) / 2
        vertical_span = max(self.parent.sampled_y) - min(self.parent.sampled_y)

        # Apply calculated scales to axes, adjusting view to the left of the latest data
        self.ax.set_xlim(-2 * horizontal_span, -horizontal_span)
        self.ax.set_ylim(amplitude_center - vertical_span, amplitude_center + vertical_span)

        plt.draw()


    def on_key_press(self, event):
        if event.key == 'ctrl+a':
            self.autoscale()
            plt.draw()
        
        elif event.key ==' ':
            if self.paused:
                self.erase_marks()
            self.paused=not self.paused
        elif event.key == 'ctrl+alt+s':
            if self.paused and self.poly is not None:
                start_line_t=self.start_line.get_xdata()[0]
                end_line_t=self.end_line.get_xdata()[0]
                
                start_index = np.argmin(np.abs(self.display_ts - start_line_t))
                end_index = np.argmin(np.abs(self.display_ts - end_line_t))
                
                save_t=self.display_ts[start_index:end_index+1]
                save_y=self.display_ys[start_index:end_index+1]
                
                self.save(save_t,save_y)
            
    def on_scroll(self, event):
        xdata, ydata = event.xdata, event.ydata  
        if not xdata or not ydata: 
            return
        
        base_scale = 1.1
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()

        if event.button == 'up':
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            scale_factor = base_scale
        else:
            return

        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor


        relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
        
        self.ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
        self.ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])


        plt.draw()
        

    def on_click(self, event):
        if self.fig.canvas.toolbar.mode=='' and self.paused:
            if event.button==1 and event.inaxes is not None:
                self.erase_marks()
                self.start_line = self.ax.axvline(x=event.xdata, color='black', alpha=0, zorder=4)
                self.click_count=1
                self.dragging=True
                self.fig.canvas.draw()   
            else:
                print('Clicked outside axes bounds but inside plot window')
    
    def on_button_release(self,event):
        if self.fig.canvas.toolbar.mode=='' and self.paused and self.dragging and event.button==1:
            self.start_line.set_alpha(1)
            
            end_line_t=event.xdata
            self.end_line=self.ax.axvline(x=end_line_t, color='black', alpha=1, zorder=4)
            
            self.fig.canvas.draw()
            self.dragging=False
    
    def on_motion(self, event):
        if self.fig.canvas.toolbar.mode=='' and self.paused and self.dragging:
            if event.inaxes is not None:
                start_line_t = self.start_line.get_xdata()[0]
                end_line_t = event.xdata
                if start_line_t != end_line_t:
                    # Define the new points for the polygon
                    new_points = [(start_line_t,  self.y_max_width),
                                  (start_line_t, -self.y_max_width),
                                  (  end_line_t, -self.y_max_width),
                                  (  end_line_t,  self.y_max_width)]
                    if self.poly is None:
                        # If the polygon doesn't exist, create it
                        self.poly = Polygon(new_points, color='black', alpha=0.5, zorder=3)
                        self.ax.add_patch(self.poly)  # Add the polygon to the axes
                    else:
                        # If the polygon exists, update its points
                        self.poly.set_xy(new_points)
                    self.fig.canvas.draw()
            else:
                self.erase_marks()
                self.dragging=False

            
    def on_xlim_changed(self, event=None):
        current_t_lim = self.ax.get_xlim()
        w = current_t_lim[1] - current_t_lim[0]  
        
        if w > self.t_max_width:
            w = self.t_max_width

        left_lim = max(current_t_lim[0], -self.t_max_width)
        right_lim = min(left_lim + w, 0)

        if (left_lim, right_lim) != current_t_lim:
            self.ax.set_xlim([left_lim, right_lim])
        else:
            self.prev_x_lim = current_t_lim
        
        current_t_min=self.ax.get_xlim()[0]
        offset_sampled_t = self.parent.sampled_t
        sampled_t = np.array(offset_sampled_t) - max(offset_sampled_t)
        self.window_len=len(sampled_t)-abs(np.argmin(np.abs(sampled_t-current_t_min)))


    def on_ylim_changed(self, event=None):
        current_y_lim = self.ax.get_ylim()
        h = current_y_lim[1] - current_y_lim[0]
        
        if h > self.y_max_width:
            h = self.y_max_width

        bottom_lim = max(current_y_lim[0], -self.y_max_width/2)

        if bottom_lim + h > self.y_max_width/2:
            bottom_lim = self.y_max_width/2 - h

        top_lim = bottom_lim + h

        if (bottom_lim, top_lim) != current_y_lim:
            self.ax.set_ylim([bottom_lim, top_lim])
        else:
            self.prev_y_lim = current_y_lim

    def erase_marks(self):
        if self.start_line is not None:
            self.start_line.remove()
            del self.start_line
            self.start_line=None
        if self. end_line is not None:
            self.end_line.remove()
            del self.end_line
            self.end_line=None
        if self.poly is not None:
            self.poly.remove()
            del self.poly
            self.poly=None
            
            
            
    ###########################################################################
    # Should be moved to Recorder once ready
    def save(self, ts, ys):
        # Generate the default filename
        default_filename = "data_{}.csv".format(datetime.datetime.now().strftime("%Y-%m-%d"))
        
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




    