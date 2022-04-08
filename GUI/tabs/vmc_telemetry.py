from __future__ import annotations

import json

from lib.mqtt_library import (
    VrcFcmBatteryMessage,
    VrcFcmGpsInfoMessage,
    VrcFcmLocationGlobalMessage,
    VrcFcmLocationLocalMessage,
    VrcFcmStatusMessage,
    VrcFcmAttitudeEulerMessage,
)
from PySide6 import QtWidgets

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
        top_groupbox = QtWidgets.QGroupBox("Status")
        top_layout = QtWidgets.QHBoxLayout()
        top_groupbox.setLayout(top_layout)

        # top-left quadrant
        top_left_frame = QtWidgets.QFrame()
        top_left_layout = QtWidgets.QFormLayout()
        top_left_frame.setLayout(top_left_layout)

        # satellites row
        satellites_layout = QtWidgets.QHBoxLayout()

        self.num_satellites_label = QtWidgets.QLabel("")
        satellites_layout.addWidget(self.num_satellites_label)

        self.fix_type_label = QtWidgets.QLabel("")
        satellites_layout.addWidget(self.fix_type_label)

        top_left_layout.addRow(QtWidgets.QLabel("Satellites:"), satellites_layout)

        # battery row
        battery_layout = QtWidgets.QHBoxLayout()

        self.battery_percent_bar = QtWidgets.QProgressBar()
        self.battery_percent_bar.setRange(0, 100)
        self.battery_percent_bar.setTextVisible(True)
        battery_layout.addWidget(self.battery_percent_bar)

        self.battery_voltage_label = QtWidgets.QLabel("")
        battery_layout.addWidget(self.battery_voltage_label)

        top_left_layout.addRow(QtWidgets.QLabel("Battery:"), battery_layout)

        top_layout.addWidget(top_left_frame)

        # top-right quadrant
        top_right_frame = QtWidgets.QFrame()
        top_right_layout = QtWidgets.QFormLayout()
        top_right_frame.setLayout(top_right_layout)

        # armed row
        self.armed_label = QtWidgets.QLabel("")
        top_right_layout.addRow(QtWidgets.QLabel("Armed:"), self.armed_label)

        # flight mode row
        self.flight_mode_label = QtWidgets.QLabel("")
        top_right_layout.addRow(
            QtWidgets.QLabel("Flight Mode:"), self.flight_mode_label
        )

        top_layout.addWidget(top_right_frame)

        layout.addWidget(top_groupbox)

        # bottom groupbox
        bottom_groupbox = QtWidgets.QGroupBox("Position")
        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_groupbox.setLayout(bottom_layout)

        # bottom-left quadrant
        bottom_left_groupbox = QtWidgets.QGroupBox("Location")
        bottom_left_layout = QtWidgets.QFormLayout()
        bottom_left_groupbox.setLayout(bottom_left_layout)

        # xyz row
        loc_xyz_layout = QtWidgets.QHBoxLayout()

        self.loc_x_line_edit = QtWidgets.QLineEdit("")
        self.loc_x_line_edit.setDisabled(True)
        loc_xyz_layout.addWidget(self.loc_x_line_edit)

        self.loc_y_line_edit = QtWidgets.QLineEdit("")
        self.loc_y_line_edit.setDisabled(True)
        loc_xyz_layout.addWidget(self.loc_y_line_edit)

        self.loc_z_line_edit = QtWidgets.QLineEdit("")
        self.loc_z_line_edit.setDisabled(True)
        loc_xyz_layout.addWidget(self.loc_z_line_edit)

        bottom_left_layout.addRow(
            QtWidgets.QLabel("Local NED (x, y, z):"), loc_xyz_layout
        )

        # lat, lon, alt row
        loc_lla_layout = QtWidgets.QHBoxLayout()

        self.loc_lat_line_edit = QtWidgets.QLineEdit("")
        self.loc_lat_line_edit.setDisabled(True)
        loc_lla_layout.addWidget(self.loc_lat_line_edit)

        self.loc_lon_line_edit = QtWidgets.QLineEdit("")
        self.loc_lon_line_edit.setDisabled(True)
        loc_lla_layout.addWidget(self.loc_lon_line_edit)

        self.loc_alt_line_edit = QtWidgets.QLineEdit("")
        self.loc_alt_line_edit.setDisabled(True)
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

        self.att_r_line_edit = QtWidgets.QLineEdit("")
        self.att_r_line_edit.setDisabled(True)
        att_rpy_layout.addWidget(self.att_r_line_edit)

        self.att_p_line_edit = QtWidgets.QLineEdit("")
        self.att_p_line_edit.setDisabled(True)
        att_rpy_layout.addWidget(self.att_p_line_edit)

        self.att_y_line_edit = QtWidgets.QLineEdit("")
        self.att_y_line_edit.setDisabled(True)
        att_rpy_layout.addWidget(self.att_y_line_edit)

        bottom_right_layout.addRow(QtWidgets.QLabel("Euler (r, p , y)"), att_rpy_layout)

        # auaternion row
        # quaternion_layout = QtWidgets.QHBoxLayout()

        # self.att_w_line_edit = QtWidgets.QLineEdit("")
        # self.att_w_line_edit.setDisabled(True)
        # quaternion_layout.addWidget(self.att_w_line_edit)

        # self.att_x_line_edit = QtWidgets.QLineEdit("")
        # self.att_x_line_edit.setDisabled(True)
        # quaternion_layout.addWidget(self.att_x_line_edit)

        # self.att_y_line_edit = QtWidgets.QLineEdit("")
        # self.att_y_line_edit.setDisabled(True)
        # quaternion_layout.addWidget(self.att_y_line_edit)

        # self.att_z_line_edit = QtWidgets.QLineEdit("")
        # self.att_z_line_edit.setDisabled(True)
        # quaternion_layout.addWidget(self.att_z_line_edit)

        # bottom_right_layout.addRow(
        #     QtWidgets.QLabel("Quaternion (w, x, y, z):"), quaternion_layout
        # )

        bottom_layout.addWidget(bottom_right_groupbox)

        layout.addWidget(bottom_groupbox)

    def update_satellites(self, payload: VrcFcmGpsInfoMessage) -> None:
        """
        Update satellites information
        """
        self.num_satellites_label.setText(f"{payload['num_satellites']} visible")
        self.fix_type_label.setText(payload["fix_type"])

    def update_battery(self, payload: VrcFcmBatteryMessage) -> None:
        """
        Update battery information
        """
        self.battery_percent_bar.setValue(int(payload["soc"] * 100))
        self.battery_voltage_label.setText(f"{payload['voltage']} Volts")

    def update_status(self, payload: VrcFcmStatusMessage) -> None:
        """
        Update status information
        """
        armed = payload["armed"]
        if armed:
            color = "Red"
        else:
            color = "Green"

        self.armed_label.setText(f"<span style='color:{color};'>{armed}</span>")
        self.flight_mode_label.setText(payload["mode"])

    def update_local_location(self, payload: VrcFcmLocationLocalMessage) -> None:
        """
        Update local location information
        """
        self.loc_x_line_edit.setText(str(payload["dX"]))
        self.loc_y_line_edit.setText(str(payload["dY"]))
        self.loc_z_line_edit.setText(str(payload["dZ"]))

    def update_global_location(self, payload: VrcFcmLocationGlobalMessage) -> None:
        """
        Update global location information
        """
        self.loc_lat_line_edit.setText(str(payload["lat"]))
        self.loc_lon_line_edit.setText(str(payload["lon"]))
        self.loc_alt_line_edit.setText(str(payload["alt"]))

    def update_euler_attitude(self, payload: VrcFcmAttitudeEulerMessage) -> None:
        """
        Update euler attitude information
        """
        self.att_r_line_edit.setText(str(payload["roll"]))
        self.att_p_line_edit.setText(str(payload["pitch"]))
        self.att_y_line_edit.setText(str(payload["yaw"]))

    # def update_auaternion_attitude(self, payload: VrcFcmAttitudeQuaternionMessage) -> None:
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
            "vrc/fcm/gps_info": self.update_satellites,
            "vrc/fcm/battery": self.update_battery,
            "vrc/fcm/status": self.update_status,
            "vrc/fcm/location/local": self.update_local_location,
            "vrc/fcm/location/global": self.update_global_location,
            "vrc/fcm/attitude/euler": self.update_euler_attitude,
        }

        if topic not in topic_map:
            return

        data = json.loads(payload)
        topic_map[topic](data)
