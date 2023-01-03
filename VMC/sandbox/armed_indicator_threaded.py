from bell.avr.mqtt.client import MQTTModule
from bell.avr.mqtt.payloads import AvrFcmStatusPayload

from loguru import logger

import time
from threading import Thread


class Sandbox(MQTTModule):
    def __init__(self) -> None:
        super().__init__()
        self.topic_map = {
            "avr/fcm/status": self.handle_status_message,
            "avr/vio/confidence": self.handle_vio_message,
        }

        self.is_armed: bool = False
        self.confidence = -1

        self.color_green = [0, 0, 255, 0]
        self.color_red = [0, 255, 0, 0]
        self.color_yellow = [0, 252, 186, 3]

    def handle_status_message(self, payload: AvrFcmStatusPayload) -> None:
        armed = payload["armed"]
        self.is_armed = armed

    def handle_vio_message(self, payload: dict) -> None:
        confidence = payload["tracker"]
        if confidence >= 0 and confidence <= 100:
            self.confidence = confidence

    def loop(self):
        while True:
            # set the color according to our conditions
            color = self.color_red
            if self.is_armed:
                color = self.color_green
                if self.confidence < 75:
                    color = self.color_yellow

            self.send_message("avr/pcm/set_base_color", {"wrgb": color})
            time.sleep(1)


if __name__ == "__main__":

    box = Sandbox()
    loop_thread = Thread(target=box.loop)
    loop_thread.setDaemon(True)
    loop_thread.start()
    box.run()
