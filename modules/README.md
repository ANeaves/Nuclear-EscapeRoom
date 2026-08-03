# Puzzle Modules

Each puzzle module will be as self contained as possible, using some sort of input/output devices to be solved by the user.

Each module communicates with the central Pi Computer via i2c as a Slave device.
Each module has, at the very least, a status LED to mark it as Complete/Won, and some sort of Input from the user.