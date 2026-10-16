"""CircuitPython Base Puzzle Module"""
import board
import asyncio
from digitalio import DigitalInOut, Direction, Pull
try:
    import typing
    from microcontroller import Pin
except ImportError:
    pass

PUZ_STATE = typing.Literal["INIT", "RUN", "WON", "LOSS", "RESET"]

class Puzzle:
    """Base Puzzle class, each puzzle module should extend this class"""

    def __init__(self, led_pins: typing.Tuple[Pin, Pin] = (board.GP0, board.GP1), submit_button_pin = board.GP2):
        """Initialise the puzzle"""
        self.puz_state: PUZ_STATE = "INIT"

        # Init Submit Button Input
        self.submit_button = DigitalInOut(submit_button_pin)
        self.submit_button.pull = Pull.UP

        # Init Button Bi-colour LED Output
        self.led_green = DigitalInOut(led_pins[0])
        self.led_red = DigitalInOut(led_pins[1])
        self.led_green.direction = Direction.OUTPUT
        self.led_red.direction = Direction.OUTPUT

        self.async_tasks = [
            asyncio.create_task(self.handle_submit_button())
        ]

    def run(self):
        asyncio.run(self.main())

    async def main(self):
        """Run the Async IOLoop. At minimum, needs to catch the Submit Button interrupt task"""
        await asyncio.gather(*self.async_tasks)

    def gen_solution(self):
        """Generate a solution to the puzzle. Must be extended by specific puzzle module"""
        raise NotImplementedError

    def check_solution(self) -> bool:
        """Check that the solution from the user is correct"""
        raise NotImplementedError

    def has_reset(self) -> bool:
        """Check that the inputs are in a valid state for a new puzzle to start"""
        return True

    async def handle_submit_button(self):
        """Check if the Submit button has been pressed.
        If so, check solution and change state/LED light accordingingly
        """
        while True:
            if self.submit_button.value == False:
                # Button setup with a Pullup. Pressing should pull to ground, and so read false

                #TODO: How to report status to core control PC?
                correctness = self.check_solution()

                if correctness:
                    self.puz_state = "WON"
                    self.led_green.value = True
                    self.led_red.value = False
                else:
                    self.puz_state = "LOSS"
                    self.led_red.value = True
                    self.led_green.value = False
            else:
                if self.puz_state != "WON":
                    self.led_red.value = False
                    self.led_green.value = False
