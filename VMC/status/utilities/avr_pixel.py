import itertools
import time
from typing import List, Union

import board
import neopixel_spi as neopixel

def clamp(
    n: Union[float, int],
    min_val: Union[float, int],
    max_val: Union[float, int],
) -> Union[float, int]:
    return max(min(max_val, n), min_val)

def rgb2int(color: List[int]) -> int:
    red = int(clamp(color[0], 0, 255)) << 16
    green = int(clamp(color[1], 0, 255)) << 8
    blue = int(clamp(color[2], 0, 255))

    return int(red + green + blue)

def int2rgb(color: int) -> List[int]:
    red = (color & 0xFF0000) >> 16
    green = (color & 0x00FF00) >> 8
    blue = (color & 0x0000FF)
    return [red, green, blue]

class AVR_PIXEL(object):
    def __init__(self, num_pixels: int = 12):
        self.spi = board.SPI()
        self.num_pixels = num_pixels
        self.pixel_order = neopixel.GRB
        self.pixels = neopixel.NeoPixel_SPI(
            self.spi, self.num_pixels, pixel_order=self.pixel_order, auto_write=False
        )

    def set_all_color(self, color: Union[List[int], int]) -> None:
        if isinstance(color, list):
            color = self.rgb2int(color)
        for i in range(self.num_pixels):
            self.pixels[i] = color
        self.pixels.show()

    def all_pixels_off(self) -> None:
        self.set_all_color([0, 0, 0])

    def set_pixel_color(self, which_one: int, color: Union[List[int], int]) -> None:
        if isinstance(color, list):
            color = self.rgb2int(color)
        self.pixels[which_one] = color
        self.pixels.show()
