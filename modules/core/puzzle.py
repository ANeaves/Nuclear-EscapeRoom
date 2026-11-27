"""CircuitPython Base Puzzle Module"""
import board
import asyncio
import keypad
import usb_cdc
from digitalio import DigitalInOut, Direction, Pull
from StateMachine import StateMachine, State
try:
    from typing import Literal, Tuple
    from microcontroller import Pin
    # PUZ_STATE = Literal["init", "run", "win", "loss", "reset"]
    # LED_COLOUR = Literal["OFF", "RED", "GREEN"]
except ImportError:
    # PUZ_STATE = str
    # LED_COLOUR = str
    pass


class Puzzle(StateMachine):
    """State Machine class to handle the common puzzle logic."""

    def __init__(self, name: str, led_pins: Tuple[Pin, Pin] = (board.GP0, board.GP1), submit_button_pin = board.GP2):
        super().__init__()
        self.name = name

        # self.submit_button = submit_button_pin

        self.led_green = DigitalInOut(led_pins[0])
        self.led_red = DigitalInOut(led_pins[1])
        self.submit = DigitalInOut(submit_button_pin)
        self.led_green.direction = Direction.OUTPUT
        self.led_red.direction = Direction.OUTPUT
        self.submit.direction = Direction.INPUT
        self.submit.pull = Pull.UP
        # self.keys = keypad.Keys((self.submit_button,), value_when_pressed=False, pull=True)

        self.serial = usb_cdc.data
        self.command: str | None = None

        self.add_state(InitState())
        self.add_state(RunState())
        self.add_state(WinState())
        self.add_state(LossState())
        self.add_state(ResetState())

        self.go_to_state("init")

    def gen_solution(self):
        """Generate a solution to the puzzle. Must be extended by specific puzzle module"""
        raise NotImplementedError

    def check_solution(self) -> bool:
        """Check that the solution from the user is correct. must be implemented by specific puzzle module"""
        raise NotImplementedError

    def start_reset(self):
        """Begin the reset process, should the puzzle require it"""
        pass

    def has_reset(self) -> bool:
        """Check that the inputs are in a valid state for a new puzzle to begin"""
        return True

    def set_led(self, colour: Literal["OFF", "RED", "GREEN"]):
        """Set the colour of the Submit button LED"""
        match colour:
            case "OFF":
                self.led_green = False
                self.led_red = False
            case "GREEN":
                self.led_green = True
                self.led_red = False
            case "RED":
                self.led_green = False
                self.led_red = True

    def go_to_state(self, state_name: Literal["init", "run", "win", "loss", "reset"]):
        return super().go_to_state(state_name)

    def update(self):
        self.command = self.read_instruction()
        return super().update()

    def read_instruction(self):
        """If an instruction from the main computer has sent a command, return that command. Otherwise, return None"""
        command = None
        if self.serial and self.serial.in_waiting:
            command = self.serial.readline()
        if command is not None:
            command = command.decode("utf-8")
        return command

    def write_response(self, message: str):
        """Write to the main computer"""

        if self.serial:
            self.serial.write(bytes(message, "utf-8"))


class InitState(State):

    @property
    def name(self):
        return "init"

    def update(self, machine: Puzzle):
        if machine.command == "name":
            machine.write_response(machine.name)
        elif machine.command == "start":
            machine.go_to_state("run")

    def exit(self, machine: Puzzle):
        super().exit(machine)
        machine.gen_solution()


class RunState(State):

    @property
    def name(self):
        return "run"

    def update(self, machine: Puzzle):
        if machine.command == "reset":
            machine.go_to_state("reset")
            return
        if machine.submit.value == False:
            # Submit button pressed.
            correct = machine.check_solution()
            if correct:
                machine.go_to_state("win")
            else:
                machine.go_to_state("loss")


class WinState(State):

    @property
    def name(self):
        return "win"

    def enter(self, machine: Puzzle):
        machine.set_led("GREEN")
        machine.write_response("won")
        return super().enter(machine)


    def update(self, machine: Puzzle):
        if machine.command == "reset":
            machine.go_to_state("reset")


class LossState(State):

    @property
    def name(self):
        return "loss"

    def enter(self, machine: Puzzle):
        machine.set_led("RED")
        machine.write_response("loss")
        return super().enter(machine)

    def update(self, machine: Puzzle):
        if machine.command == "reset":
            machine.go_to_state("reset")
            return
        if machine.submit.value == True:
            # Submit Button released
            machine.go_to_state("run")

    def exit(self, machine: Puzzle):
        super().exit(machine)
        machine.set_led("OFF")

class ResetState(State):

    @property
    def name(self):
        return "reset"

    def enter(self, machine: Puzzle):
        machine.start_reset()
        return super().enter(machine)

    def update(self, machine: Puzzle):
        if machine.has_reset():
            machine.write_response("reset_finished")
            machine.go_to_state("init")
