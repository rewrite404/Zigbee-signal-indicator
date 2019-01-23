import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
from time import sleep, time

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


class Lcd:
    def __init__(self):
        self.WIDTH = 128
        self.HEIGHT = 160
        self.display = TFT.ST7735(24, rst=25, spi=SPI.SpiDev(0, 0, max_speed_hz=4000000))
        self.font1 = ImageFont.truetype('HelveticaBlkIt.ttf', 24)
        self.label_font = ImageFont.truetype('HelveticaBlkIt.ttf', 12)

        self.display.begin()

        # Load an image.
        image = Image.open('logo.jpg').rotate(0).resize((self.WIDTH, self.HEIGHT))
        self.display.display(image)
        # self.draw = self.display.draw()

    @staticmethod
    def draw_rotated_text(image, text, position, angle, font, fill=(255, 255, 255)):
        # Get rendered font width and height.
        draw = ImageDraw.Draw(image)
        width, height = draw.textsize(text, font=font)
        # Create a new image with transparent background to store the text.
        textimage = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        # Render the text.
        textdraw = ImageDraw.Draw(textimage)
        textdraw.text((0, 0), text, font=font, fill=fill)
        # Rotate the text image.
        rotated = textimage.rotate(angle, expand=1)
        # Paste the text into the image, using it as a mask for transparency.
        image.paste(rotated, position, rotated)

    def redraw(self, channel, state='N/A', lqi='N/A', rssi='N/A'):
        self.display.clear()
        self.draw_rotated_text(self.display.buffer, state, (10, 10), 0, self.font1, fill=(0, 0, 255))
        self.draw_rotated_text(self.display.buffer, 'CHANNEL', (10, 100), 0, self.label_font, fill=(0, 255, 0))
        self.draw_rotated_text(self.display.buffer, str(channel), (75, 90), 0, self.font1, fill=(255, 255, 255))
        self.draw_rotated_text(self.display.buffer, 'LQI', (10, 120), 0, self.label_font, fill=(0, 255, 0))
        self.draw_rotated_text(self.display.buffer, lqi, (10, 130), 0, self.font1, fill=(255, 255, 255))
        self.draw_rotated_text(self.display.buffer, 'RSSI', (70, 120), 0, self.label_font, fill=(0, 255, 0))
        self.draw_rotated_text(self.display.buffer, rssi, (70, 130), 0, self.font1, fill=(255, 255, 255))
        self.display.display()

