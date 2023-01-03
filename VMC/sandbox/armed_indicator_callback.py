from bell.avr.mqtt.client import MQTTModule
from bell.avr.mqtt.payloads import AvrFcmStatusPayload

from loguru import logger


class Sandbox(MQTTModule):
    def __init__(self) -> None:
        super().__init__()
        self.topic_map = {"avr/fcm/status": self.handle_status_message}

        self.is_armed: bool = False

        self.color_green = [0, 0, 255, 0]
        self.color_red = [0, 255, 0, 0]

    def handle_status_message(self, payload: AvrFcmStatusPayload) -> None:
        armed = payload["armed"]

        # check and see if the status has changed...
        if armed != self.is_armed:
            # if were armed, set the color to green, otherwise set to red
            if armed:
                color = self.color_green
            else:
                color = self.color_red

            self.send_message("avr/pcm/set_base_color", {"wrgb": color})
            self.is_armed = armed


if __name__ == "__main__":

    box = Sandbox()
    box.run()
