# from typing import Any, List, Sequence, Union

from machine import Pin, I2C
# from _mpy_shed import AnyReadableBuf, AnyWritableBuf


class TCA:

    def __init__(self, bus: int, sda = Pin(0), scl = Pin(1), addr = 0x70) -> None:
        self.bus = I2C(bus, sda=sda, scl=scl)
        self.addr = addr

        self.channels = [None] * 8
        for x in range(0, 7):
            self.channels[x] = TCA_Channel(x, self)

    def select_chan(self, chan: int):
        if(chan < 0 or chan > 7):
            raise ValueError("Channel can only be 0-7")
        self.bus.writeto(self.addr, bytes([1 << chan]))

class TCA_Channel:
    """
    Utility class for each channel on the TCA multiplexer.
    
    Designed to be treated as an I2C bus, but transparently switches the Mux channel
    before doing read/writes
    """

    def __init__(self, chan: int, tca: "TCA"):
        self.chan = chan
        self.tca = tca

    def scan(self):
        self.tca.select_chan(self.chan)
        return self.tca.bus.scan()

    def readfrom_mem_into(self, addr: int, memaddr: int, buf, *, addrsize: int = 8) -> None:
        self.tca.select_chan(self.chan)
        return self.tca.bus.readfrom_mem_into(addr, memaddr, buf, addrsize=addrsize)

    def readfrom_into(self, addr: int, buf, stop: bool = True) -> None:
        self.tca.select_chan(self.chan)
        return self.tca.bus.readfrom_into(addr, buf, stop)

    def readfrom_mem(self, addr: int, memaddr: int, nbytes: int, *, addrsize: int = 8) -> bytes:
        self.tca.select_chan(self.chan)
        return self.tca.bus.readfrom_mem(addr, memaddr, nbytes, addrsize=addrsize)

    def writeto_mem(self, addr: int, memaddr: int, buf, *, addrsize: int = 8) -> None:
        self.tca.select_chan(self.chan)
        return self.tca.bus.writeto_mem(addr, memaddr, buf, addrsize=addrsize)

    def writeto(self, addr: int, buf, stop: bool = True) -> int:
        self.tca.select_chan(self.chan)
        return self.tca.bus.writeto(addr, buf, stop)

    def writevto(self, addr: int, vector, stop: bool = True) -> int:
        self.tca.select_chan(self.chan)
        return self.tca.bus.writevto(addr, vector, stop)

    def start(self) -> None:
        self.tca.select_chan(self.chan)
        return self.tca.bus.start()

    def readfrom(self, addr: int, nbytes: int, stop: bool = True) -> bytes:
        self.tca.select_chan(self.chan)
        return self.tca.bus.readfrom(addr, nbytes, stop)

    def readinto(self, buf, nack: bool = True) -> None:
        self.tca.select_chan(self.chan)
        return self.tca.bus.readinto(buf, nack)

    def stop(self) -> None:
        self.tca.select_chan(self.chan)
        return self.tca.bus.stop()

    def write(self, buf) -> int:
        self.tca.select_chan(self.chan)
        return self.tca.bus.write(buf)