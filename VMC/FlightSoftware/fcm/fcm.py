import asyncio
import json
import queue
from typing import Any

import paho.mqtt.client as mqtt
from fcc_library import FlightControlComputer, PyMAVLinkAgent
from loguru import logger
from mavsdk import System
from mqtt_library import MQTTModule


class FlightControlModule(MQTTModule):
    def __init__(self):
        super().__init__()

        # data queues
        self.command_queue = queue.Queue()
        self.hilgps_queue = queue.Queue()
        self.offboard_ned_queue = queue.Queue()
        self.offboard_body_queue = queue.Queue()

        # MQTT topics
        self.topic_map = {
            "vrc/fusion/hil_gps": self.hilgps_queue_handler,
        }

    def hilgps_queue_handler(self, payload: dict) -> None:
        self.hilgps_queue.put(payload)

    async def run(self) -> None:
        # connect the MQTT client
        self.mqtt_client.connect(self.mqtt_host, self.mqtt_port)

        # start the MQTT loop
        self.mqtt_client.loop_start()

        # create the mavsdk system object
        drone = System()

        # create the FCC objects
        self.fcc = FlightControlComputer(
            drone,
            self.mqtt_client,
            self.command_queue,
            self.offboard_ned_queue,
            self.offboard_body_queue,
        )

        self.gps_fcc = PyMAVLinkAgent(self.mqtt_client, self.hilgps_queue)

        # connect to the FCC
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
    fcc = FlightControlModule()
    asyncio.run(fcc.run())
