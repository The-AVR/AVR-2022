import base64
import json
import threading
import time
from typing import Any, Optional

import adafruit_amg88xx
import board
import paho.mqtt.client as mqtt
from loguru import logger

INTERRUPTED = False


class Thermal(object):
    def __init__(self):
        self.mqtt_host = "mqtt"
        self.mqtt_port = 18830

        self.mqtt_client = mqtt.Client()

        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        self.topic_prefix = "vrc/thermal"

        self.topic_map = {
            "vrc/thermal/request_thermal_reading": self.request_thermal_reading,
        }

        print("connecting to thermal camera...")
        i2c = board.I2C()
        self.amg = adafruit_amg88xx.AMG88XX(i2c)
        print("Connected to Thermal Camera!")

    def on_message(
        self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage
    ) -> None:
        try:
            # logger.debug(f"{msg.topic}: {str(msg.payload)}")
            if msg.topic in self.topic_map:
                payload = json.loads(msg.payload)
                self.topic_map[msg.topic](payload)
        except Exception as e:
            logger.exception(f"Error handling message on {msg.topic}")
            print(e)

    def on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        rc: int,
        properties: Optional[mqtt.Properties] = None,
    ) -> None:
        logger.debug(f" THERAM: Connected with result code {rc}")
        for topic in self.topic_map.keys():
            logger.debug(f"THERMAL: Subscribed to: {topic}")
            client.subscribe(topic)

    def request_thermal_reading(self, msg: dict):
        reading = bytearray(64)
        i = 0
        for row in self.amg.pixels:
            for pix in row:
                pixasint = round(pix)
                bpix = pixasint.to_bytes(1, "big")
                reading[i] = bpix[0]
                i += 1
        base64Encoded = base64.b64encode(reading)
        # logger.debug(str(base64Encoded))
        base64_string = base64Encoded.decode("utf-8")

        thermalreading = {"reading": base64_string}
        self.mqtt_client.publish(
            f"{self.topic_prefix}/thermal_reading",
            json.dumps(thermalreading),
            retain=False,
            qos=0,
        )

    def request_thread(self):
        msg = {}
        while True:
            self.request_thermal_reading(msg)
            time.sleep(0.2)

    def run(self):
        # allows for graceful shutdown of any child threads
        self.mqtt_client.connect(host=self.mqtt_host, port=self.mqtt_port, keepalive=60)

        request_thread = threading.Thread(
            target=self.request_thread, args=(), daemon=True, name="request_thread"
        )
        request_thread.start()

        self.mqtt_client.loop_forever()


if __name__ == "__main__":
    thermal = Thermal()
    thermal.run()
