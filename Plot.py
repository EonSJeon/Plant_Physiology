import matplotlib.pyplot as plt
import matplotlib.animation as animation


class Plot():
    def __init__(self, recorder):
        self.parent = recorder
        self.display_len = 100
        self.fig, self.ax = plt.subplots()
        self.ax.set_ylim([-1, 1])
        self.line, = self.ax.plot([], [])
        self.anim = animation.FuncAnimation(self.fig, self.animate, interval=200)
        #mplcursors.cursor(hover=True)
        print("in5")
        
    
    def animate(self, i):
        sampled_t = self.parent.sampled_t
        sampled_y = self.parent.sampled_y
        if len(sampled_y) >= self.display_len:
            display_xs = sampled_t[-self.display_len:]
            display_ys = sampled_y[-self.display_len:]
            self.line.set_data(display_xs, display_ys)
            #self.ax.set_xlim(min(display_xs), max(display_xs))
            #self.ax.relim()
            #self.ax.autoscale_view(scalex=True, scaley=True)
