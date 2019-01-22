import multiprocessing
from gpiozero import Buzzer
from gpiozero import Button
from signal import pause
from time import sleep, time
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

import serial as serial
import threading
import queue

jmp = Button(21)
btn37 = Button(26)
stopbtn = Button(19)
channelbtn = Button(13)
startbtn = Button(6, hold_time=5)
channel = 11
#bz = Buzzer(12)
#bz.beep(on_time=3)


WIDTH = 128
HEIGHT = 160
SPEED_HZ = 4000000
# Raspberry Pi configuration.
DC = 24
RST = 25
SPI_PORT = 0
SPI_DEVICE = 0

disp = TFT.ST7735(
    DC,
    rst=RST,
    spi=SPI.SpiDev(
        SPI_PORT,
        SPI_DEVICE,
        max_speed_hz=SPEED_HZ))

disp.begin()
disp.clear()
# Load an image.
print('Loading image...')
image = Image.open('1234.jpg')

# Resize the image and rotate it so matches the display.
image = image.rotate(270).resize((WIDTH, HEIGHT))

# Draw the image on the display hardware.
print('Drawing image')
disp.display(image)
sleep(3)


draw = disp.draw()
#font = ImageFont.load_default()
font1 = ImageFont.truetype('HelveticaBlkIt.ttf', 24)
font2 = ImageFont.truetype('HelveticaBlkIt.ttf', 12)


def draw_rotated_text(image, text, position, angle, font, fill=(255,255,255)):
    # Get rendered font width and height.
    draw = ImageDraw.Draw(image)
    width, height = draw.textsize(text, font=font)
    # Create a new image with transparent background to store the text.
    textimage = Image.new('RGBA', (width, height), (0,0,0,0))
    # Render the text.
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0,0), text, font=font, fill=fill)
    # Rotate the text image.
    rotated = textimage.rotate(angle, expand=1)
    # Paste the text into the image, using it as a mask for transparency.
    image.paste(rotated, position, rotated)

# Write two lines of white text on the buffer, rotated 90 degrees counter clockwise.
#draw_rotated_text(disp.buffer, 'lqi:0xFF!', (30, 80), 90, font, fill=(255,255,255))
#draw_rotated_text(disp.buffer, 'channel:11!', (50, 80), 90, font, fill=(255,255,255))
disp.display()



class SerialProcess():

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





def rxtxmode():
    if jmp.is_pressed:
        return 0
    else:
        return 1


def stoptest():
    print('sended stop')
    sp.write('e')
    print('stop sended')
    disp.clear()
    draw_rotated_text(disp.buffer, 'STOPED ', (90, 40), 270, font1, fill=(255, 255, 255))
    draw_rotated_text(disp.buffer, 'Channel', (55, 20), 270, font2, fill=(0, 255, 0))
    draw_rotated_text(disp.buffer, str(channel), (50, 80), 270, font1, fill=(255, 255, 255))
    draw_rotated_text(disp.buffer, 'LQI', (30, 20), 270, font2, fill=(0, 255, 0))
    draw_rotated_text(disp.buffer, 'N/A', (10, 20), 270, font1,
                      fill=(255, 255, 255))
    draw_rotated_text(disp.buffer, 'rssi', (30, 100), 270, font2, fill=(0, 255, 0))
    draw_rotated_text(disp.buffer, 'N/A', (10, 100), 270, font1,
                      fill=(255, 255, 255))
    disp.display()


def change_channel():
    print('try to change channel')
    sp.write('e')
    global channel
    if channel == 25:
        channel = 11
    else:
        channel = channel+1
    sp.write('setchannel '+format(channel, 'X'))
    disp.clear()
    draw_rotated_text(disp.buffer, 'Channel', (55, 20), 270, font2, fill=(0, 255, 0))
    draw_rotated_text(disp.buffer, str(channel), (50, 80), 270, font1, fill=(255, 255, 255))
    draw_rotated_text(disp.buffer, 'LQI', (30, 20), 270, font2, fill=(0, 255, 0))
    draw_rotated_text(disp.buffer, 'N/A', (10, 20), 270, font1,
                      fill=(255, 255, 255))
    draw_rotated_text(disp.buffer, 'rssi', (30, 100), 270, font2, fill=(0, 255, 0))
    draw_rotated_text(disp.buffer, 'N/A', (10, 100), 270, font1,
                      fill=(255, 255, 255))
    disp.display()
    print('changed to channel ' + str(channel))


'''
def signaling():
    for i in range(10):
        if output_queue.get().split('{')[7][0:4] == '0xFF':
'''
'''
def checkdata():
    if output_queue.qsize()<10:
        return 0
    else:
'''




