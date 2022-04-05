import math
import colour
import numpy as np
import pygame
from scipy.interpolate import griddata


class VRC_ThermalView(object):
    def __init__(self) -> None:
        # low range of the sensor (this will be blue on the screen)
        self.MINTEMP = 20.0

        # high range of the sensor (this will be red on the screen)
        self.MAXTEMP = 32.0

        # how many color values we can have
        self.COLORDEPTH = 1024

        # pylint: disable=no-member
        pygame.init()
        # pylint: enable=no-member

        # pylint: disable=invalid-slice-index
        self.points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
        self.grid_x, self.grid_y = np.mgrid[0:7:32j, 0:7:32j]
        # pylint: enable=invalid-slice-index

        # sensor is an 8x8 grid so lets do a square
        self.height = 512
        self.width = 512

        # the list of colors we can choose from
        self.blue = colour.Color("indigo")
        self.colors = list(self.blue.range_to(colour.Color("red"), self.COLORDEPTH))

        # create the array of colors
        self.colors = [
            (int(c.red * 255), int(c.green * 255), int(c.blue * 255))
            for c in self.colors
        ]

        self.displayPixelWidth = self.width / 30
        self.displayPixelHeight = self.height / 30

        self.lcd = pygame.display.set_mode((self.width, self.height))

        self.lcd.fill((255, 0, 0))

        pygame.display.update()
        pygame.mouse.set_visible(False)

        self.lcd.fill((0, 0, 0))
        pygame.display.update()

    # some utility functions
    def constrain(self, val: int, min_val: int, max_val: int) -> int:
        return min(max_val, max(min_val, val))

    def map_value(
        self, x: int, in_min: int, in_max: int, out_min: int, out_max: int
    ) -> float:
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def update(self, pixels: list[int]) -> None:
        # (p, 0, 255, 15.0, 40.0)
        # read the pixels
        # pixels = []
        # for row in self.sensor.pixels:
        #    pixels = pixels + row

        pixels = [
            self.map_value(p, self.MINTEMP, self.MAXTEMP, 0, self.COLORDEPTH - 1)
            for p in pixels
        ]

        bicubic = griddata(
            self.points, pixels, (self.grid_x, self.grid_y), method="cubic"
        )

        # draw everything
        for ix, row in enumerate(bicubic):
            for jx, pixel in enumerate(row):
                pygame.draw.rect(
                    self.lcd,
                    self.colors[self.constrain(int(pixel), 0, self.COLORDEPTH - 1)],
                    (
                        self.displayPixelHeight * ix,
                        self.displayPixelWidth * jx,
                        self.displayPixelHeight,
                        self.displayPixelWidth,
                    ),
                )

        pygame.display.update()
