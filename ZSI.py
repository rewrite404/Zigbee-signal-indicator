from gpiozero import Button
from signal import pause
from time import sleep, time

import serial as serial
import threading
import queue
import statistics
from enum import Enum
from lcd import Lcd
from buzzer import Buzzer


class Mode(Enum):
    START_MODE = '@'
    STOP_MODE = '#'
    CHANNEL_MODE = '$'
    IDLE_MODE = '%'
    HOLD_MODE = '^'


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

        if self.zigbee_uart.is_open:
            input_queue.put('setchannel '+format(channel, 'X'))
            if is_tx():
                input_queue.put('setTxPowMode 10')
                input_queue.put('settxpower ' + format(power, 'X'))

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


def is_tx():
    return not jmp.is_pressed


def power_mode():
    if not is_tx():
        return
    global power
    power += 1
    if power == 9:
        power = -8

    input_queue.put('settxpower ' + format(power, 'X'))
    buzzer.prog()


def set_channels():
    global current_mode, channel
    if current_mode != Mode.CHANNEL_MODE:
        return

    input_queue.put('setchannel ' + format(channel, 'X'))
    current_mode = Mode.HOLD_MODE
    buzzer.prog()


def channels():
    global current_mode, channel
    if current_mode == Mode.START_MODE:
        return
    elif current_mode == Mode.HOLD_MODE:
        current_mode = Mode.IDLE_MODE
        return

    current_mode = Mode.CHANNEL_MODE

    channel += 1
    if channel == 27:
        channel = 11

    buzzer.set()


def stop():
    global current_mode
    if current_mode == Mode.START_MODE:
        current_mode = Mode.STOP_MODE
        input_queue.put('e')
    btn_start.when_pressed = start
    buzzer.set()


def start():
    global current_mode
    if current_mode != Mode.START_MODE:
        current_mode = Mode.START_MODE
        if is_tx():
            input_queue.put('tx 0')
        else:
            input_queue.put('rx')

    btn_start.when_pressed = stop
    buzzer.set()


def io_jobs():
    sp.flush_Input()
    sp.flush_Output()

    rssi = []
    lqi = []
    while sp.is_open():

        if current_mode == Mode.STOP_MODE:
            lcd.redraw(channel, 'STOPED', 'N/A', 'N/A')
        elif current_mode == Mode.CHANNEL_MODE:
            lcd.redraw(channel, 'CHANNEL', 'N/A', 'N/A')
        elif current_mode == Mode.IDLE_MODE:
            lcd.redraw(channel, 'IDLE', 'N/A', 'N/A')
        elif current_mode == Mode.START_MODE and output_queue.empty():
            if is_tx():
                lcd.redraw(channel, 'Transmit', 'N/A', 'N/A')
            else:
                lcd.redraw(channel, 'Receive', 'N/A', 'N/A')
        elif not output_queue.empty():
            output_queue.get()
            if y == 255:
                lcd.redraw(channel, 'Good', str(y), str(x))
                buzzer.buzz(.5, 5000)
            else:
                lcd.redraw(channel, 'Bad', str(y), str(x))

        sleep(.1)

        if not input_queue.empty():
            data = input_queue.get()
            # send it to the serial device
            if data == 'e':
                sp.flush_Input()
                sp.flush_Output()
                output_queue.queue.clear()
                input_queue.queue.clear()

            sp.write(data)
            print(data)

        if sp.in_Waiting() > 1 and current_mode == Mode.START_MODE:
            data = sp.read()
            if len(data) > 80:
                r = (data.split('{')[8][0:3])
                l = (data.split('{')[7][0:4])
                try:
                    int(r)
                    rssi.append(r)
                    lqi.append(int(l, 16))
                except ValueError:
                    continue

                if len(rssi) > 10:
                    sp.flush_Input()
                    try:
                        x = statistics.mode(rssi)
                        y = statistics.mode(lqi)
                        rssi[:] = []
                        lqi[:] = []
                        output_queue.put(data)
                        print('RSSI:{}, LQI: {}'.format(repr(x), repr(y)))
                        if y == 255:
                            lcd.redraw(channel, 'Good', str(y), str(x))
                            buzzer.buzz(.1, 5000, 1)
                        else:
                            lcd.redraw(channel, 'Bad', str(y), str(x))
                    except statistics.StatisticsError:
                        continue


if __name__ == '__main__':
    time()
    jmp = Button(21)
    btn_power = Button(19)
    btn_channel = Button(13, hold_time=2)
    btn_start = Button(6)

    channel = 11
    power = 8
    current_mode = ''

    input_queue = queue.Queue()
    output_queue = queue.Queue()

    sp = SerialProcess()
    lcd = Lcd()
    buzzer = Buzzer()

    buzzer.start()

    if is_tx():
        print("Tx Mode")
    else:
        print("Rx mode")

    while True:
        while not sp.is_open():
            sp = SerialProcess()
            print('port is open')

        try:
            t = threading.Thread(target=io_jobs)
            t.start()
            btn_start.when_pressed = start
            btn_channel.when_released = channels
            btn_channel.when_held = set_channels
            btn_power.when_pressed = power_mode
            current_mode = Mode.IDLE_MODE
            pause()
        except Exception:
            sp.close()
            raise
        sp.close()

