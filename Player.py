import tkinter as tk
from tkinter import filedialog
import numpy as np
from scipy.interpolate import interp1d
import time
# import MCP4725
# Make sure to import or define MCP4725 class correctly

class Player():
    def __init__(self):
      pass
        # self.dac = MCP4725.MCP4725()
    
    def select_the_file(self):
      fileName = filedialog.askopenfilename(title='Select a data file', filetypes=[('CSV files', '*.csv')])
      if not fileName:
          print("No file selected.")
          return None
      return fileName
    
    
    def interpolate(self, data, N):
      interp_func = interp1d(data[:, 0], data[:, 1], kind='linear')
      new_x = np.linspace(np.min(data[:, 0]), np.max(data[:, 0]), num=int(data.shape[0]*N))
      new_y = interp_func(new_x)
      interp_data = np.column_stack((new_x, new_y))
      return interp_data

    def play_file(self, fileName, N):
      if fileName is None:
          return
      data = np.genfromtxt(fileName, delimiter=',', skip_header=1)
      self.play_data(data, N)

    def play_data(self, data, N):
        if not (data.shape[0]>0 and data.shape[1]==2):
          print("The data format is wrong")

        data = self.interpolate(data, N)
        
        start_ms = time.time()
        for i in range(data.shape[0]):
            while True:
                passed_ms = (time.time() - start_ms) * 1000
                if passed_ms >= data[i, 0]:
                    break

            voltage_mV = data[i, 1]
            voltage_V = voltage_mV / 1000.0
            dac_value = int((voltage_V / 5.0) * 4095)
            dac_value = max(0, min(4095, dac_value))
            # self.dac.set_voltage(dac_value)  # Ensure this method correctly communicates with your DAC

player = Player()
player.play_data()
