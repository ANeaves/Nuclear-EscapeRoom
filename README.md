# Keep Talking and Nothing Melts Down

An escape room type of thing designed to be at least semi-portable.

The idea is to have a central PC (Probably a Raspberry Pi) Controlling the game, and then to have Puzzle Modules (ESP32) with various inputs/outputs that are self contained and communicate their win/loss state to the central machine via some sort of protocol (Probably I2C?)

Additionally, a Manual that people outside the "Escape Room" have access to, that tells the user how to solve the various puzzles. They must communicate with the user inside via a microphone/phone line type setup, without being able to see the puzzles themselves. Think **Keep Talking and Nobody Explodes**