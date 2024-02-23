
import MCP4725
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import RPi.GPIO as GPIO
import datetime
import csv
import threading
import numpy as np
import Recorder

__all__=['Hashirama']

START_BTN = 11
END_BTN = 13

class Hashirama:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Hashirama, cls).__new__(cls)
            # Initialization only happens once
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        print("Init Hashirama")        
        
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup([START_BTN, END_BTN], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(START_BTN, GPIO.RISING, \
            callback=lambda channel: self.recorder.start_saving(), bouncetime=200)
        GPIO.add_event_detect(END_BTN, GPIO.RISING, \
            callback=lambda channel: self.recorder.end_saving(), bouncetime=200)
        
        self.recorder=Recorder.Recorder()
        print("recorder init end")
        
        data_collection_thread = threading.Thread(target=self.recorder.collect_data, daemon=True)
        data_collection_thread.start()
        print("thread started")
        
        plt.show()
    
        
hashi=Hashirama()
            
