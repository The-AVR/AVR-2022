import asyncio
import json
import queue
from typing import Any

import paho.mqtt.client as mqtt
from loguru import logger
from mavsdk import System

try:
    from fcc_library import FCC, PyMAVLinkAgent  # type: ignore
except ImportError:
    from .fcc_library import FCC, PyMAVLinkAgent


class FCCModule:
    def __init__(self):

        self.mqtt_host = "localhost"
        self.mqtt_port = 18830

        self.mqtt_client = mqtt.Client()

        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        self.command_queue = queue.Queue()
        self.mocap_queue = queue.Queue()
        self.offboard_ned_queue = queue.Queue()
        self.offboard_body_queue = queue.Queue()

        self.topic_prefix = "vrc"

        self.mqtt_topics = {
            f"{self.topic_prefix}/fusion/hil_gps": self.mocap_queue,
        }

    def on_message(
        self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage
    ) -> None:
        try:
            # logger.debug(f"{msg.topic}: {str(msg.payload)}")
            if msg.topic in self.mqtt_topics.keys():
                data = json.loads(msg.payload)
                self.mqtt_topics[msg.topic].put(data)
        except Exception as e:
            logger.exception(f"Error handling message on {msg.topic}")

    def on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        rc: int,
        properties: mqtt.Properties = None,
    ) -> None:
        logger.debug(f'Connected with result code {rc}')
        for topic in self.mqtt_topics.keys():
            logger.debug(f"FCCModule: Subscribed to: {topic}")
            client.subscribe(topic)

    # @decorators.async_try_except()
    async def run(self) -> None:
        """
        Main entry point.
        """

        # connect the MQTT client
        self.mqtt_client.connect(self.mqtt_host, self.mqtt_port)

        # start the MQTT loop
        self.mqtt_client.loop_start()

        # create the drone object
        drone = System()
        # create the FCC object
        self.fcc = FCC(
            drone,
            self.mqtt_client,
            self.command_queue,
            self.offboard_ned_queue,
            self.offboard_body_queue,
        )

        self.gps_fcc = PyMAVLinkAgent(self.mqtt_client, self.mocap_queue)
        # connect the drone
        await self.fcc.connect()

        asyncio.get_event_loop()

        logger.debug("Starting FCC Tasks")
        asyncio.gather(
            self.fcc.telemetry_tasks(),
            # self.fcc.offboard_tasks(),
            # self.fcc.action_dispatcher(),
            self.gps_fcc.run(),
        )

        while True:
            await asyncio.sleep(3)


if __name__ == "__main__":
    fcc = FCCModule()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fcc.run())
    loop.close()
