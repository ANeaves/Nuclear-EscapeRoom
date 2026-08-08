from machine import Pin, I2C
from utime import sleep
from ssd1306 import SSD1306_I2C
from adafruit_tca9548a import TCA9548A

pin = Pin("LED", Pin.OUT)

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
sleep(1)

display = SSD1306_I2C(128, 64, i2c, 0x3C)



contrast = 0
while(True):
    if contrast == 255:
        contrast = 0
    else:
        contrast = 255
    display.fill(0)

    display.text("Hello World!", 0, 0)

    display.contrast(contrast)

    display.text(f"Contrast: {contrast}", 0, 8)

    display.show()

    sleep(1)
