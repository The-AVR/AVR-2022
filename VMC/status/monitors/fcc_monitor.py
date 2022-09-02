import time
import threading
from typing import Union, List
from loguru import logger
from .monitor import LEDAnimator, Monitor, STATE

# TODO - dont like this import mech. find a better way
import sys

sys.path.append("..")  # Adds higher directory to python modules path.
from utilities.avr_pixel import clamp, rgb2int, int2rgb


class FCCMonitor(Monitor):
    def __init__(self, led_index: int, nominal_color: Union[List[int], int]):
        super().__init__("fcc", led_index, nominal_color)

        self.topic_map = {
            "avr/fcm/status": self.fcm_status_handler,
        }

        self.last_update = 0
        self.last_status_update = 0
        self.fcm_mode = "UNKNOWN"
        self.fcm_armed = False

    def get_telemetry(self) -> dict:
        return {
            "led_color": self.led_manager.current_color,
            "state": self.state.name,
            "mode": self.fcm_mode,
            "armed": self.fcm_armed,
        }

    def fcm_status_handler(self, payload: dict):
        self.last_status_update = time.time()
        self.last_update = time.time()

        try:
            self.fcm_mode = payload["mode"]
            self.fcm_armed = payload["armed"]
        except:
            logger.warning("fcm status handler couldnt parse fcm status msg")
    def run(self):
        while True:

            # check various error conditions and update the state accordingly
            # these statements should be written such that you only hit a single
            # if block, so that the correct state is chosen

            # if we havent heard from the module in 5 seconds, we're dead
            if time.time() - self.last_update > 5:
                self.state = STATE.DEAD

            if time.time() - self.last_status_update < 1:
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
