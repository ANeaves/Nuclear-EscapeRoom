import sys
import struct
from framebuf import FrameBuffer, MONO_HLSB

class ImageBuffer:


    def __init__(self, filename: str) -> None:
        with open(filename, "rb") as f:
            contents = bytearray(f.read())

        offset = struct.unpack("I", contents[10:14])[0]
        fileSize = struct.unpack("I", contents[2:6])[0]
        self.width = struct.unpack("I", contents[18:22])[0]
        self.height = struct.unpack("I", contents[22:26])[0]
        num_colours = struct.unpack("I", contents[46:50])[0]
        print(f"Filesize: {fileSize}")
        print(f"Shape: ({self.width}, {self.height})")
        if num_colours > 2:
            raise ValueError("Only Works for 1 Bit bmps")

        self.data = contents[offset:fileSize]
        self.framebuf = FrameBuffer(self.data, self.width, self.height, MONO_HLSB)