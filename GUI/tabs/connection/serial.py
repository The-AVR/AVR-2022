import threading
import time

from bell.vrc.serial.client import SerialLoop
from bell.vrc.serial.ports import list_serial_ports
from lib.config import config
from lib.enums import ConnectionState
from lib.widgets import IntLineEdit
from loguru import logger
from PySide6 import QtCore, QtGui, QtWidgets


class SerialClient(QtCore.QObject):
    # This class is a more convential client object that gets passed around.
    # There's much less threading complexities so we don't need a
    # pub/sub architecture like the MQTT class does

    connection_state: QtCore.SignalInstance = QtCore.Signal(object)  # type: ignore

    def __init__(self) -> None:
        super().__init__()

        self.client = SerialLoop()

    def read_loop(self) -> None:
        """
        Infinite loop to read incoming data from the serial port.
        """
        while not self.stop_thread and self.client.in_waiting > 0:
            self.client.read(1)
            time.sleep(0.01)

    def login(self, port: str, baud_rate: int) -> None:
        """
        Connect to the serial port. This method cannot be named "connect"
        as this conflicts with the connect methods of the Signals
        """
        # do nothing on empty sring
        if not port:
            return

        logger.info(f"Connecting to serial port at {port}:{baud_rate}")
        self.connection_state.emit(ConnectionState.connecting)

        self.client.port = port
        self.client.baudrate = baud_rate

        try:
            self.client.open()

            self.stop_thread = False
            self.read_loop_thread = threading.Thread(target=self.read_loop)
            self.read_loop_thread.start()

            # save settings
            config.serial_port = port
            config.serial_baud_rate = baud_rate

            logger.success("Connected to serial port")
            self.connection_state.emit(ConnectionState.connected)

        except Exception:
            logger.exception("Connection failed to serial port")
            self.connection_state.emit(ConnectionState.failure)

    def logout(self) -> None:
        """
        Disconnect from the serial port.
        """
        logger.info("Disconnecting from serial port")
        self.connection_state.emit(ConnectionState.disconnecting)

        self.stop_thread = True
        self.read_loop_thread.join()
        self.client.close()

        logger.info("Disconnected from serial port")
        self.connection_state.emit(ConnectionState.disconnected)


class SerialConnectionWidget(QtWidgets.QWidget):
    connection_state: QtCore.SignalInstance = QtCore.Signal(object)  # type: ignore

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

        self.serial_client = SerialClient()
        self.serial_client.connection_state.connect(self.set_connected_state)

    def build(self) -> None:
        """
        Build the GUI layout
        """
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)

        serial_ports = list_serial_ports()

        # lay out the host label and line edit
        host_layout = QtWidgets.QFormLayout()

        self.com_port_combo = QtWidgets.QComboBox()
        host_layout.addRow(QtWidgets.QLabel("COM Port:"), self.com_port_combo)

        self.baud_rate_line_edit = IntLineEdit()
        host_layout.addRow(QtWidgets.QLabel("Baud Rate:"), self.baud_rate_line_edit)

        layout.addLayout(host_layout)

        # lay out the bottom connection state and buttons
        bottom_layout = QtWidgets.QHBoxLayout()
        self.state_label = QtWidgets.QLabel()
        bottom_layout.addWidget(self.state_label)

        button_layout = QtWidgets.QHBoxLayout()
        self.connect_button = QtWidgets.QPushButton("Connect")
        button_layout.addWidget(self.connect_button)

        self.disconnect_button = QtWidgets.QPushButton("Disconnect")
        button_layout.addWidget(self.disconnect_button)

        bottom_layout.addLayout(button_layout)

        layout.addLayout(bottom_layout)

        # set starting state
        self.set_connected_state(ConnectionState.disconnected)

        self.com_port_combo.addItems(serial_ports)
        self.com_port_combo.setCurrentIndex(
            self.com_port_combo.findText(config.serial_port)
        )
        self.baud_rate_line_edit.setText(str(config.serial_baud_rate))

        # set up connections
        self.connect_button.clicked.connect(  # type: ignore
            lambda: self.serial_client.login(
                self.com_port_combo.currentText(), int(self.baud_rate_line_edit.text())
            )
        )
        self.disconnect_button.clicked.connect(self.serial_client.logout)  # type: ignore

    def set_connected_state(self, connection_state: ConnectionState) -> None:
        color_lookup = {
            ConnectionState.connected: "Green",
            ConnectionState.connecting: "DarkGoldenRod",
            ConnectionState.disconnecting: "DarkGoldenRod",
            ConnectionState.disconnected: "Red",
            ConnectionState.failure: "Red",
        }

        connected = connection_state == ConnectionState.connected
        disconnected = connection_state in [
            ConnectionState.failure,
            ConnectionState.disconnected,
        ]

        self.state_label.setText(
            f"State: <span style='color:{color_lookup[connection_state]};'>{connection_state.name.title()}</span>"
        )

        self.disconnect_button.setEnabled(connected)
        self.connect_button.setDisabled(connected)

        self.com_port_combo.setDisabled(not disconnected)
        self.baud_rate_line_edit.setReadOnly(not disconnected)

        self.connection_state.emit(connection_state)
        QtGui.QGuiApplication.processEvents()
