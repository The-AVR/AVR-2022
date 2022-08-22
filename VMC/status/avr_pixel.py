import itertools
import time
from typing import List, Union

import board
import neopixel_spi as neopixel

NUM_PIXELS = 12
PIXEL_ORDER = neopixel.GRB

# RGB
COLORS = (0xFF0000, 0x00FF00, 0x0000FF)
CLR_PURPLE = 0x6A0DAD
CLR_AQUA = 0x00FFFF
CLR_ORANGE = 0xF5A506
CLR_YELLOW = 0xe3db00
CLR_BLUE = 0x0000FF
CLR_BLACK = 0x000000
CLR_GREEN = 0x00FF00
CLR_RED = 0xFF0000

VIO_LED = 1
PCC_LED = 2
THERMAL_LED = 3
FCC_LED = 4
APRIL_LED = 5

DELAY = 0.1


class AVR_PIXEL(object):
    def __init__(self):
        self.spi = board.SPI()
        self.pixels = neopixel.NeoPixel_SPI(
            self.spi, NUM_PIXELS, pixel_order=PIXEL_ORDER, auto_write=False
        )

    def clamp(
        self,
        n: Union[float, int],
        min_val: Union[float, int],
        max_val: Union[float, int],
    ) -> Union[float, int]:
        return max(min(max_val, n), min_val)

    def rgb2int(self, color: List[int]) -> int:
        red = int(self.clamp(color[0], 0, 255)) << 16
        green = int(self.clamp(color[1], 0, 255)) << 8
        blue = int(self.clamp(color[2], 0, 255))

        return int(red + green + blue)

    def set_all_color(self, color: Union[List[int], int]) -> None:
        if isinstance(color, list):
            color = self.rgb2int(color)
        for i in range(NUM_PIXELS):
            self.pixels[i] = color
        self.pixels.show()

    def all_pixels_off(self) -> None:
        self.set_all_color(CLR_BLACK)

    def set_pixel_color(self, which_one: int, color: Union[List[int], int]) -> None:
        if isinstance(color, list):
            color = self.rgb2int(color)
        self.pixels[which_one] = color
        self.pixels.show()

    def light_show(self) -> None:
        for color, i in itertools.product(COLORS, range(NUM_PIXELS)):
            self.pixels[i] = color
            self.pixels.show()
            time.sleep(DELAY)
            self.pixels.fill(0)
