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

class PhoneState:

    def __init__(self):
        self.state: typing.Literal["idle", "dialing", "connected", "disconnected"] = "idle"
        self.current_dial_val = 0
        self.dialed_number = ""


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
            if state.state == "idle" or state.state == "dialing":
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


async def play_audio(filename, state: PhoneState):
    audio = audiopwmio.PWMAudioOut(board.A0)
    decoder = audiomp3.MP3Decoder(open(filename, "rb"))
    
    while True:
        if state.state == "idle":
            # handset has been replaced. Cut Audio
            if audio.playing:
                audio.stop()
        if state.state == "dialing":
            if state.dialed_number == "999" and not audio.playing:
                print("Audio: Connected")
                state.state = "connected"
                audio.play(decoder)
        if state.state == "connected":
            if not audio.playing:
                print("Disconnected")
                state.state = "disconnected"
                state.dialed_number = ""
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
            screen.set_white()
        if state.state == "dialing" and state.dialed_number != last_number:
            last_number = state.dialed_number
            last_state = state.state
            screen.update("Dialing...", state.dialed_number)
        if state.state == "connected" and last_state != "connected":
            last_state = "connected"
            screen.set_rgb(0, 255, 0)
            screen.update("Connected!")
        if state.state == "disconnected" and last_state != "disconnected":
            last_state = "disconnected"
            last_number = "None"
            screen.set_rgb(255, 0, 0)
            screen.update("Disconnected...")

        
        await asyncio.sleep(0)

def get_screen(scl: Pin, sda: Pin):
    i2c = I2C(scl, sda)
    screen = Screen(i2c)
    screen.update("Initialising...")

    return screen

async def main():

    state = PhoneState()
    screen = get_screen(board.GP5, board.GP4)

    interrupt_task = asyncio.create_task(catch_interrupt(board.GP13, board.GP14, state))
    audio_task = asyncio.create_task(play_audio("ringing.mp3", state))
    screen_task = asyncio.create_task(handle_screen(screen, state))

    handset_tast = asyncio.create_task(handle_lifting(board.GP0, state))


    await asyncio.gather(interrupt_task, audio_task, screen_task, handset_tast)

asyncio.run(main())

