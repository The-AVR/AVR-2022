import json
import os
from typing import Any


class _Config:
    config_file = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "settings.json")
    )

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


config = _Config()
