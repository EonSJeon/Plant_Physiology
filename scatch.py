import matplotlib.pyplot as plt
import numpy as np


fig,ax=plt.subplots()

x = np.sin(np.linspace(0,10, 266))+1
ax.plot(x)

class Restrictor():
    def __init__(self, ax, x=lambda x: True,y=lambda x: True):
        self.res = [x,y]
        self.ax =ax
        self.limits = self.get_lim()
        self.ax.callbacks.connect('xlim_changed', lambda evt: self.lims_change(axis=0))
        self.ax.callbacks.connect('ylim_changed', lambda evt: self.lims_change(axis=1))

    def get_lim(self):
        return [self.ax.get_xlim(), self.ax.get_ylim()]

    def set_lim(self, axis, lim):
        if axis==0:
            self.ax.set_xlim(lim)
        else:
            self.ax.set_ylim(lim)
        self.limits[axis] = self.get_lim()[axis]

    def lims_change(self, event=None, axis=0):
        curlim = np.array(self.get_lim()[axis])
        if self.limits[axis] != self.get_lim()[axis]:
            # avoid recursion
            if not np.all(self.res[axis](curlim)):
                # if limits are invalid, reset them to previous state
                self.set_lim(axis, self.limits[axis])
            else:
                # if limits are valid, update previous stored limits
                self.limits[axis] = self.get_lim()[axis]

res = Restrictor(ax, x=lambda x: x>=0,y=lambda x: x>=0)

plt.show()