from loguru import logger
from mqtt_library import (
    MQTTModule,
    VrcFcmVelocityMessage,
    VrcPcmSetServoOpenCloseMessage,
)


class Sandbox(MQTTModule):
    def __init__(self) -> None:
        self.topic_map = {
            "vrc/fcm/velocity": self.show_velocity,
        }

    def show_velocity(self, payload: VrcFcmVelocityMessage) -> None:
        vx = payload["vX"]
        vy = payload["vY"]
        vz = payload["vZ"]
        v_ms = (vx, vy, vz)
        logger.debug(f"Velocity information: {v_ms} m/s")

    def open_servo(self) -> None:
        self.send_message(
            "vrc/pcm/set_servo_open_close", {"servo":0, "action": "open"},
        )


if __name__ == "__main__":
    box = Sandbox()
    box.run()
