
from PySide6 import QtWidgets

from ..base import BaseTabWidget
from .mqtt import MQTTConnectionWidget
from .serial import SerialConnectionWidget


class MainConnectionWidget(BaseTabWidget):
    """
    This manages connections to all the external services
    """

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

        self.setWindowTitle("Connections")

    def build(self) -> None:
        """
        Build the GUI layout
        """
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)

        mqtt_groupbox = QtWidgets.QGroupBox("MQTT")
        mqtt_layout = QtWidgets.QVBoxLayout()
        mqtt_groupbox.setLayout(mqtt_layout)

        self.mqtt_connection_widget = MQTTConnectionWidget(self)
        self.mqtt_connection_widget.build()
        mqtt_layout.addWidget(self.mqtt_connection_widget)

        mqtt_groupbox.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        layout.addWidget(mqtt_groupbox)

        serial_groupbox = QtWidgets.QGroupBox("Serial")
        serial_layout = QtWidgets.QVBoxLayout()
        serial_groupbox.setLayout(serial_layout)

        self.serial_connection_widget = SerialConnectionWidget(self)
        self.serial_connection_widget.build()
        serial_layout.addWidget(self.serial_connection_widget)

        serial_groupbox.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        layout.addWidget(serial_groupbox)
