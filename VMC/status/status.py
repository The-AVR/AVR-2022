import signal
import time
from typing import Any, Dict, Tuple

import avr_pixel
import nvpmodel
import paho.mqtt.client as mqtt
from bell.avr.mqtt.client import MQTTModule

CLR_PURPLE = 0x6A0DAD
CLR_AQUA = 0x00FFFF
CLR_ORANGE = 0xF5A506
CLR_YELLOW = 0xC1E300
CLR_BLUE = 0x001EE3
CLR_BLACK = 0x000000
CLR_GREEN = 0xFF5733
CLR_RED = 0xFF0000

NVPMODEL_LED = 0
VIO_LED = 1
PCC_LED = 2
THERMAL_LED = 3
FCC_LED = 4
APRIL_LED = 5


class StatusModule(MQTTModule):
    def __init__(self):
        super().__init__()

        self.topic_map = {
            # "avr/status/light/pcm": self.light_status,
            # "avr/status/light/vio": self.light_status,
            # "avr/status/light/apriltags": self.light_status,
            # "avr/status/light/fcm": self.light_status,
            # "avr/status/light/thermal": self.light_status,
            "avr/apriltags/c/status": self.apriltags_state,
        }

        self.nvpmodel = nvpmodel.NVPModel()
        self.pixels = avr_pixel.AVR_PIXEL()

        # set up handling for turning off the lights on docker shutdown
        self.enabled = True
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

        # set all the LEDs to red
        self.pixels.set_all_color(CLR_RED)

    def on_message(
        self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage
    ) -> None:
        # run this function on every message recieved before processing topic map
        self.process_status_update(msg.topic)
        super().on_message(client, userdata, msg)

    def on_connect(
        self, client: mqtt.Client, userdata: Any, flags: dict, rc: int
    ) -> None:
        super().on_connect(client, userdata, flags, rc)
        # additionally subscribe to all topics
        # TODO - its generally not a good idea to subscribe to everything
        # TODO - create dedicated status topics and sub to those
        client.subscribe("avr/#")

    def apriltags_state(self, payload: dict) -> None:
        # TODO - add state history so that the if statements can be compared to historical values to ensure the module is operating
        print(payload)
        print(type(payload))
        # print(int(payload["status"]["num_frames_processed"]))
        # print(float(payload["status"]["last_update_time"]))

        # if (int(payload["status"]["num_frames_processed"]) > 1) and (
        #     float(payload["status"]["last_update_time"]) - time.time() < 5
        # ):
        #     self.pixels.set_pixel_color(APRIL_LED, CLR_YELLOW)
        # else:
        #     self.pixels.set_pixel_color(APRIL_LED, CLR_BLACK)

    def process_status_update(self, topic: str) -> None:
        """
        this function is run for every incoming message on the avr/# topic
        the logic is such that if ANY message comes in that starts with the below topics
        it will light up the associated pixel with its associated color
        """
        lookup: Dict[str, Tuple[int, int]] = {
            "avr/vio": (VIO_LED, CLR_PURPLE),
            "avr/pcm": (PCC_LED, CLR_AQUA),
            "avr/fcm": (FCC_LED, CLR_ORANGE),
            "avr/thermal": (THERMAL_LED, CLR_BLUE),
            # "avr/apriltags": (APRIL_LED, CLR_YELLOW), #we are overriding this one with a special handler
        }

        for key, value in lookup.items():
            if topic.startswith(key):
                self.pixels.set_pixel_color(value[0], value[1])

    def light_status(self, payload: dict) -> None:
        self.pixels.light_show()

    def nvpmodel_status_check(self) -> None:
        self.pixels.set_pixel_color(
            NVPMODEL_LED, CLR_GREEN if self.nvpmodel.check_nvpmodel_maxn() else CLR_RED
        )

    def run(self) -> None:
        self.run_non_blocking()
        self.nvpmodel.initialize()

        while self.enabled:
            self.nvpmodel_status_check()
            time.sleep(1)
        self.all_off()

    def exit_gracefully(self, *args) -> None:
        self.enabled = False


if __name__ == "__main__":
    status = StatusModule()
    status.run()
