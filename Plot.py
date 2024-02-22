import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Polygon
import numpy as np


class Plot():
    def __init__(self, recorder):
        self.parent = recorder
        self.paused=False
        self.display_len = 100
        self.fig, self.ax = plt.subplots()
        self.ax.set_ylim([-1, 1])
        self.line, = self.ax.plot([], [])
        
        self.tmax=1e9
        self.ymax=1e9
        
        self.display_ts = np.zeros(self.display_len)
        self.display_ys = np.zeros(self.display_len)
        
        self.lines=[]
        self.click_count=0
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
            self.paused=False if self.paused else True
            
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
                self.click_count += 1
                color = 'red' if self.click_count % 2 != 0 else 'blue'
                line = self.ax.axvline(x=event.xdata, color=color)
                self.lines.append((event.xdata, line))

                if len(self.lines) == 2:
                    x_values = [self.lines[0][0], self.lines[1][0]]
                    poly = Polygon([(x_values[0], self.ymax ), \
                                    (x_values[0], -self.ymax), \
                                    (x_values[1], -self.ymax), \
                                    (x_values[1], self.ymax)], 
                                    color='0.9', alpha=0.5)
                    self.ax.add_patch(poly)
                    self.fig.canvas.draw()

                    # Reset for the next pair of lines
                    self.lines = []
            else:
                print('Clicked outside axes bounds but inside plot window')


    