"""Main Phone Puzzle Code"""
import board
import asyncio
from digitalio import DigitalInOut, Direction, Pull

from puzzle import Puzzle
from PhoneHandler import PhoneHandler, PHONE_STATE
from rgb1602 import Screen
from busio import I2C


# Puzzle Pins
led_green = board.GP1
led_red = board.GP2
submit = board.GP3

# Phone Pins
enable = board.GP13
pulse = board.GP14
handset = board.GP0
audio = board.A0

# Puzzle Input/Output Pins
# NOTE: Counter pin 0 is not used and permanantly tied to GND
# declared as an unused pin here for completeness.
counter = [board.GP11, board.GP16, board.GP17, board.GP18, board.GP19, board.GP20, board.GP21, board.GP22, board.GP27, board.GP28]
select = [board.GP6, board.GP7, board.GP8, board.GP9, board.GP10]
screen_scl = board.GP5
screen_sda = board.GP4

class PhonePuzzle(Puzzle):

    def __init__(self):
        """Initialise the Phone Puzzle Class"""
        # Setup base class
        super().__init__("phone", (led_green, led_red), submit)

        # Setup Phone state machine
        self.phone = PhoneHandler(enable, pulse, handset, audio)

        # Setup Screen I2C
        i2c = I2C(screen_scl, screen_sda)
        self.screen = Screen(i2c)
        self.screen.update("Initialising...")

        # Setup Puzzle
        self.display_code = ""
        """The Code to display on the screen as a hint to the solution"""
        self.solution_code = 0
        """The Correct code to input on the dials to solve the puzzle"""
        self.counters = [DigitalInOut(count_pin) for count_pin in counter if count_pin]
        for count in self.counters:
            count.direction = Direction.INPUT
            count.pull = Pull.DOWN
        self.count_selectors = [DigitalInOut(select_pin) for select_pin in select]
        for selector in self.count_selectors:
            selector.direction = Direction.OUTPUT

        # Setup Async update loops
        self.async_tasks.append(asyncio.create_task(self.monitor_phone()))

    def run(self):
        print("Starting Phone Main Run Loop")
        return super().run()

    def gen_solution(self):
        # TODO: Generate real solution
        self.display_code = "FBA319-T"
        self.solution_code = 0

    def check_solution(self) -> bool:
        # Read the input from the dials
        print("Checking Phone Solution")
        values: list[int] = [0] * len(self.count_selectors)
        for index, selector in enumerate(self.count_selectors):
            selector.value = True
            count_vals = [count.value for count in self.counters]
            true_pins = [i for i, x in enumerate(count_vals) if x]
            selector.value = False # reset pin down to avoid breaking next selector read
            if not true_pins:
                # No pin read high, means a value of 0
                values[index] = 0
            elif len(true_pins) > 1:
                print(f"Read {len(true_pins)} connected dial values, which is invalid")
                return False
            else:
                values[index] = true_pins[0] if true_pins else 0

        print(f"Read Dial Values: {values}")
        input_val = int(''.join(map(str, values)))
        return input_val == self.solution_code

    def update_screen(self, old_state: PHONE_STATE = "idle", state: PHONE_STATE = "idle", old_num: str = "", num: str = ""):

        if state == "dialing" and old_num != num:
            if len(num):
                area, rest = num[:5], num[5:]
                if len(rest) > 3:
                    rest = " ".join([rest[:3], rest[3:]])
                num = " ".join([area, rest])
            self.screen.set_css_color("white")
            self.screen.update("Dialing...", num)
            return
        elif state != old_state:
            # Check for state change because just updating the screen every time causes flickering
            if state == "idle":
                self.screen.set_css_color("white")
                self.screen.update("Handset Network Code:", self.display_code)
                return
            elif state == "dialing":
                # Handled Above with number checking
                return
            elif state == "connected":
                self.screen.set_css_color("green")
                self.screen.update("Connected!")
                return
            elif state == "disconnected":
                self.screen.set_css_color("red")
                self.screen.update("Disconnected...")
                return
            elif state == "invalid":
                self.screen.set_css_color("orange")
                self.screen.update("Invalid Number")
                return
    
    async def monitor_phone(self):
        while True:
            old_state: PHONE_STATE = getattr(self.phone.state, "name", "idle")
            old_number = self.phone.dialed_number
            self.phone.update()
            state: PHONE_STATE = getattr(self.phone.state, "name", "idle")
            self.update_screen(old_state, state, old_number, self.phone.dialed_number)

            await asyncio.sleep(0)


puzzle = PhonePuzzle()
puzzle.gen_solution()
puzzle.run()

