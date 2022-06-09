import itertools
import signal
import subprocess
import time
from typing import Any, Dict, Optional, Tuple

import board
import neopixel_spi as neopixel
import paho.mqtt.client as mqtt
from bell.vrc.mqtt.client import MQTTModule
from loguru import logger

NUM_PIXELS = 12
PIXEL_ORDER = neopixel.GRB

# RGB
COLORS = (0xFF0000, 0x00FF00, 0x0000FF)
CLR_PURPLE = 0x6A0DAD
CLR_AQUA = 0x00FFFF
CLR_ORANGE = 0xF5A506
CLR_YELLOW = 0xC1E300
CLR_BLUE = 0x001EE3
CLR_BLACK = 0x000000

VIO_LED = 1
PCC_LED = 2
THERMAL_LED = 3
FCC_LED = 4
APRIL_LED = 5

DELAY = 0.1


class StatusModule(MQTTModule):
    def __init__(self):
        super().__init__()

        self.initialized = False

        self.topic_map = {
            "vrc/status/light/pcm": self.light_status,
            "vrc/status/light/vio": self.light_status,
            "vrc/status/light/apriltags": self.light_status,
            "vrc/status/light/fcm": self.light_status,
            "vrc/status/light/thermal": self.light_status,
        }

        self.spi = board.SPI()
        self.pixels = neopixel.NeoPixel_SPI(
            self.spi, NUM_PIXELS, pixel_order=PIXEL_ORDER, auto_write=False
        )

        # set up handling for turning off the lights on docker shutdown
        self.run_status_check = True
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

        self.red_status_all()

    def on_message(
        self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage
    ) -> None:
        # run this function on every message recieved before processing topic map
        self.check_status(msg.topic)
        super().on_message(client, userdata, msg)

    def on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        rc: Any,
        properties: Optional[mqtt.Properties] = None,
    ) -> None:
        super().on_connect(client, userdata, rc, properties)
        # additionally subscribe to all topics
        client.subscribe("vrc/#")

    def set_cpu_status(self) -> None:
        # Initialize power mode status
        cmd = ["/app/nvpmodel", "--verbose", "-f", "/app/nvpmodel.conf", "-m", "0"]
        try:
            subprocess.check_call(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            logger.exception(
                f"Command '{e.cmd}' return with error ({e.returncode}): {e.output}"
            )

    def check_status(self, topic: str) -> None:
        lookup: Dict[str, Tuple[int, int]] = {
            "vrc/vio": (VIO_LED, CLR_PURPLE),
            "vrc/pcm": (PCC_LED, CLR_AQUA),
            "vrc/fcm": (FCC_LED, CLR_ORANGE),
            "vrc/thermal": (THERMAL_LED, CLR_BLUE),
            "vrc/apriltags": (APRIL_LED, CLR_YELLOW),
        }

        for key, value in lookup.items():
            if topic.startswith(key):
                self.light_up(*value)

    def red_status_all(self) -> None:
        for i in range(NUM_PIXELS):
            self.pixels[i] = COLORS[0]
        self.pixels.show()

    def all_off(self) -> None:
        for i in range(NUM_PIXELS):
            self.pixels[i] = CLR_BLACK
        self.pixels.show()

    def light_up(self, which_one: int, color: int) -> None:
        self.pixels[which_one] = color
        self.pixels.show()

    def light_status(self, payload: Any) -> None:
        for color, i in itertools.product(COLORS, range(NUM_PIXELS)):
            self.pixels[i] = color
            self.pixels.show()
            time.sleep(DELAY)
            self.pixels.fill(0)

    def status_check(self) -> None:
        if not self.initialized:
            self.set_cpu_status()
            self.initialized = True

        cmd = ["/app/nvpmodel", "-f", "/app/nvpmodel.conf", "-q"]
        try:
            result = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode(
                "utf-8"
            )
            self.pixels[0] = COLORS[1] if "MAXN" in result else COLORS[0]
            self.pixels.show()
        except subprocess.CalledProcessError as e:
            logger.exception(
                f"Command '{e.cmd}' return with error ({e.returncode}): {e.output}"
            )

    def run(self) -> None:
        self.run_non_blocking()

        while self.run_status_check:
            self.status_check()
            time.sleep(1)
        self.all_off()

    def exit_gracefully(self, *args) -> None:
        self.run_status_check = False


if __name__ == "__main__":
    status = StatusModule()
    status.run()
