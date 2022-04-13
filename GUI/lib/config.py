import json
import os
import sys
from typing import Any

if getattr(sys, "frozen", False):
    DATA_DIR = sys._MEIPASS  # type: ignore
    ROOT_DIR = os.path.dirname(sys.executable)
else:
    DATA_DIR = os.path.join(os.path.dirname(__file__), "..")
    ROOT_DIR = DATA_DIR

ROOT_DIR = os.path.abspath(ROOT_DIR)
DATA_DIR = os.path.abspath(DATA_DIR)


class _Config:
    config_file = os.path.join(ROOT_DIR, "settings.json")

    def __read(self) -> dict:
        if not os.path.isfile(self.config_file):
            return {}

        with open(self.config_file) as fp:
            return json.load(fp)

    def __write(self, data: dict) -> None:
        with open(self.config_file, "w") as fp:
            json.dump(data, fp)

    def __get(self, key: str, default: Any = None) -> Any:
        data = self.__read()
        if key in data:
            return data[key]
        return default

    def __set(self, key: str, value: Any) -> None:
        data = self.__read()
        data[key] = value
        self.__write(data)

    @property
    def mqtt_host(self) -> str:
        return self.__get("mqtt_host", "")

    @mqtt_host.setter
    def mqtt_host(self, value: str) -> None:
        return self.__set("mqtt_host", value)

    @property
    def mqtt_port(self) -> int:
        return self.__get("mqtt_port", 18830)

    @mqtt_port.setter
    def mqtt_port(self, value: int) -> None:
        return self.__set("mqtt_port", value)

    @property
    def serial_port(self) -> str:
        return self.__get("serial_port", "")

    @serial_port.setter
    def serial_port(self, value: str) -> None:
        return self.__set("serial_port", value)

    @property
    def serial_baud_rate(self) -> int:
        return self.__get("serial_baud_rate", 115200)

    @serial_baud_rate.setter
    def serial_baud_rate(self, value: int) -> None:
        return self.__set("serial_baud_rate", value)

    @property
    def mavlink_host(self) -> str:
        return self.__get("mavlink_host", "")

    @mavlink_host.setter
    def mavlink_host(self, value: str) -> None:
        return self.__set("mavlink_host", value)

    @property
    def mavlink_port(self) -> int:
        return self.__get("mavlink_port", 5670)

    @mavlink_port.setter
    def mavlink_port(self, value: int) -> None:
        return self.__set("mavlink_port", value)


config = _Config()
