import csv
import time
import MCP4725
import smbus2
import numpy as np
from scipy.interpolate import interp1d

class Player():
  def __init__(self):
    self.dac = MCP4725.MCP4725()

  def play(self):
    fileName = 'data_2024-02-23.csv'
    data = np.genfromtxt(fileName, delimiter=',', skip_header=1)
    print(data.shape)

    interp_func = interp1d(data[:, 0], data[:, 1], kind='linear')
    new_x = np.linspace(np.min(data[:, 0]), np.max(data[:, 0]), num=data.shape[0]*5)
    new_y = interp_func(new_x)
    interp_data = np.column_stack((new_x, new_y))
    print(interp_data.shape)

    start_ms=time.time()

    for i in range(interp_data.shape[0]):
      while True:
        t0=time.time()
        passed_ms = (time.time() - start_ms) * 1000
        if (passed_ms >= interp_data[i][0]):
          break
      
        voltage_mV = interp_data[i][1]       
        voltage_V = voltage_mV / 1000.0
        dac_value = int((voltage_V / 5.0) * 4095)
        dac_value = max(0, min(4095, dac_value))
        self.dac.write(dac_value)
        #print(1/(time.time()-t0))

player=Player()
player.play()