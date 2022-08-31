import signal
import time
from typing import Any, Dict, Tuple, List
from monitors.apriltag_monitor import ApriltagMonitor
from monitors.vio_monitor import VIOMonitor
from monitors.monitor import Monitor

import utilities.avr_pixel as avr_pixel
import utilities.nvpmodel as nvpmodel
import paho.mqtt.client as mqtt
from bell.avr.mqtt.client import MQTTModule
from loguru import logger
import json

CLR_PURPLE = 0x6A0DAD
CLR_AQUA = 0x00FFFF
CLR_ORANGE = 0xF5A506
CLR_YELLOW = 0xE3DB00
CLR_BLUE = 0x0000FF
CLR_BLACK = 0x000000
CLR_GREEN = 0x00FF00
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

        self.topic_map = {}

        self.monitors: List[Monitor] = []

        self.monitors.append(ApriltagMonitor(APRIL_LED, CLR_YELLOW))
        self.monitors.append(VIOMonitor(VIO_LED, CLR_PURPLE))

        for monitor in self.monitors:
            # start the run thread for the monitor
            monitor.initialize()
            # add the callbacks for the monitor
            if monitor.topic_map:
                self.topic_map.update(monitor.topic_map) #type: ignore
            else:
                logger.debug(f"Monitor {monitor.name} has no topic map")


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
        """
        On connection callback. Subscribes to MQTT topics in the topic map.
        """
        logger.debug(f"Connected with result {rc}")

        for topic in self.topic_map.keys():
            client.subscribe(topic)
            logger.debug(f"Subscribed to: {topic}")
        # additionally subscribe to all topics
        # TODO - its generally not a good idea to subscribe to everything
        # TODO - create dedicated status topics and sub to those
        client.subscribe("avr/#")

    def process_status_update(self, topic: str) -> None:
        """
        this function is run for every incoming message on the avr/# topic
        the logic is such that if ANY message comes in that starts with the below topics
        it will light up the associated pixel with its associated color
        """
        lookup: Dict[str, Tuple[int, int]] = {
            "avr/pcm": (PCC_LED, CLR_AQUA),
            "avr/fcm": (FCC_LED, CLR_ORANGE),
            "avr/thermal": (THERMAL_LED, CLR_BLUE),
        }

        for key, value in lookup.items():
            if topic.startswith(key):
                self.pixels.set_pixel_color(value[0], value[1])

    def nvpmodel_status_check(self) -> None:
        self.pixels.set_pixel_color(
            NVPMODEL_LED, CLR_GREEN if self.nvpmodel.check_nvpmodel_maxn() else CLR_RED
        )

    def run(self) -> None:
        self.run_non_blocking()
        self.nvpmodel.initialize()

        last_publish_time = time.time()

        while self.enabled:
            self.nvpmodel_status_check()
            for monitor in self.monitors:
                self.pixels.set_pixel_color(
                    monitor.led_manager.led_index, monitor.led_manager.current_color
                )
            if time.time() - last_publish_time > 1:
                now = time.time()
                self.send_message("avr/status/last_update", {"timestamp": now}) #type: ignore
                last_publish_time = now
                for monitor in self.monitors:
                    self.send_message(f"avr/status/monitor/{monitor.name}", monitor.get_telemetry() ) #type: ignore
            time.sleep(0.01)
        self.pixels.all_pixels_off()

    def exit_gracefully(self, *args) -> None:
        self.enabled = False


if __name__ == "__main__":
    status = StatusModule()
    status.run()
