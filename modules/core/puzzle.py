"""CircuitPython Base Puzzle Module"""
import board
import asyncio
import keypad
from digitalio import DigitalInOut, Direction, Pull
try:
    import typing
    from microcontroller import Pin
except ImportError:
    pass

PUZ_STATE = typing.Literal["INIT", "RUN", "WON", "LOSS", "RESET"]
LED_COLOUR = typing.Literal["OFF", "RED", "GREEN"]

class Puzzle:
    """Base Puzzle class, each puzzle module should extend this class"""

    def __init__(self, name: str, led_pins: typing.Tuple[Pin, Pin] = (board.GP0, board.GP1), submit_button_pin = board.GP2):
        """Initialise the puzzle"""
        self.name = name
        self.puz_state: PUZ_STATE = "INIT"

        # Init Submit Button Input
        self.submit_button = submit_button_pin

        # Init Button Bi-colour LED Output
        self.led_green = DigitalInOut(led_pins[0])
        self.led_red = DigitalInOut(led_pins[1])
        self.led_green.direction = Direction.OUTPUT
        self.led_red.direction = Direction.OUTPUT

        self.state_transitions: list[tuple[PUZ_STATE, PUZ_STATE]] = [
            ("INIT", "RUN"),
            ("RUN", "WON"),
            ("RUN", "LOSS"),
            ("RUN", "RESET"),
            ("RESET", "RUN"),
            ("WIN", "RESET"),
            ("LOSS", "RUN"),
            ("LOSS", "RESET")
        ]

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

        keys = keypad.Keys((self.submit_button,), value_when_pressed=False, pull=True)
        while True:
            event = keys.events.get()
            if event:
                if event.pressed:
                    correctness = self.check_solution()
                    if correctness:
                        self.set_state("WON")
                    else:
                        self.set_state("LOSS")
                elif event.released:
                    self.set_state("RUN")

            await asyncio.sleep(0)

    def set_state(self, state: PUZ_STATE):
        """Set the state of the puzzle"""
        #TODO: Add some sort of reporting back to the central PC of the state
        if (self.puz_state, state) not in self.state_transitions:
            print(f"Disallowed State Transition attempted: {self.puz_state} -> {state}")
            return

        if state == "INIT":
            self.puz_state = state
            self.set_led("OFF")
        elif state == "RUN":
            self.puz_state = state
        elif state == "LOSS":
            self.puz_state = state
            self.set_led("RED")
        elif state == "RESET":
            self.puz_state = state
            self.set_led("OFF")
        elif state == "WON":
            self.puz_state = state
            self.set_led("GREEN")

    def set_led(self, colour: LED_COLOUR):
        """Set the colour of the Submit button LED"""
        if colour == "OFF":
            self.led_red.value = False
            self.led_green.value = False
        elif colour == "GREEN":
            self.led_green.value = True
            self.led_red.value = False
        elif colour == "RED":
            self.led_green.value = False
            self.led_red.value = True