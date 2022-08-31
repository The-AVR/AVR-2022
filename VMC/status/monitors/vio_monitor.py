import time
import threading
from typing import Union, List
from .monitor import LEDAnimator, Monitor, STATE

# TODO - dont like this import mech. find a better way
import sys

sys.path.append("..")  # Adds higher directory to python modules path.
from utilities.avr_pixel import clamp, rgb2int, int2rgb

class VIOMonitor(Monitor):
    def __init__(self, led_index: int, nominal_color: Union[List[int], int]):
        super().__init__("vio", led_index, nominal_color)

        self.topic_map = {
            "avr/vio/velocity/ned": self.vio_vel_ned_handler
        }

        self.last_vel_update = 0
        self.last_update = 0

    def vio_vel_ned_handler(self, payload: dict):
        self.last_vel_update = time.time()
        self.last_update = time.time()

    def get_telemetry(self) -> dict:
        return {
            "led_color": self.led_manager.current_color,
            "state": self.state.name,
            "last_vel_update":self.last_vel_update
        }

    def run(self):
        while True:

            # check various error conditions and update the state accordingly
            # these statements should be written such that you only hit a single
            # if block, so that the correct state is chosen

            # if we havent heard from the module in 5 seconds, we're dead
            if time.time() - self.last_update > 5:
                self.state = STATE.DEAD

            if time.time() - self.last_vel_update < 1:
                self.state = STATE.NOMINAL

            # update the LED color
            self.led_manager.update_led_color(self.state)
            time.sleep(0.1)

    def initialize(self):
        # TODO - make this implementation more thread-safe
        # because we arent really doing mission critical things here,
        # exploited race conditions wont really cause harm
        self.thread = threading.Thread(target=self.run, args=(), daemon=True)
        self.thread.start()
        return self.thread