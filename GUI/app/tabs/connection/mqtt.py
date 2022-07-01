from typing import Any

import paho.mqtt.client as mqtt
from app.lib.enums import ConnectionState
from app.lib.widgets import IntLineEdit
from app.lib.config import config
from loguru import logger
from PySide6 import QtCore, QtGui, QtWidgets


class MQTTClient(QtCore.QObject):
    # This class MUST inherit from QObject in order for the signals to work

    # This class works with a QSigna based architecture, as the MQTT client
    # runs in a seperate thread. The callbacks from the MQTT client run in the same
    # thread as the client and thus those cannot update the GUI, as only the
    # thread that started the GUI is allowed to update it. Thus, set up the
    # MQTT client in a seperate class with signals that are emitted and connected to
    # so the data gets passed back to the GUI thread.

    # Once the Signal objects are created, they transform into SignalInstance objects
    connection_state: QtCore.SignalInstance = QtCore.Signal(object)  # type: ignore
    message: QtCore.SignalInstance = QtCore.Signal(str, str)  # type: ignore

    def __init__(self) -> None:
        super().__init__()

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def on_connect(
        self, client: mqtt.Client, userdata: Any, flags: dict, rc: int
    ) -> None:
        """
        Callback when the MQTT client connects
        """
        # subscribe to all topics
        logger.debug("Subscribing to all topics")
        client.subscribe("#")

    def on_message(
        self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage
    ) -> None:
        """
        Callback for every MQTT message
        """
        self.message.emit(msg.topic, msg.payload.decode("utf-8"))

    def on_disconnect(
        self,
        client: mqtt.Client,
        userdata: Any,
        rc: int,
    ) -> None:
        """
        Callback when the MQTT client disconnects
        """
        logger.debug("Disconnected from MQTT server")
        self.connection_state.emit(ConnectionState.disconnected)

    def login(self, host: str, port: int) -> None:
        """
        Connect the MQTT client to the server. This method cannot be named "connect"
        as this conflicts with the connect methods of the Signals
        """
        # do nothing on empty sring
        if not host:
            return

        logger.info(f"Connecting to MQTT server at {host}:{port}")
        self.connection_state.emit(ConnectionState.connecting)

        try:
            # try to connect to MQTT server
            self.client.connect(host=host, port=port, keepalive=60)
            self.client.loop_start()

            # save settings
            config.mqtt_host = host
            config.mqtt_port = port

            # emit success
            logger.success("Connected to MQTT server")
            self.connection_state.emit(ConnectionState.connected)

        except Exception:
            logger.exception("Connection failed to MQTT server")
            self.connection_state.emit(ConnectionState.failure)

    def logout(self) -> None:
        """
        Disconnect the MQTT client to the server.
        """
        logger.info("Disconnecting from MQTT server")
        self.connection_state.emit(ConnectionState.disconnecting)

        self.client.disconnect()
        self.client.loop_stop()

        logger.info("Disconnected from MQTT server")
        self.connection_state.emit(ConnectionState.disconnected)

    def publish(self, topic: str, payload: Any) -> None:
        """
        Publish an MQTT message. Proxy function to the underlying client
        """
        if not topic:
            return

        logger.debug(f"Publishing message {topic}: {payload}")
        self.client.publish(topic, payload)


class MQTTConnectionWidget(QtWidgets.QWidget):
    connection_state: QtCore.SignalInstance = QtCore.Signal(object)  # type: ignore

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

        self.mqtt_client = MQTTClient()
        self.mqtt_client.connection_state.connect(self.set_connected_state)

    def build(self) -> None:
        """
        Build the GUI layout
        """
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)

        # lay out the host label and line edit
        host_layout = QtWidgets.QFormLayout()

        self.hostname_line_edit = QtWidgets.QLineEdit()
        host_layout.addRow(QtWidgets.QLabel("Host:"), self.hostname_line_edit)

        self.port_line_edit = IntLineEdit()
        host_layout.addRow(QtWidgets.QLabel("Port:"), self.port_line_edit)

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

        self.hostname_line_edit.setText(config.mqtt_host)
        self.port_line_edit.setText(str(config.mqtt_port))

        # set up connections
        self.hostname_line_edit.returnPressed.connect(self.connect_button.click)  # type: ignore
        self.connect_button.clicked.connect(  # type: ignore
            lambda: self.mqtt_client.login(
                self.hostname_line_edit.text(), int(self.port_line_edit.text())
            )
        )
        self.disconnect_button.clicked.connect(self.mqtt_client.logout)  # type: ignore

    def set_connected_state(self, connection_state: ConnectionState) -> None:
        """
        Set the connected state of the MQTT connection widget elements.
        """
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

        self.hostname_line_edit.setReadOnly(not disconnected)
        self.port_line_edit.setReadOnly(not disconnected)

        self.connection_state.emit(connection_state)
        QtGui.QGuiApplication.processEvents()
