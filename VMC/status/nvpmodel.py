import subprocess
from typing import Union

from loguru import logger


class NVPModel(object):
    def __init__(self):
        self.initialized = False

    def initialize(self):
        self.set_nvpmodel("0")
        self.initialized = True

    def set_nvpmodel(self, mode: str) -> None:
        # Initialize power mode status
        cmd = ["/app/nvpmodel", "--verbose", "-f", "/app/nvpmodel.conf", "-m", mode]
        try:
            subprocess.check_call(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            logger.exception(
                f"Command '{e.cmd}' return with error ({e.returncode}): {e.output}"
            )

    def check_nvpmodel_maxn(self) -> Union[bool, None]:
        cmd = ["/app/nvpmodel", "-f", "/app/nvpmodel.conf", "-q"]
        try:
            result = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode(
                "utf-8"
            )
            return "MAXN" in result
        except subprocess.CalledProcessError as e:
            logger.exception(
                f"Command '{e.cmd}' return with error ({e.returncode}): {e.output}"
            )
