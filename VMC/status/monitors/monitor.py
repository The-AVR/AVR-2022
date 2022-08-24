from enum import Enum
from os import curdir
from typing import List, Union
import time
from VMC.status.utilities.avr_pixel import int2rgb, rgb2int, clamp


class STATE(Enum):
    NOMINAL = 1
    DEGRADED = 2
    CRITICAL = 3
    DEAD = 4


class LEDAnimator(object):
    def __init__(self, led_index: int, nominal_color: Union[List[int], int]):
        self.led_index = led_index
        if isinstance(nominal_color, int):
            nominal_color = int2rgb(nominal_color)
        self.nominal_color = nominal_color
        self.critical_color: List = [255, 0, 0]
        self.dead_color: List = [255, 0, 0]

        self._current_color: List = [0, 0, 0]
        self.last_color_change: float = time.time()

    @property
    def current_color(self):
        return self._current_color

    @current_color.setter
    def current_color(self, color: Union[List[int], int]):
        if isinstance(color, int):
            color = int2rgb(color)
        self._current_color = color
        self.last_color_change = time.time()

    def update_led_color(self, state):
        if state == STATE.NOMINAL:
            if self.current_color != self.nominal_color:
                self.current_color = self.nominal_color
        elif state == STATE.DEGRADED:
            # if the color hasnt changed in over half a second
            if time.time() - self.last_color_change > 0.5:
                # its time for a color change
                if self.current_color == self.nominal_color:
                    self.current_color = self.dead_color
                elif self.current_color == self.dead_color:
                    self.current_color = self.nominal_color
                else:
                    self.current_color = self.dead_color
        elif state == STATE.CRITICAL:
            # if the color hasnt changed in over .1 a second
            if time.time() - self.last_color_change > 0.1:
                # its time for a color change
                if self.current_color == self.dead_color:
                    self.current_color = [0, 0, 0]
                elif self.current_color == [0, 0, 0]:
                    self.current_color = self.dead_color
                else:
                    self.current_color = self.dead_color
        elif state == STATE.DEAD:
            if self.current_color != self.dead_color:
                self.current_color = self.dead_color
        else:
            raise ValueError("The LED animator has been handed an unknown state type")


class Monitor(object):
    def __init__(self, led_index: int, nominal_color: Union[List[int], int]):
        self.state = STATE.DEAD
        self.led_manager = LEDAnimator(led_index, nominal_color)
        self.topic_map: dict = {}
