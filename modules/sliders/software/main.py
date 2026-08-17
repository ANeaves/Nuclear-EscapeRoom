from machine import Pin, ADC
from utime import sleep
from ssd1306 import SSD1306_I2C
from tca import TCA
from images.images import ImageBuffer
import framebuf

PUZZLE_STATES = ["INIT", "RUN", "WON", "LOSS", "RESET"]

BALANCE_OPTIONS = [
    ("magic", "more magic"),
    ("flora", "fauna"),
    ("accelerate", "decelerate")
]


class Puzzle:

    def __init__(self):
        self.state = "INIT"
        self.led_pin = Pin(0, Pin.OUT)
        
        self.submit_button = Pin(1, Pin.IN, Pin.PULL_UP )

        self.slider_0 = ADC(Pin(26))
        self.slider_1 = ADC(Pin(27))
        self.slider_2 = ADC(Pin(28))

        print("Init MUX")
        self.mux = TCA(0, sda=Pin(4), scl=Pin(5))
        sleep(1)

        print("Create Screen objects")
        self.screens = [SSD1306_I2C(128, 64, self.mux.channels[x]) for x in range(0, 6)]

        print("Init Screens")
        for index, screen in enumerate(self.screens):
            screen.init_display()
            screen.fill(0)
            screen.text("Initialising", 8, 8)
            screen.text(f"Screen {index}...", 8, 20)
            screen.show()

        images = [ImageBuffer(f"images/{name}.bmp") for name in list("ABCDEFGHIJ")]

        background = ImageBuffer("images/background.bmp")

        self.screens[0].write_cmd(0xC0) # mirror image vertically
        self.screens[0].fill(0)
        self.screens[0].blit(background.framebuf, 0, 0)
        self.screens[0].blit(images[0].framebuf, 32, 0)
        self.screens[0].show()

        self.screens[1].write_cmd(0xC0) # mirror image vertically
        self.screens[1].fill(0)
        self.screens[1].blit(background.framebuf, 0, 0)
        self.screens[1].blit(images[1].framebuf, 32, 0)
        self.screens[1].show()

    def generate_solution(self):
        """Some method to create a valid solution and display it"""
        pass

    def check_solution(self):
        """Method to check if user input matches generated solution"""


if __name__ == "__main__":

    puz = Puzzle()