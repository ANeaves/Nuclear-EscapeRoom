import sys
import struct
from framebuf import FrameBuffer, MONO_HLSB

class ImageBuffer:
    
    IMG_SIZE = (128*64)/8 # 8 pixels per byte

    def __init__(self, filename: str) -> None:
        with open(filename, "rb") as f:
            contents = bytearray(f.read())

        offset = struct.unpack("I", contents[10:14])
        fileSize = struct.unpack("I", contents[2:6])
        num_colours = struct.unpack("I", contents[46:50])
        print(f"Filesize: {fileSize}")
        if num_colours[0] > 2:
            raise ValueError("Only Works for 1 Bit bmps")

        self.data = contents[offset[0]:fileSize[0]]
        self.framebuf = FrameBuffer(self.data, 128, 64, MONO_HLSB)