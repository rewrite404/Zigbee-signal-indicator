import RPi.GPIO as GPIO
from time import sleep


class Buzzer:
    """docstring for Buzzer"""

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(12, GPIO.OUT)
        self.p = GPIO.PWM(12, 5000)

    def beep(self, freq):
        self.p.ChangeFrequency(freq)
        self.p.start(50)
        sleep(0.1)
        self.p.stop(50)

    def buzz(self, gap, freq, n=1):
        self.p.start(0)
        sleep(1)
        self.p.stop()
        for x in range(n):
            self.beep(freq)
            sleep(gap)


