from __future__ import annotations

import json
from typing import Dict

from bell.avr.mqtt.payloads import (
    AvrFcmAttitudeEulerPayload,
    AvrFcmBatteryPayload,
    AvrFcmGpsInfoPayload,
    AvrFcmLocationGlobalPayload,
    AvrFcmLocationLocalPayload,
    AvrFcmStatusPayload,
)
from PySide6 import QtCore, QtWidgets

from ..lib.color import smear_color, wrap_text
from ..lib.widgets import DisplayLineEdit, StatusLabel
from .base import BaseTabWidget


class VMCTelemetryWidget(BaseTabWidget):
    # This widget provides a minimal QGroundControl-esque interface.
    # In our case, this operates over MQTT as all the relevant data
    # is already published there.

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

        self.setWindowTitle("VMC Telemetry")

    def build(self) -> None:
        """
        Build the GUI layout
        """
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)

        # top groupbox
        top_groupbox = QtWidgets.QGroupBox("FCC Status")
        top_groupbox.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed
        )
        top_layout = QtWidgets.QFormLayout()
        top_groupbox.setLayout(top_layout)

        # satellites row
        self.satellites_label = QtWidgets.QLabel("")
        top_layout.addRow(QtWidgets.QLabel("Satellites:"), self.satellites_label)

        # battery row
        battery_layout = QtWidgets.QHBoxLayout()

        self.battery_percent_bar = QtWidgets.QProgressBar()
        self.battery_percent_bar.setRange(0, 100)
        self.battery_percent_bar.setTextVisible(True)
        battery_layout.addWidget(self.battery_percent_bar)

        self.battery_voltage_label = QtWidgets.QLabel("")
        battery_layout.addWidget(self.battery_voltage_label)

        top_layout.addRow(QtWidgets.QLabel("Battery:"), battery_layout)

        # armed row
        self.armed_label = QtWidgets.QLabel("")
        top_layout.addRow(QtWidgets.QLabel("Armed Status:"), self.armed_label)

        # flight mode row
        self.flight_mode_label = QtWidgets.QLabel("")
        top_layout.addRow(QtWidgets.QLabel("Flight Mode:"), self.flight_mode_label)

        layout.addWidget(top_groupbox)

        # bottom groupbox
        bottom_group = QtWidgets.QFrame()
        bottom_group.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed
        )
        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_group.setLayout(bottom_layout)

        # bottom-left quadrant
        bottom_left_groupbox = QtWidgets.QGroupBox("Location")
        bottom_left_layout = QtWidgets.QFormLayout()
        bottom_left_groupbox.setLayout(bottom_left_layout)

        # xyz row
        loc_xyz_layout = QtWidgets.QHBoxLayout()

        self.loc_x_line_edit = DisplayLineEdit("")
        loc_xyz_layout.addWidget(self.loc_x_line_edit)

        self.loc_y_line_edit = DisplayLineEdit("")
        loc_xyz_layout.addWidget(self.loc_y_line_edit)

        self.loc_z_line_edit = DisplayLineEdit("")
        loc_xyz_layout.addWidget(self.loc_z_line_edit)

        bottom_left_layout.addRow(
            QtWidgets.QLabel("Local NED (x, y, z):"), loc_xyz_layout
        )

        # lat, lon, alt row
        loc_lla_layout = QtWidgets.QHBoxLayout()

        self.loc_lat_line_edit = DisplayLineEdit("", round_digits=8)
        loc_lla_layout.addWidget(self.loc_lat_line_edit)

        self.loc_lon_line_edit = DisplayLineEdit("", round_digits=8)
        loc_lla_layout.addWidget(self.loc_lon_line_edit)

        self.loc_alt_line_edit = DisplayLineEdit("")
        loc_lla_layout.addWidget(self.loc_alt_line_edit)

        bottom_left_layout.addRow(
            QtWidgets.QLabel("Global (lat, lon, alt):"), loc_lla_layout
        )

        bottom_layout.addWidget(bottom_left_groupbox)

        # bottom-right quadrant
        bottom_right_groupbox = QtWidgets.QGroupBox("Attitude")
        bottom_right_layout = QtWidgets.QFormLayout()
        bottom_right_groupbox.setLayout(bottom_right_layout)

        # euler row
        att_rpy_layout = QtWidgets.QHBoxLayout()

        self.att_r_line_edit = DisplayLineEdit("")
        att_rpy_layout.addWidget(self.att_r_line_edit)

        self.att_p_line_edit = DisplayLineEdit("")
        att_rpy_layout.addWidget(self.att_p_line_edit)

        self.att_y_line_edit = DisplayLineEdit("")
        att_rpy_layout.addWidget(self.att_y_line_edit)

        bottom_right_layout.addRow(QtWidgets.QLabel("Euler (r, p , y)"), att_rpy_layout)

        # auaternion row
        # quaternion_layout = QtWidgets.QHBoxLayout()

        # self.att_w_line_edit = DisplayLineEdit("")
        # quaternion_layout.addWidget(self.att_w_line_edit)

        # self.att_x_line_edit = DisplayLineEdit("")
        # quaternion_layout.addWidget(self.att_x_line_edit)

        # self.att_y_line_edit = DisplayLineEdit("")
        # quaternion_layout.addWidget(self.att_y_line_edit)

        # self.att_z_line_edit = DisplayLineEdit("")
        # quaternion_layout.addWidget(self.att_z_line_edit)

        # bottom_right_layout.addRow(
        #     QtWidgets.QLabel("Quaternion (w, x, y, z):"), quaternion_layout
        # )

        bottom_layout.addWidget(bottom_right_groupbox)

        layout.addWidget(bottom_group)

        # ==========================
        # Status
        module_status_groupbox = QtWidgets.QGroupBox("Module Status")
        module_status_groupbox.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed
        )
        module_status_layout = QtWidgets.QHBoxLayout()
        module_status_groupbox.setLayout(module_status_layout)

        # data structure to hold the topic prefixes and the corresponding widget
        self.topic_status_map: Dict[str, StatusLabel] = {}
        # data structure to hold timers to reset services to unhealthy
        self.topic_timer: Dict[str, QtCore.QTimer] = {}

        fcc_status = StatusLabel("FCM")
        self.topic_status_map["avr/fcm"] = fcc_status
        module_status_layout.addWidget(fcc_status)

        # pcc_status = StatusLabel("PCM")
        # self.topic_status_map["avr/pcm"] = pcc_status
        # status_layout.addWidget(pcc_status)

        vio_status = StatusLabel("VIO")
        self.topic_status_map["avr/vio"] = vio_status
        module_status_layout.addWidget(vio_status)

        at_status = StatusLabel("AT")
        self.topic_status_map["avr/apriltag"] = at_status
        module_status_layout.addWidget(at_status)

        fus_status = StatusLabel("FUS")
        self.topic_status_map["avr/fusion"] = fus_status
        module_status_layout.addWidget(fus_status)

        layout.addWidget(module_status_groupbox)

    def clear(self) -> None:
        # status
        self.battery_percent_bar.setValue(0)
        self.battery_voltage_label.setText("")

        self.armed_label.setText("")
        self.flight_mode_label.setText("")

        # position
        self.loc_x_line_edit.setText("")
        self.loc_y_line_edit.setText("")
        self.loc_z_line_edit.setText("")

        self.loc_lat_line_edit.setText("")
        self.loc_lon_line_edit.setText("")
        self.loc_alt_line_edit.setText("")

        self.att_r_line_edit.setText("")
        self.att_p_line_edit.setText("")
        self.att_y_line_edit.setText("")

    def update_satellites(self, payload: AvrFcmGpsInfoPayload) -> None:
        """
        Update satellites information
        """
        self.satellites_label.setText(
            f"{payload['num_satellites']} visible, {payload['fix_type']}"
        )

    def update_battery(self, payload: AvrFcmBatteryPayload) -> None:
        """
        Update battery information
        """
        soc = payload["soc"]
        # prevent it from dropping below 0
        soc = max(soc, 0)
        # prevent it from going above 100
        soc = min(soc, 100)

        self.battery_percent_bar.setValue(int(soc))
        self.battery_voltage_label.setText(f"{round(payload['voltage'], 4)} Volts")

        # this is required to change the progress bar color as the value changes
        color = smear_color(
            (135, 0, 16), (11, 135, 0), value=soc, min_value=0, max_value=100
        )

        stylesheet = f"""
            QProgressBar {{
                border: 1px solid grey;
                border-radius: 0px;
                text-align: center;
            }}

            QProgressBar::chunk {{
                background-color: rgb{color};
            }}
            """

        self.battery_percent_bar.setStyleSheet(stylesheet)

    def update_status(self, payload: AvrFcmStatusPayload) -> None:
        """
        Update status information
        """
        if payload["armed"]:
            color = "Red"
            text = "Armed (and dangerous)"
        else:
            color = "DarkGoldenRod"
            text = "Disarmed"

        self.armed_label.setText(wrap_text(text, color))
        self.flight_mode_label.setText(payload["mode"])

    def update_local_location(self, payload: AvrFcmLocationLocalPayload) -> None:
        """
        Update local location information
        """
        self.loc_x_line_edit.setText(str(payload["dX"]))
        self.loc_y_line_edit.setText(str(payload["dY"]))
        self.loc_z_line_edit.setText(str(payload["dZ"]))

    def update_global_location(self, payload: AvrFcmLocationGlobalPayload) -> None:
        """
        Update global location information
        """
        self.loc_lat_line_edit.setText(str(payload["lat"]))
        self.loc_lon_line_edit.setText(str(payload["lon"]))
        self.loc_alt_line_edit.setText(str(payload["alt"]))

    def update_euler_attitude(self, payload: AvrFcmAttitudeEulerPayload) -> None:
        """
        Update euler attitude information
        """
        self.att_r_line_edit.setText(str(payload["roll"]))
        self.att_p_line_edit.setText(str(payload["pitch"]))
        self.att_y_line_edit.setText(str(payload["yaw"]))

    # def update_auaternion_attitude(self, payload: AvrFcmAttitudeQuaternionMessage) -> None:
    #     """
    #     Update euler attitude information
    #     """
    #     self.att_w_line_edit.setText(str(payload["w"]))
    #     self.att_x_line_edit.setText(str(payload["x"]))
    #     self.att_y_line_edit.setText(str(payload["y"]))
    #     self.att_z_line_edit.setText(str(payload["z"]))

    def process_message(self, topic: str, payload: str) -> None:
        """
        Process an incoming message and update the appropriate component
        """
        topic_map = {
            "avr/fcm/gps_info": self.update_satellites,
            "avr/fcm/battery": self.update_battery,
            "avr/fcm/status": self.update_status,
            "avr/fcm/location/local": self.update_local_location,
            "avr/fcm/location/global": self.update_global_location,
            "avr/fcm/attitude/euler": self.update_euler_attitude,
        }

        # discard topics we don't recognize
        if topic in topic_map:
            data = json.loads(payload)
            topic_map[topic](data)

        for status_prefix in self.topic_status_map.keys():
            if not topic.startswith(status_prefix):
                continue

            # set icon to healthy
            status_label = self.topic_status_map[status_prefix]
            status_label.set_health(True)

            # reset existing timer
            if status_prefix in self.topic_timer:
                timer = self.topic_timer[status_prefix]
                timer.stop()
                timer.deleteLater()

            # create a new timer
            # Can't do .singleShot on an exisiting QTimer as that
            # creates a new instance
            timer = QtCore.QTimer()
            timer.timeout.connect(lambda: status_label.set_health(False))  # type: ignore
            timer.setSingleShot(True)
            timer.start(2000)

            self.topic_timer[status_prefix] = timer
            break
