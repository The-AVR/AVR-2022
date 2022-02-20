# VRC Peripheral Python Library
# Written by Casey Hanner
import time
from struct import pack
from typing import Any, List, Literal, Optional, Union

import serial
from loguru import logger


class PeripheralControlComputer:
    def __init__(self, port: str, use_serial: bool = True) -> None:
        self.port = port

        self.PREAMBLE = (0x24, 0x50)

        self.HEADER_OUTGOING = (*self.PREAMBLE, 0x3C)
        self.HEADER_INCOMING = (*self.PREAMBLE, 0x3E)

        self.commands = {
            "SET_SERVO_OPEN_CLOSE": 0,
            "SET_SERVO_MIN": 1,
            "SET_SERVO_MAX": 2,
            "SET_SERVO_PCT": 3,
            "SET_BASE_COLOR": 4,
            "SET_TEMP_COLOR": 5,
            "RESET_VRC_PERIPH": 6,
            "CHECK_SERVO_CONTROLLER": 7,
        }

        self.use_serial = use_serial

        if self.use_serial:
            logger.debug("Opening serial port")
            self.ser = serial.Serial()
            self.ser.baudrate = 115200
            self.ser.port = self.port
            self.ser.open()

        else:
            logger.debug("VRCPeripheral: Serial Transmission is OFF")

        self.shutdown: bool = False

    def run(self) -> None:
        while not self.shutdown:
            if self.use_serial:
                while self.ser.in_waiting > 0:
                    print(self.ser.read(1), end="")

            time.sleep(0.01)

    def set_base_color(self, wrgb: List[int]) -> None:
        # wrgb + code = 5
        if len(wrgb) != 4:
            wrgb = [0, 0, 0, 0]

        for i, color in enumerate(wrgb):
            if not isinstance(color, int) or color > 255 or color < 0:
                wrgb[i] = 0

        command = self.commands["SET_BASE_COLOR"]
        data = self._construct_payload(command, 1 + len(wrgb), wrgb)

        if self.use_serial is True:
            self.ser.write(data)
        else:
            logger.debug("VRCPeripheral serial data: ")
            logger.debug(data)

    def set_temp_color(self, wrgb: List[int], time: float = 0.5) -> None:
        # wrgb + code = 5
        if len(wrgb) != 4:
            wrgb = [0, 0, 0, 0]

        for i, color in enumerate(wrgb):
            if not isinstance(color, int) or color > 255 or color < 0:
                wrgb[i] = 0

        command = self.commands["SET_TEMP_COLOR"]
        time_bytes = self.list_pack("<f", time)
        data = self._construct_payload(
            command, 1 + len(wrgb) + len(time_bytes), wrgb + time_bytes
        )

        if self.use_serial is True:
            self.ser.write(data)
        else:
            logger.debug("VRCPeripheral serial data: ")
            logger.debug(data)

    def set_servo_open_close(
        self, servo: int, action: Literal["open", "close"]
    ) -> None:
        valid_command = False

        command = self.commands["SET_SERVO_OPEN_CLOSE"]
        data = []

        # 128 is inflection point, over 128 == open; under 128 == close

        if action == "close":
            data = [servo, 100]
            valid_command = True

        elif action == "open":
            data = [servo, 150]
            valid_command = True

        if valid_command:
            if self.use_serial is True:
                length = 3  # command + servo + action
                self.ser.write(self._construct_payload(command, length, data))
            else:
                logger.debug("VRCPeripheral serial data: ")
                logger.debug(data)

    def set_servo_min(self, servo: int, minimum: float) -> None:
        valid_command = False

        data = []

        if isinstance(minimum, (float, int)) and minimum < 1000 and minimum > 0:
            valid_command = True
            data = [servo, minimum]

        if valid_command:
            command = self.commands["SET_SERVO_MIN"]
            if self.use_serial is True:
                length = 3  # command + servo + min pwm
                self.ser.write(self._construct_payload(command, length, data))
            else:
                logger.debug("VRCPeripheral serial data: ")
                logger.debug(data)

    def set_servo_max(self, servo: int, maximum: float) -> None:
        valid_command = False

        data = []

        if isinstance(maximum, (float, int)) and maximum < 1000 and maximum > 0:
            valid_command = True
            data = [servo, maximum]

        if valid_command:
            command = self.commands["SET_SERVO_MAX"]
            if self.use_serial is True:
                length = 3  # command + servo + min pwm
                self.ser.write(self._construct_payload(command, length, data))
            else:
                logger.debug("VRCPeripheral serial data: ")
                logger.debug(data)

    def set_servo_pct(self, servo: int, pct: float) -> None:
        valid_command = False

        data = []

        if isinstance(pct, (float, int)) and pct < 100 and pct > 0:
            valid_command = True
            data = [servo, int(pct)]

        if valid_command:
            command = self.commands["SET_SERVO_PCT"]
            if self.use_serial is True:
                length = 3  # command + servo + percent
                self.ser.write(self._construct_payload(command, length, data))
            else:
                logger.debug("VRCPeripheral serial data: ")
                logger.debug(data)

    def reset_vrc_peripheral(self) -> None:
        command = self.commands["RESET_VRC_PERIPH"]
        if self.use_serial:

            length = 1  # just the reset command

            self.ser.write(self._construct_payload(command, length))
            self.ser.close()
            # wait for the VRC_Periph to reboot
            time.sleep(5)

            # try to reconnect
            self.ser.open()
        else:
            logger.debug("VRCPeripheral reset triggered (NO SERIAL)")

    def check_servo_controller(self) -> None:
        if self.use_serial:
            command = self.commands["CHECK_SERVO_CONTROLLER"]
            length = 1
            self.ser.write(self._construct_payload(command, length))

    def _construct_payload(
        self, code: int, size: int = 0, data: Optional[list] = None
    ) -> bytes:
        # [$][P][>][LENGTH-HI][LENGTH-LOW][DATA][CRC]
        payload = bytes()

        if data is None:
            data = []

        new_data = (
            ("<3b", self.HEADER_OUTGOING),
            (">H", [size]),
            ("<B", [code]),
            ("<%dB" % len(data), data),
        )

        for section in new_data:
            payload += pack(section[0], *section[1])

        crc = self.calc_crc(payload, len(payload))

        payload += pack("<B", crc)

        return payload

    def list_pack(self, bit_format: Union[str, bytes], value: Any) -> List[int]:
        bytez = pack(bit_format, value)

        return list(bytez)

    def crc8_dvb_s2(self, crc: int, a: int) -> int:
        # https://stackoverflow.com/a/52997726
        crc ^= a
        for _ in range(8):
            crc = ((crc << 1) ^ 0xD5) % 256 if crc & 0x80 else (crc << 1) % 256
        return crc

    def calc_crc(self, string: bytes, length: int) -> int:
        crc = 0
        for i in range(length):
            crc = self.crc8_dvb_s2(crc, string[i])
        return crc
