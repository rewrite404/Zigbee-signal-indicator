import RPi.GPIO as GPIO
from time import sleep


class Buzzer:
    """docstring for Buzzer"""

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(12, GPIO.OUT)
        self.p = GPIO.PWM(12, 5000)
        self.p.start(0)
        sleep(.1)
        self.p.stop()

    def beep(self, freq):
        self.p.ChangeFrequency(freq)
        self.p.start(100)
        sleep(0.05)
        self.p.stop(100)

    def buzz(self, gap):
        for x in range(6):
            self.beep(5000)
            sleep(gap)


