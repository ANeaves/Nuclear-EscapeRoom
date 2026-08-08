from machine import Pin, I2C
from utime import sleep
from ssd1306 import SSD1306_I2C
from tca import TCA

pin = Pin("LED", Pin.OUT)

mux = TCA(0, sda=Pin(0), scl=Pin(1))
sleep(1)


screen_0 = SSD1306_I2C(128, 64, mux.channels[0])
screen_1 = SSD1306_I2C(128, 64, mux.channels[1])

screen_0.init_display()
screen_0.fill(0)

screen_0.text("Display 1", 0, 0)
screen_0.show()

screen_1.init_display()
screen_1.fill(0)

screen_1.text("Display 2!", 0, 0)
# screen_1.invert(1)
screen_1.show()