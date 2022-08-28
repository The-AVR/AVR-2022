import time
import threading
from typing import Union, List
from .monitor import LEDAnimator, Monitor, STATE

# TODO - dont like this import mech. find a better way
import sys
sys.path.append("..") # Adds higher directory to python modules path.
from utilities.avr_pixel import clamp, rgb2int, int2rgb

class ApriltagMonitor(Monitor):
    def __init__(self, led_index: int, nominal_color: Union[List[int], int]):
        super().__init__(led_index, nominal_color)

        self.topic_map = {
            "avr/apriltags/c/status": self.apriltags_c_status_handler,
        }

        self.last_update: float = 0.0

        self._current_frames_processed: int = 0
        self._previous_frames_processed: int = 0

    @property
    def previous_frames_processed(self):
        return self._previous_frames_processed

    @property
    def current_frames_processed(self):
        return self._current_frames_processed

    @current_frames_processed.setter
    def current_frames_processed(self, value: int):
        self._previous_frames_processed = self._current_frames_processed
        self._current_frames_processed = value

    def apriltags_c_status_handler(self, payload: dict):
        self.current_frames_processed = int(payload["status"]["num_frames_processed"])
        self.last_update = float(payload["status"]["last_update"])

    def run(self):
        while True:

            # check various error conditions and update the state accordingly
            # these statements should be written such that you only hit a single
            # if block, so that the correct state is chosen

            # if we havent heard from the module in 5 seconds, we're dead
            if time.time() - self.last_update > 5:
                self.state = STATE.DEAD

            # if we got updates, but the module hasnt processed a frame in over a second, we're critical
            if (
                self.current_frames_processed - self.previous_frames_processed < 1
                and time.time() - self.last_update > 1
            ):
                self.state = STATE.CRITICAL

            # if we are getting regular updates and the module is processing frames, we're probably nominal
            if (
                time.time() - self.last_update < 1
                and self.current_frames_processed - self.previous_frames_processed > 1
            ):
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
