from typing import List, Literal

from pcc_library import PeripheralControlComputer
from mqtt_library import MQTTModule


class PeripheralControlModule(MQTTModule):
    def __init__(self, serial_port: str):
        super().__init__()

        # PCC connection
        self.pcc = PeripheralControlComputer(serial_port)

        # MQTT topics
        self.topic_map = {
            "vrc/pcm/set_base_color": self.set_base_color,
            "vrc/pcm/set_temp_color": self.set_temp_color,
            "vrc/pcm/set_servo_open_close": self.set_servo_open_close,
            "vrc/pcm/set_servo_min": self.set_servo_min,
            "vrc/pcm/set_servo_max": self.set_servo_max,
            "vrc/pcm/set_servo_pct": self.set_servo_pct,
            "vrc/pcm/reset": self.reset,
        }

    def set_base_color(self, payload: dict) -> None:
        wrgb: List = payload["wrgb"]
        self.pcc.set_base_color(wrgb=wrgb)

    def set_temp_color(self, payload: dict) -> None:
        wrgb: List = payload["wrgb"]
        time: float = payload.get("time", 0.5)
        self.pcc.set_temp_color(wrgb=wrgb, time=time)

    def set_servo_open_close(self, payload: dict) -> None:
        servo: int = payload["servo"]
        action: Literal["open", "close"] = payload["action"]
        self.pcc.set_servo_open_close(servo, action)

    def set_servo_min(self, payload: dict) -> None:
        servo: int = payload["servo"]
        pulse: int = payload["min_pulse"]
        self.pcc.set_servo_min(servo, pulse)

    def set_servo_max(self, payload: dict) -> None:
        servo: int = payload["servo"]
        pulse: int = payload["max_pulse"]
        self.pcc.set_servo_max(servo, pulse)

    def set_servo_pct(self, payload: dict) -> None:
        servo: int = payload["servo"]
        percent: int = payload["percent"]
        self.pcc.set_servo_pct(servo, percent)

    def reset(self, payload: dict) -> None:
        self.pcc.reset_vrc_peripheral()


if __name__ == "__main__":
    pcm = PeripheralControlModule("/dev/ttyACM0")
    pcm.run()
