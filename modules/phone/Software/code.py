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

class DialCount:

    def __init__(self):
        self.value = 0
        self.full_number = ""


async def catch_interrupt(enable, pulse, pulse_count):

    with keypad.Keys((enable, pulse), value_when_pressed=False) as keys:
        while True:
            event = keys.events.get()

            if event:
                if event.pressed:
                    if event.key_number == 0:
                        print(f"Dialed {pulse_count.value}")
                        pulse_count.full_number += str(pulse_count.value) if pulse_count.value < 10 else "0"
                        print(f"Current Number: {pulse_count.full_number}")
                        # if(pulse_count.value == 10):
                        #     asyncio.run(play_audio)
                        pulse_count.value = 0
                    elif event.key_number == 1:
                        pulse_count.value += 1
                
            await asyncio.sleep(0)


async def play_audio(filename, pulse_count):
    audio = audiopwmio.PWMAudioOut(board.A0)
    decoder = audiomp3.MP3Decoder(open(filename, "rb"))
    
    while True:
        if pulse_count.full_number == "999":
            pulse_count.full_number = ""
            audio.play(decoder)
        await asyncio.sleep(0)

async def main():

    pulse_count = DialCount()
    interrupt_task = asyncio.create_task(catch_interrupt(board.GP13, board.GP14, pulse_count))
    audio_task = asyncio.create_task(play_audio("ringing.mp3", pulse_count))

    await asyncio.gather(interrupt_task, audio_task)

asyncio.run(main())
# audio = audiopwmio.PWMAudioOut(board.A0)

# decoder = audiomp3.MP3Decoder(open("ringing.mp3", "rb"))

# audio.play(decoder)
# while audio.playing:
#     pass

# print("Done playing!")
