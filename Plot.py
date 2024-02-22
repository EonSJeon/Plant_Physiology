import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Polygon
import numpy as np

# Should be moved once ready
import tkinter as tk
from tkinter import simpledialog
import datetime
import csv

class Plot():
    def __init__(self, recorder):
        self.parent = recorder
        self.paused=False
        self.display_len = 100
        self.fig, self.ax = plt.subplots()
        self.ax.set_ylim([-1, 1])
        self.line, = self.ax.plot([], [])
        
        self.tmax=1e5
        self.ymax=1e5
        
        self.display_ts = np.zeros(self.display_len)
        self.display_ys = np.zeros(self.display_len)
        
        self.click_count=0
        
        self.start_line=None
        self.end_line=None
        self.poly=None
        
        self.anim = animation.FuncAnimation(self.fig, self.animate, interval=200)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
    
    def animate(self, i):
        if not self.paused:
            offset_sampled_t = self.parent.sampled_t
            sampled_y = self.parent.sampled_y

            if len(sampled_y) >= self.display_len:
                sampled_t = np.array(offset_sampled_t) - min(offset_sampled_t)
                self.display_ts = sampled_t[-self.display_len:]
                self.display_ys = sampled_y[-self.display_len:]
                self.line.set_data(self.display_ts, self.display_ys)

    def autoscale(self):
        th=max(self.display_ts); tl=min(self.display_ts)
        tw=th-tl; tc=(th+tl)/2
        yh=max(self.display_ys); yl=min(self.display_ys)
        yw=yh-yl; yc=(yh+yl)/2
        
        self.ax.set_xlim(tc-tw/6,tc+tw/6)
        self.ax.set_ylim(yc-yw,yc+yw)

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
                
                start_save_t=min(start_line_t,min(self.display_ts))
                end_save_t=max(end_line_t,max(self.display_tx))
                
                self.save(self.display_ts,self.display_ys)
            
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
        if self.paused:
            if event.button==1 and event.inaxes is not None:
                if self.click_count==0:
                    self.erase_marks()
                    self.start_line = self.ax.axvline(x=event.xdata, color='red')
                    self.click_count=1
                elif self.click_count==1:
                    start_line_t=self.start_line.get_xdata()[0]
                    if(event.xdata>start_line_t):
                        end_line_t=event.xdata
                        self.end_line = self.ax.axvline(x=end_line_t, color='blue')
                        self.poly = Polygon([(start_line_t,  self.ymax), \
                                             (start_line_t, -self.ymax), \
                                             (  end_line_t, -self.ymax), \
                                             (  end_line_t,  self.ymax)], 
                                             color='0.9', alpha=0.5)
                        self.ax.add_patch(self.poly)
                        self.click_count=0
                    else:
                        self.erase_marks()
                        self.start_line = self.ax.axvline(x=event.xdata, color='red')
                else:
                    print(f"Something Error: self.click_count({self.click_count}) exceeds two.")
                    return
                self.fig.canvas.draw()
            else:
                print('Clicked outside axes bounds but inside plot window')
                
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

        # Ask the user for a filename, with the default name pre-filled
        filename = simpledialog.askstring("Save File", "Enter filename:", initialvalue=default_filename)
        
        # If the user didn't cancel the dialog
        if filename:
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Time (ms)", "Voltage (mV)"])
                writer.writerows(np.column_stack((ts, ys)))



    