import multiprocessing
from gpiozero import Button
from signal import pause
from time import sleep, time

import serial as serial
import threading
import queue

from lcd import Lcd
from buzzer import Buzzer

jmp = Button(21)
# btn37 = Button(26)
btn_power = Button(19)
btn_channel = Button(13)
btn_start = Button(6, hold_time=5)
channel = 11
power = 8


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
buzzer = Buzzer()


def is_tx():
    return not jmp.is_pressed


def power_mode():
    global power
    power += 1
    if power == 9:
        power = -8

    input_queue.put('setTxPower ' + format(power, 'X'))


def channels():
    input_queue.put('e')
    global channel
    channel += 1
    if channel == 27:
        channel = 11

    input_queue.put('setchannel '+format(channel, 'X'))
    lcd.redraw(channel, 'CHANNEL', 'N/A', 'N/A')


def start():
    sleep(1)
    while not btn_start.is_pressed:
        if is_tx():
            input_queue.put('tx 0')
            lcd.redraw(channel, 'TX mode', 'N/A', 'N/A')
        else:
            input_queue.put('rx')

            if not output_queue.empty():
                if output_queue.get().split('{')[7][0:4] == '0xFF':
                    lcd.redraw(channel, 'GOOD', (output_queue.get().split('{')[7][0:4]), (output_queue.get().split('{')[8][0:3]))
                    output_queue.queue.clear()
                    buzzer.buzz(0.3)
                else:
                    lcd.redraw(channel, 'BAD', (output_queue.get().split('{')[7][0:4]), (output_queue.get().split('{')[8][0:3]))
                    output_queue.queue.clear()
                    buzzer.buzz(0.5)
            else:
                lcd.redraw(channel, 'NO DATA', (output_queue.get().split('{')[7][0:4]), (output_queue.get().split('{')[8][0:3]))
                buzzer.buzz(1)

    input_queue.put('e')
    lcd.redraw(channel, 'STOPED', 'N/A', 'N/A')


def io_jobs():
    sp.flush_Input()
    sp.flush_Output()
    while sp.is_open():
        if not input_queue.empty():
            data = input_queue.get()
            # send it to the serial device
            sp.write(data)
            print(data)

        if sp.in_Waiting() > 0:
            data = sp.read()
            if len(data) > 80:
                output_queue.put(data)


def test():
    buzzer.buzz(0.5)
    print('exit buzzer')


def main():
    while True:
        global sp
        while not sp.is_open():
            sp = SerialProcess()
            print('port is open')

        try:
            t = threading.Thread(target=io_jobs)
            t.start()
            btn_start.when_pressed = start
            btn_channel.when_pressed = channels
            btn_power.when_pressed = power_mode
            pause()

        except Exception as e:
            print('error123')
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

