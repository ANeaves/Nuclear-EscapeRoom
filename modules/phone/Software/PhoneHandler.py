import audiomp3
import audiopwmio
import keypad
from StateMachine import StateMachine, State

try:
    import typing
    from microcontroller import Pin
except ImportError:
    pass

PHONE_STATE = typing.Literal["idle", "dialing", "connected", "disconnected", "invalid"]

dial = "dial_tone.mp3"
invalid = "number_unavailable.mp3"
ringing = "ringing.mp3"
poacher = "poacher.mp3"
sam = "sam.mp3"

class PhoneHandler(StateMachine):
    """State Machine class to handle the various functions of the Phone, such as dialing and playing audio"""

    def __init__(self, enable: Pin, pulse: Pin, handset: Pin, audio: Pin) -> None:
        super().__init__()
        self.dial_val = 0
        self.dialed_number = "NaN"

        self.audio = audiopwmio.PWMAudioOut(audio)
        self.decoder = audiomp3.MP3Decoder(dial) # pyright: ignore[reportCallIssue]
        self.keys = keypad.Keys((enable, pulse, handset), value_when_pressed=False)

        self.number_dict = {
            "01282": [ringing, poacher],
            "01154": [ringing, sam]
        }

        self.add_state(IdleState())
        self.add_state(DialingState())
        self.add_state(ConnectedState())
        self.add_state(DisconnectedState())
        self.add_state(InvalidState())

        self.go_to_state("idle")

    def go_to_state(self, state_name: PHONE_STATE):
        return super().go_to_state(state_name)


class IdleState(State):

    def __init__(self) -> None:
        super().__init__()

    @property
    def name(self) -> PHONE_STATE:
        return 'idle'

    def enter(self, machine: PhoneHandler) -> State:
        machine.audio.stop()
        machine.dialed_number = "NaN"
        return super().enter(machine)

    def exit(self, machine: PhoneHandler):
        return super().exit(machine)

    def update(self, machine: PhoneHandler):
        
        event = machine.keys.events.get()
        if event and event.key_number == 2 and event.released:
            return machine.go_to_state("dialing")


class DialingState(State):

    def __init__(self) -> None:
        super().__init__()
        self.dial_val = 0

    @property
    def name(self) -> PHONE_STATE:
        return 'dialing'

    def enter(self, machine: PhoneHandler) -> State:
        machine.dialed_number = ""
        machine.decoder.open(dial)
        machine.audio.play(machine.decoder, loop=True)
        return super().enter(machine)

    def exit(self, machine: PhoneHandler):
        machine.audio.stop()
        return super().exit(machine)

    def update(self, machine: PhoneHandler):
        event = machine.keys.events.get()
        if event and event.pressed:
            if event.key_number == 0:
                # Dial Enable Pin. When pressed, means the dialing has finished
                print(f"Dialed {self.dial_val}")
                machine.dialed_number += str(self.dial_val) if self.dial_val < 10 else "0"
                self.dial_val = 0
            elif event.key_number == 1:
                # Dial Pulse Pin. Increment dialed number
                self.dial_val += 1
            elif event.key_number == 2:
                # Handset replaced
                machine.go_to_state("idle")

        if machine.dialed_number in machine.number_dict.keys():
            return machine.go_to_state("connected")
        elif len(machine.dialed_number) >= max(len(num) for num in machine.number_dict.keys()):
            return machine.go_to_state("invalid")


class ConnectedState(State):

    def __init__(self) -> None:
        super().__init__()
        self.files: list[str] = []

    @property
    def name(self) -> PHONE_STATE:
        return 'connected'

    def enter(self, machine: PhoneHandler):
        self.files = machine.number_dict.get(machine.dialed_number, [invalid])
        return super().enter(machine)

    def exit(self, machine: PhoneHandler):
        return super().exit(machine)

    def update(self, machine: PhoneHandler):
        event = machine.keys.events.get()
        if event and event.pressed and event.key_number == 2:
            return machine.go_to_state("idle")
            

        if not machine.audio.playing:
            if self.files:
                machine.decoder.open(self.files.pop(0))
                machine.audio.play(machine.decoder)
            else:
                machine.go_to_state("disconnected")


class DisconnectedState(State):

    def __init__(self) -> None:
        super().__init__()

    @property
    def name(self) -> PHONE_STATE:
        return 'disconnected'

    def enter(self, machine: PhoneHandler):
        machine.audio.stop()
        return super().enter(machine)

    def exit(self, machine: PhoneHandler):
        return super().exit(machine)

    def update(self, machine: PhoneHandler):
        event = machine.keys.events.get()
        if event and event.pressed and event.key_number == 2:
            return machine.go_to_state("idle")


class InvalidState(State):

    def __init__(self) -> None:
        super().__init__()

    @property
    def name(self) -> PHONE_STATE:
        return 'invalid'

    def enter(self, machine: PhoneHandler):
        machine.decoder.open(invalid)
        machine.audio.play(machine.decoder)
        return super().enter(machine)

    def exit(self, machine: PhoneHandler):
        return super().exit(machine)

    def update(self, machine: PhoneHandler):
        event = machine.keys.events.get()
        if event and event.pressed and event.key_number == 2:
            return machine.go_to_state("idle")

        if not machine.audio.playing:
            return machine.go_to_state("disconnected")
