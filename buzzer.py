import RPi.GPIO as GPIO
import time
from time import sleep


class Buzzer:
    """docstring for Buzzer"""

    def __init__(self):

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(12, GPIO.OUT)
        self.p = GPIO.PWM(12, 5000)  # channel=12 frequency=50Hz

    def rebuz(self, gap):
        self.p.start(0)
        time.sleep(1)
        self.p.stop()
        for i in range(5):
            self.p.ChangeFrequency(5000)
            self.p.start(50)
            time.sleep(0.05)
            self.p.stop(50)
            time.sleep(gap)
        self.p.stop()
        GPIO.cleanup()

