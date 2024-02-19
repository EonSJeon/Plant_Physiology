import time
import smbus2
import MCP4725

dac = MCP4725.MCP4725(smbus2.SMBus(1), 0x62,smbus2)


while True:
    current=time.time()
    for x in range(0,4097,150):
        dac.write(x)
    period=time.time()-current
    freq=1/period
    print("\nFreq: %.2f\n" % freq)
        #voltage = x/4096.0*5.0
        #print("\nAnalogVolt: %.2f\n" % voltage)