from bell.avr.mqtt.client import MQTTModule
from bell.avr.mqtt.payloads import (
    AvrFcmEventsPayload,
)
from bell.avr.utils.decorators import async_try_except, try_except

class FCMMQTTModule(MQTTModule):
    def __init__(self) -> None:
        super().__init__()
        self.mqtt_host = "127.0.0.1"

    @try_except()
    def _publish_event(self, name: str, payload: str = "") -> None:
        """
        Create and publish state machine event.
        """
        event = AvrFcmEventsPayload(
            name=name,
            payload=payload,
        )
        self.send_message("avr/fcm/events", event) #type: ignore