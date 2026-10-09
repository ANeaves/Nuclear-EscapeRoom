# SPDX-FileCopyrightText: 2021 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
CircuitPython single MP3 playback example for Raspberry Pi Pico.
Plays a single MP3 once.
"""
import board
import audiomp3
import audiopwmio
import asyncio
import keypad

from rgb1602 import Screen
from busio import I2C

try:
    import typing
    from microcontroller import Pin
except ImportError:
    pass

MAX_NUMBER_LENGTH = 11
number_dict = {
    "999": "ringing.mp3",
    "01282960229": "poacher.mp3",
    "unknown": "number_unavailable.mp3",
    "01154960925": "sam.mp3",
    "111": "sam.mp3"
}

class PhoneState:

    def __init__(self):
        self.state: typing.Literal["idle", "dialing", "connecting", "connected", "disconnected", "invalid"] = "idle"
        self.current_dial_val = 0
        self.dialed_number = ""
        self.audio_filename = ""
        self.playing = False


async def state_handler(state: PhoneState, audio: audiopwmio.PWMAudioOut):

    while True:
        if state.state == "dialing":
            if state.dialed_number in number_dict.keys():
                print("State: Number recognised, transition to Connected")
                state.state = "connecting"
                state.audio_filename = number_dict[state.dialed_number]
                audio.stop()
                
            elif len(state.dialed_number) >= MAX_NUMBER_LENGTH:
                print("State: Invalid number, transition to Invalid")
                state.state = "invalid"
                audio.stop()
        elif state.state == "connected" or state.state == "invalid":
            if not audio.playing:
                # MP3 playback completed
                print("State: Audio playback complete. Tranition to Disconnected")
                state.state = "disconnected"
                state.dialed_number = ""
                state.audio_filename = ""
                state.playing = False

        await asyncio.sleep(0)

async def handle_lifting(lift: Pin, state: PhoneState):
    with keypad.Keys((lift,), value_when_pressed=False) as keys:
        while True:
            event = keys.events.get()
            if event:
                if event.pressed:
                    print("Handset Replaced")
                    state.state = "idle"

                elif event.released:
                    print("Handset Lifted")
                    state.state = "dialing"

            await asyncio.sleep(0)


async def catch_interrupt(enable: Pin, pulse: Pin, state: PhoneState):

    with keypad.Keys((enable, pulse), value_when_pressed=False) as keys:
        # Using Keypad to handle pin state transitions (rising/falling edges)
        while True:
            if state.state == "dialing":
                event = keys.events.get()

                if event:
                    if event.pressed:
                        state.state = "dialing"
                        if event.key_number == 0:
                            print(f"Dialed {state.current_dial_val}")
                            state.dialed_number += str(state.current_dial_val) if state.current_dial_val < 10 else "0"
                            print(f"Current Number: {state.dialed_number}")
                            # if(state.value == 10):
                            #     asyncio.run(play_audio)
                            state.current_dial_val = 0
                        elif event.key_number == 1:
                            state.current_dial_val += 1
            await asyncio.sleep(0)


async def handle_audio(audio: audiopwmio.PWMAudioOut, state: PhoneState):
        
    while True:
        if state.state == "idle":
            # handset has been replaced. Cut Audio
            if audio.playing:
                audio.stop()
        elif state.state == "dialing":
            if not audio.playing:
                decode = audiomp3.MP3Decoder(open("dial_tone.mp3", "rb"))
                audio.play(decode, loop=True)
        elif state.state == "connecting":
            if not audio.playing:
                if not state.playing:
                    print("Starting Ringer Audio")
                    state.playing = True
                    decode = audiomp3.MP3Decoder(open("ringing.mp3", "rb"))
                    audio.play(decode)
                else:
                    print("Connected")
                    state.state = "connected"
                    decode = audiomp3.MP3Decoder(open(state.audio_filename, "rb"))
                    audio.play(decode)
        elif state.state == "invalid":
            if not audio.playing:
                file = number_dict["unknown"]
                decode = audiomp3.MP3Decoder(open(file, "rb"))
                audio.play(decode)
        elif state.state == "disconnected":
            audio.stop()
        await asyncio.sleep(0)


async def handle_screen(screen: Screen, state: PhoneState):
    last_number = "None"
    last_state = "None"
    while True:
        if state.state == "idle" and state.state != last_state:
            last_state = state.state
            screen.update("Lift Handset","to start")
            last_number = "None"
            state.dialed_number = ""
            screen.set_css_color("white")
        if state.state == "dialing" and state.dialed_number != last_number:
            last_number = state.dialed_number
            last_state = state.state
            display_number = state.dialed_number
            if len(display_number):
                area, rest = display_number[:5], display_number[5:]
                if len(rest) > 3:
                    rest = " ".join([rest[:3], rest[3:]])

                display_number = " ".join([area, rest])
            screen.set_css_color("white")
            screen.update("Dialing...", display_number)
        if state.state == "connected" and last_state != "connected":
            last_state = "connected"
            screen.set_css_color("green")
            screen.update("Connected!")
        if state.state == "disconnected" and last_state != "disconnected":
            last_state = "disconnected"
            last_number = "None"
            screen.set_css_color("red")
            screen.update("Disconnected...")
        if state.state == "invalid" and last_state != "invalid":
            last_state = "invalid"
            screen.set_css_color("orange")
            screen.update("Invalid Number")

        
        await asyncio.sleep(0)

def get_screen(scl: Pin, sda: Pin):
    i2c = I2C(scl, sda)
    screen = Screen(i2c)
    screen.update("Initialising...")

    return screen

async def main():

    state = PhoneState()
    screen = get_screen(board.GP5, board.GP4)
    audio = audiopwmio.PWMAudioOut(board.A0)

    interrupt_task = asyncio.create_task(catch_interrupt(board.GP13, board.GP14, state))
    audio_task = asyncio.create_task(handle_audio(audio, state))
    screen_task = asyncio.create_task(handle_screen(screen, state))

    handset_tast = asyncio.create_task(handle_lifting(board.GP0, state))

    state_task = asyncio.create_task(state_handler(state, audio))


    await asyncio.gather(interrupt_task, audio_task, screen_task, handset_tast, state_task)

asyncio.run(main())

