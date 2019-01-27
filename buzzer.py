import RPi.GPIO as GPIO
from time import sleep


class Buzzer:
    """docstring for Buzzer"""

    pin = 12

    Short_Duration = .06
    Long_Duration = .18
    Low_Pitch = 2550
    mid_Pitch = 2750
    High_Pitch = 3150

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin, 100)

    def beep(self, freq, duration):
        self.pwm.ChangeFrequency(freq)
        self.pwm.start(0)
        sleep(.01)
        for x in range(30):
            self.pwm.ChangeDutyCycle(x)
        sleep(duration)
        self.pwm.stop()

    def buzz(self, gap, freq, n=1):
        for x in range(n):
            self.beep(freq, gap)
            sleep(.1)

    def start(self):
        self.buzz(self.Short_Duration, self.Low_Pitch)
        self.buzz(self.Long_Duration, self.mid_Pitch)
        self.buzz(self.Short_Duration * 2, self.High_Pitch)

    def error(self):
        self.buzz(self.Short_Duration, self.High_Pitch, 3)

    def set(self):
        self.buzz(self.Short_Duration, self.mid_Pitch)

    def prog(self):
        self.buzz(self.Long_Duration, self.High_Pitch)
        self.buzz(self.Short_Duration, self.mid_Pitch)