def starttest():
    while not stopbtn.is_pressed:
        #stopbtn.is_pressed = menu
        if rxtxmode() == 1:
            print('enter tx mode send tx0')
            sp.write('tx 0')
            disp.clear()
            draw_rotated_text(disp.buffer, 'TX mode', (90,40), 270, font1, fill=(255, 255, 255))
            draw_rotated_text(disp.buffer, 'Channel', (55, 20), 270, font2, fill=(0, 255, 0))
            draw_rotated_text(disp.buffer, str(channel), (50, 80), 270, font1, fill=(255, 255, 255))
            disp.display()

        else:
            print('enter rx mode recving')
            sp.write('rx')
            #while not output_queue.empty():
            #checkdata()
            if not output_queue.empty():
                if output_queue.get().split('{')[7][0:4] == '0xFF':
                    print('good')
                    print('rssi')
                    print((output_queue.get().split('{')[8][0:3]))
                    disp.clear()
                    #draw_rotated_text(disp.buffer, 'GOOD', (30, 20), 270, font2, fill=(255, 255, 255))
                    draw_rotated_text(disp.buffer, 'GOOD', (90, 40), 0, font1, fill=(255, 255, 255))
                    draw_rotated_text(disp.buffer, 'Channel', (55, 20), 0, font2, fill=(0, 255, 0))
                    draw_rotated_text(disp.buffer, str(channel), (50, 80), 0, font1, fill=(255, 255, 255))
                    draw_rotated_text(disp.buffer, 'LQI', (30, 20), 0, font2, fill=(0, 255, 0))
                    draw_rotated_text(disp.buffer, (output_queue.get().split('{')[7][0:4]), (10, 20), 270, font1, fill=(255, 255, 255))
                    draw_rotated_text(disp.buffer, 'rssi', (30, 100), 0, font2, fill=(0, 255, 0))
                    draw_rotated_text(disp.buffer, (output_queue.get().split('{')[8][0:3]), (10, 100), 0, font1, fill=(255, 255, 255))
                    disp.display()
                    output_queue.queue.clear()
                else:
                    print('bad')
                    print('rssi')
                    print((output_queue.get().split('{')[8][0:3]))
                    disp.clear()
                    draw_rotated_text(disp.buffer, 'BAD', (90, 40), 0, font1, fill=(255, 255, 255))
                    draw_rotated_text(disp.buffer, 'Channel', (55, 20), 0, font2, fill=(0, 255, 0))
                    draw_rotated_text(disp.buffer, str(channel), (50, 80), 0, font1, fill=(255, 255, 255))
                    draw_rotated_text(disp.buffer, 'LQI', (30, 20), 0, font2, fill=(0, 255, 0))
                    draw_rotated_text(disp.buffer, (output_queue.get().split('{')[7][0:4]), (10, 20), 270, font1,
                                      fill=(255, 255, 255))
                    draw_rotated_text(disp.buffer, 'rssi', (30, 100), 0, font2, fill=(0, 255, 0))
                    draw_rotated_text(disp.buffer, (output_queue.get().split('{')[8][0:3]), (10, 100), 270, font1,
                                      fill=(255, 255, 255))
                    disp.display()
                    output_queue.queue.clear()
            else:
                print('no data')
                disp.clear()
                draw_rotated_text(disp.buffer, 'NO DATA', (10, 10), 0, font1, fill=(0, 0, 255))
                draw_rotated_text(disp.buffer, 'CHANNEL', (10, 100), 0, font2, fill=(0, 255, 0))
                draw_rotated_text(disp.buffer, str(channel), (75, 90), 0, font1, fill=(255, 255, 255))
                draw_rotated_text(disp.buffer, 'LQI', (10, 120), 0, font2, fill=(0, 255, 0))
                draw_rotated_text(disp.buffer, 'N/A', (10, 130), 0, font1,fill=(255, 255, 255))
                draw_rotated_text(disp.buffer, 'rssi', (70, 120), 0, font2, fill=(0, 255, 0))
                draw_rotated_text(disp.buffer, 'N/A', (70, 130), 0, font1,fill=(255, 255, 255))
                disp.display()
            '''
            if output_queue.qsize() > 10:
                for i in range(10):
                    print((output_queue.get().split('{')[7][0:4]))
                    print((output_queue.get().split('{')[8][0:3]))
                    disp.clear()
                    draw_rotated_text(disp.buffer, 'lqi:'+(output_queue.get().split('{')[7][0:4]), (30, 50), 90, font,fill=(255, 255, 255))
                    disp.display()
            else:
                print('no data to print')
                disp.clear()
                draw_rotated_text(disp.buffer, 'no data', (30, 50), 90, font, fill=(255, 255, 255))
                disp.display()
            '''
            sleep(1)


input_queue = queue.Queue()
output_queue = queue.Queue()


def io_jobs():
    sp.flush_Input()
    sp.flush_Output()
    while True:
        if not input_queue.empty():
            data = input_queue.get()
            # send it to the serial device
            sp.write(data)
            print (data)

        if sp.in_Waiting() > 0:
            data = sp.read()
            if len(data) > 80 and (output_queue.get().split('{')[7][0:2]) == '0x':
                output_queue.put(data)


def menu():
    while True:
        time()
        while not sp.is_open():
            sleep(1)
            print('port is open')
        try:
            t = threading.Thread(target=io_jobs)
            t.start()
            startbtn.when_released = starttest
            channelbtn.when_pressed = change_channel
            stopbtn.when_pressed = stoptest
            pause()

        except Exception as e:
            sp.close()
            raise
        sp.close()


sp = SerialProcess()
if __name__ == '__main__':
    sp.write('setTxPowMode 10')
    sp.write('setTxPower 8')
    sp.write('setchannel B')
    menu()

