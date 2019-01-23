import multiprocessing
from gpiozero import Buzzer
from gpiozero import Button
from signal import pause
from time import sleep, time

import serial as serial
import threading
import queue

from lcd import Lcd

jmp = Button(21)
# btn37 = Button(26)
btn_power = Button(19)
btn_channel = Button(13)
startbtn = Button(6, hold_time=5)
channel = 11
power = 8
#bz = Buzzer(12)
#bz.beep(on_time=3)


class SerialProcess:
    def in_Waiting(self):
        return self.zigbee_uart.inWaiting()

    def flush_Input(self):
        self.zigbee_uart.flushInput()
        return

    def flush_Output(self):
        self.zigbee_uart.flushOutput()
        return

    def __init__(self):
        self.zigbee_uart = serial.Serial(port='/dev/ttyUSB0',
                                         baudrate=115200,
                                         parity=serial.PARITY_NONE,
                                         stopbits=serial.STOPBITS_ONE,
                                         bytesize=serial.EIGHTBITS,
                                         writeTimeout=5,
                                         rtscts=True,
                                         timeout=5)

    def is_open(self):
        return self.zigbee_uart.isOpen()

    def close(self):
        self.zigbee_uart.close()

    def write(self, data):
        data += '\r\n'
        self.zigbee_uart.write(data.encode())

    def read(self):
        data = self.zigbee_uart.readline().strip().decode('utf8')
        return data


input_queue = queue.Queue()
output_queue = queue.Queue()

sp = SerialProcess()
lcd = Lcd()


def is_tx():
    return not jmp.is_pressed


def power_mode():
    global power
    power += 1
    if power == 9:
        power = -8

    input_queue.put('setTxPower ' + format(power, 'X'))


def channels():
    print('change channel')
    input_queue.put('e')
    global channel
    channel += 1
    if channel == 27:
        channel = 11

    input_queue.put('setchannel '+format(channel, 'X'))
    lcd.redraw(channel, 'CHANNEL', 'N/A', 'N/A')


def start():
    sleep(1)
    while not startbtn.is_pressed:
        if is_tx():
            input_queue.put('tx 0')
            lcd.redraw(channel, 'TX mode', 'N/A', 'N/A')
        else:
            input_queue.put('rx')

            if not output_queue.empty():
                if output_queue.get().split('{')[7][0:4] == '0xFF':
                    lcd.redraw(channel, 'GOOD', (output_queue.get().split('{')[7][0:4]), (output_queue.get().split('{')[8][0:3]))
                    output_queue.queue.clear()
                else:
                    lcd.redraw(channel, 'BAD', (output_queue.get().split('{')[7][0:4]), (output_queue.get().split('{')[8][0:3]))
                    output_queue.queue.clear()
            else:
                lcd.redraw(channel, 'NO DATA', (output_queue.get().split('{')[7][0:4]), (output_queue.get().split('{')[8][0:3]))

    input_queue.put('e')
    lcd.redraw(channel, 'STOPED', 'N/A', 'N/A')


def io_jobs():
    sp.flush_Input()
    sp.flush_Output()
    while True:
        if not input_queue.empty():
            data = input_queue.get()
            # send it to the serial device
            sp.write(data)
            print(data)

        if sp.in_Waiting() > 0:
            data = sp.read()
            if len(data) > 80:
                output_queue.put(data)


def main():
    while True:
        while not sp.is_open():
            print('port is open')

        try:
            t = threading.Thread(target=io_jobs)
            t.start()
            startbtn.when_pressed = start
            btn_channel.when_pressed = channels
            btn_power.when_pressed = power_mode
            pause()

        except Exception as e:
            sp.close()
            raise
        sp.close()


if __name__ == '__main__':
    time()
    if is_tx():
        print("Tx Mode")
        input_queue.put('setTxPowMode 10')
        input_queue.put('setTxPower 8')
    else:
        print("Rx mode")

    input_queue.put('setchannel B')
    main()

