from __future__ import annotations

import json
from typing import Any

from app.lib.qt_icon import set_icon
from PySide6 import QtCore, QtGui, QtWidgets


class BaseTabWidget(QtWidgets.QWidget):

    pop_in: QtCore.SignalInstance = QtCore.Signal(object)  # type: ignore
    emit_message: QtCore.SignalInstance = QtCore.Signal(str, str)  # type: ignore

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        set_icon(self)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.pop_in.emit(self)
        return super().closeEvent(event)

    def send_message(self, topic: str, payload: Any) -> None:
        """
        Emit a Qt Signal for a message to be sent to the MQTT broker.
        """
        if not isinstance(payload, str):
            payload = json.dumps(payload)

        self.emit_message.emit(topic, payload)

    def process_message(self, topic: str, payload: str) -> None:
        """
        Process an incoming message from the MQTT broker.
        """
        raise NotImplementedError()
