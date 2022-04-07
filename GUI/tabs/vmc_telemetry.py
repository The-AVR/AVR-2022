from __future__ import annotations

import json
from PySide6 import QtWidgets

from lib.mqtt_library import VrcFcmBatteryMessage

from .base import BaseTabWidget
from lib.mqtt_library import VrcFcmGpsInfoMessage


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

        top_left_layout.addRow(QtWidgets.QLabel("satellites:"), satellites_layout)

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
        bottom_groupbox = QtWidgets.QGroupBox("Orientation")
        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_groupbox.setLayout(bottom_layout)

        # bottom-left quadrant
        bottom_left_groupbox = QtWidgets.QGroupBox("Position")
        bottom_left_layout = QtWidgets.QFormLayout()
        bottom_left_groupbox.setLayout(bottom_left_layout)

        # xyz row
        pos_xyz_layout = QtWidgets.QHBoxLayout()

        self.pos_x_line_edit = QtWidgets.QLineEdit("")
        self.pos_x_line_edit.setDisabled(True)
        pos_xyz_layout.addWidget(self.pos_x_line_edit)

        self.pos_y_line_edit = QtWidgets.QLineEdit("")
        self.pos_y_line_edit.setDisabled(True)
        pos_xyz_layout.addWidget(self.pos_y_line_edit)

        self.pos_z_line_edit = QtWidgets.QLineEdit("")
        self.pos_z_line_edit.setDisabled(True)
        pos_xyz_layout.addWidget(self.pos_z_line_edit)

        bottom_left_layout.addRow(
            QtWidgets.QLabel("Local NED (x, y, z):"), pos_xyz_layout
        )

        # lat, lon, alt row
        pos_lla_layout = QtWidgets.QHBoxLayout()

        self.pos_lat_line_edit = QtWidgets.QLineEdit("")
        self.pos_lat_line_edit.setDisabled(True)
        pos_lla_layout.addWidget(self.pos_lat_line_edit)

        self.pos_lon_line_edit = QtWidgets.QLineEdit("")
        self.pos_lon_line_edit.setDisabled(True)
        pos_lla_layout.addWidget(self.pos_lon_line_edit)

        self.pos_alt_line_edit = QtWidgets.QLineEdit("")
        self.pos_alt_line_edit.setDisabled(True)
        pos_lla_layout.addWidget(self.pos_alt_line_edit)

        bottom_left_layout.addRow(
            QtWidgets.QLabel("Global (lat, lon, alt):"), pos_lla_layout
        )

        bottom_layout.addWidget(bottom_left_groupbox)

        # bottom-right quadrant
        bottom_right_groupbox = QtWidgets.QGroupBox("Position")
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
        quaternion_layout = QtWidgets.QHBoxLayout()

        self.att_w_line_edit = QtWidgets.QLineEdit("")
        self.att_w_line_edit.setDisabled(True)
        quaternion_layout.addWidget(self.att_w_line_edit)

        self.att_x_line_edit = QtWidgets.QLineEdit("")
        self.att_x_line_edit.setDisabled(True)
        quaternion_layout.addWidget(self.att_x_line_edit)

        self.att_y_line_edit = QtWidgets.QLineEdit("")
        self.att_y_line_edit.setDisabled(True)
        quaternion_layout.addWidget(self.att_y_line_edit)

        self.att_z_line_edit = QtWidgets.QLineEdit("")
        self.att_z_line_edit.setDisabled(True)
        quaternion_layout.addWidget(self.att_z_line_edit)

        bottom_right_layout.addRow(
            QtWidgets.QLabel("Quaternion (w, x, y, z):"), quaternion_layout
        )

        bottom_layout.addWidget(bottom_right_groupbox)

        layout.addWidget(bottom_groupbox)

    def update_satellites(self, payload: VrcFcmGpsInfoMessage) -> None:
        self.num_satellites_label.setText(f"{payload['num_satellites']} visible")
        self.fix_type_label.setText(payload["fix_type"])

    def update_battery(self, payload: VrcFcmBatteryMessage) -> None:
        self.battery_percent_bar.setValue(int(payload["soc"] * 100))
        self.battery_voltage_label.setText(f"{payload['voltage']} Volts")

    def process_message(self, topic: str, payload: str) -> None:
        data = json.loads(payload)
        if topic == "vrc/fcm/gps_info":
            self.update_satellites(data)
        elif topic == "vrc/fcm/battery":
            self.update_battery(data)