import time

import serial
from mqtt_library import (
    MQTTModule,
    VrcPcmResetMessage,
    VrcPcmSetBaseColorMessage,
    VrcPcmSetLaserOffMessage,
    VrcPcmSetLaserOnMessage,
    VrcPcmSetServoMaxMessage,
    VrcPcmSetServoMinMessage,
    VrcPcmSetServoOpenCloseMessage,
    VrcPcmSetServoPctMessage,
    VrcPcmSetTempColorMessage,
)
from pcc_library import PeripheralControlComputer


class PeripheralControlModule(MQTTModule):
    def __init__(self, port: str, baud_rate: int):
        super().__init__()

        # PCC connection
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = baud_rate
        self.ser.open()

        self.pcc = PeripheralControlComputer(self.ser)

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

    def run(self) -> None:
        super().run_non_blocking()

        while True:
            while self.ser.in_waiting > 0:
                self.ser.read(1)
            time.sleep(0.01)

    def set_base_color(self, payload: VrcPcmSetBaseColorMessage) -> None:
        wrgb = payload["wrgb"]
        self.pcc.set_base_color(wrgb=list(wrgb))

    def set_temp_color(self, payload: VrcPcmSetTempColorMessage) -> None:
        wrgb = payload["wrgb"]
        time = payload.get("time", 0.5)  # default of 0.5 seconds
        self.pcc.set_temp_color(wrgb=list(wrgb), time=time)

    def set_servo_open_close(self, payload: VrcPcmSetServoOpenCloseMessage) -> None:
        servo = payload["servo"]
        action = payload["action"]
        self.pcc.set_servo_open_close(servo, action)

    def set_servo_min(self, payload: VrcPcmSetServoMinMessage) -> None:
        servo = payload["servo"]
        min_pulse = payload["min_pulse"]
        self.pcc.set_servo_min(servo, min_pulse)

    def set_servo_max(self, payload: VrcPcmSetServoMaxMessage) -> None:
        servo = payload["servo"]
        max_pulse = payload["max_pulse"]
        self.pcc.set_servo_max(servo, max_pulse)

    def set_servo_pct(self, payload: VrcPcmSetServoPctMessage) -> None:
        servo = payload["servo"]
        percent = payload["percent"]
        self.pcc.set_servo_pct(servo, percent)

    def set_laser_on(self, payload: VrcPcmSetLaserOnMessage) -> None:
        self.pcc.set_laser_on()

    def set_laser_off(self, payload: VrcPcmSetLaserOffMessage) -> None:
        self.pcc.set_laser_off()

    def reset(self, payload: VrcPcmResetMessage) -> None:
        self.pcc.reset_vrc_peripheral()


if __name__ == "__main__":
    pcm = PeripheralControlModule("/dev/ttyACM0", 115200)
    pcm.run()
