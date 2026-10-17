import board
from adafruit_tca9548a import TCA9548A
from adafruit_ssd1306 import SSD1306_I2C
from images.images import ImageBuffer
import asyncio
from analogio import AnalogIn#
from busio import I2C

from itertools import combinations
from random import sample, choice

from .puzzle import Puzzle, PUZ_STATE, Pin

SLIDER_MAX = 11
class DisplayPairing:

    def __init__(self, img_top: ImageBuffer, img_bot: ImageBuffer, val: int) -> None:
        self.img_top = img_top
        self.img_bot = img_bot
        self.target_val = val

class Sliders(Puzzle):
    """Slider Puzzle Module Class"""

    def __init__(self):
        super().__init__()

        self.slider_0 = AnalogIn(board.A0)
        self.slider_1 = AnalogIn(board.A1)
        self.slider_2 = AnalogIn(board.A2)

        i2c = I2C(board.GP5, board.GP4)
        tca = TCA9548A(i2c)

        self.screens = [SSD1306_I2C(128, 64, tca[x]) for x in range(0, 6)] # type: ignore

        for index, screen in enumerate(self.screens):
            screen.init_display()
            screen.fill(0)
            screen.text("Initialising", 8, 8)
            screen.text(f"Screen {index}...", 8, 20)
            screen.show()

        self.images = [ImageBuffer(f"images/{name}.bmp") for name in list("ABCDEFGHIJ")]
        self.background = ImageBuffer("images/background.bmp")

        self.pairings = self.get_all_options()
        self.solution = [0, 0, 0]

    def gen_solution(self):
        self.reset_screens()
        selected = sample(self.pairings, 3)
        for index, display in enumerate(selected):
            
            if choice([True, False]):
                # 50/50 chance of flipping the screens and therefore answer
                self.solution[index] = display.target_val
                self.screens[index].blit(display.img_top.framebuf, 32, 0)
                self.screens[index + 1].blit(display.img_bot.framebuf, 32, 0)
            else:
                self.solution[index] = SLIDER_MAX - display.target_val
                self.screens[index].blit(display.img_bot.framebuf, 32, 0)
                self.screens[index + 1].blit(display.img_top.framebuf, 32, 0)

        print(f"Solution: {self.solution}")
        for screen in self.screens:
            screen.show()
        self.puz_state = "RUN"

    def check_solution(self) -> bool:
        """Read each slider value, compare to expected values"""
        read = [self.slider_0.value, self.slider_1.value, self.slider_2.value]
        input_solution = [self.map_range(x, 0, 65535, 0, SLIDER_MAX) for x in read]

        return all(x == y for x, y in zip(self.solution, input_solution))

    def get_all_options(self):
        """Generate list of all possible screen pairings"""

        combos = combinations(range(len(self.images)), 2)

        # TODO: Actually get unique values for each pairing
        return [DisplayPairing(self.images[x], self.images[y], 0) for (x,y) in combos]

    def reset_screens(self):
        """Blank out all screens, showing just the background frame"""
        for screen in self.screens:
            screen.fill(0)
            screen.blit(self.background.framebuf, 0, 0)
            screen.show()

    def map_range(self, num: int, inMin: int, inMax: int, outMin: int, outMax: int):
        return round(outMin + ((num - inMin) / (inMax - inMin) * (outMax - outMin)))