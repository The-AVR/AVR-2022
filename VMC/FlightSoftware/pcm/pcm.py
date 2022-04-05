from mqtt_library import (
    MQTTModule,
    VRCPcmResetMessage,
    VRCPcmSetBaseColorMessage,
    VRCPcmSetServoMaxMessage,
    VRCPcmSetServoMinMessage,
    VRCPcmSetServoOpenCloseMessage,
    VRCPcmSetServoPctMessage,
    VRCPcmSetTempColorMessage,
    VRCPcmSetLaserOnMessage,
    VRCPcmSetLaserOffMessage,
)
from pcc_library import PeripheralControlComputer


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
            "vrc/pcm/set_laser_on": self.set_laser_on,
            "vrc/pcm/set_laser_off": self.set_laser_off,
            "vrc/pcm/set_servo_pct": self.set_servo_pct,
            "vrc/pcm/reset": self.reset,
        }

    def set_base_color(self, payload: VRCPcmSetBaseColorMessage) -> None:
        wrgb = payload["wrgb"]
        self.pcc.set_base_color(wrgb=list(wrgb))

    def set_temp_color(self, payload: VRCPcmSetTempColorMessage) -> None:
        wrgb = payload["wrgb"]
        time = payload.get("time", 0.5)  # default of 0.5 seconds
        self.pcc.set_temp_color(wrgb=list(wrgb), time=time)

    def set_servo_open_close(self, payload: VRCPcmSetServoOpenCloseMessage) -> None:
        servo = payload["servo"]
        action = payload["action"]
        self.pcc.set_servo_open_close(servo, action)

    def set_servo_min(self, payload: VRCPcmSetServoMinMessage) -> None:
        servo = payload["servo"]
        min_pulse = payload["min_pulse"]
        self.pcc.set_servo_min(servo, min_pulse)

    def set_servo_max(self, payload: VRCPcmSetServoMaxMessage) -> None:
        servo = payload["servo"]
        max_pulse = payload["max_pulse"]
        self.pcc.set_servo_max(servo, max_pulse)

    def set_servo_pct(self, payload: VRCPcmSetServoPctMessage) -> None:
        servo = payload["servo"]
        percent = payload["percent"]
        self.pcc.set_servo_pct(servo, percent)

    def set_laser_on(self, payload: VRCPcmSetLaserOnMessage) -> None:
        self.pcc.set_laser_on()

    def set_laser_off(self, payload: VRCPcmSetLaserOffMessage) -> None:
        self.pcc.set_laser_off()

    def reset(self, payload: VRCPcmResetMessage) -> None:
        self.pcc.reset_vrc_peripheral()


if __name__ == "__main__":
    pcm = PeripheralControlModule("/dev/ttyACM0")
    pcm.run()
