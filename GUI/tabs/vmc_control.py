from __future__ import annotations

from typing import Literal, Tuple

from bell.vrc.mqtt.payloads import (
    VrcAutonomousPayload,
    VrcPcmResetPayload,
    VrcPcmSetBaseColorPayload,
    VrcPcmSetServoOpenClosePayload,
)
from PySide6 import QtWidgets

from .base import BaseTabWidget


class VMCControlWidget(BaseTabWidget):
    # This is the primary control widget for the drone. This allows the user
    # to set LED color, open/close servos etc.

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

        self.setWindowTitle("VMC Control")

    def build(self) -> None:
        """
        Build the GUI layout
        """
        layout = QtWidgets.QGridLayout(self)
        self.setLayout(layout)

        # ==========================
        # LEDs
        led_groupbox = QtWidgets.QGroupBox("LEDs")
        led_layout = QtWidgets.QVBoxLayout()
        led_groupbox.setLayout(led_layout)

        red_led_button = QtWidgets.QPushButton("Red")
        red_led_button.setStyleSheet("background-color: red")
        red_led_button.clicked.connect(lambda: self.set_led((255, 255, 0, 0)))  # type: ignore
        led_layout.addWidget(red_led_button)

        green_led_button = QtWidgets.QPushButton("Green")
        green_led_button.setStyleSheet("background-color: green")
        green_led_button.clicked.connect(lambda: self.set_led((255, 0, 255, 0)))  # type: ignore
        led_layout.addWidget(green_led_button)

        blue_led_button = QtWidgets.QPushButton("Blue")
        blue_led_button.setStyleSheet("background-color: blue; color: white")
        blue_led_button.clicked.connect(lambda: self.set_led((255, 0, 0, 255)))  # type: ignore
        led_layout.addWidget(blue_led_button)

        clear_led_button = QtWidgets.QPushButton("Clear")
        clear_led_button.setStyleSheet("background-color: white")
        clear_led_button.clicked.connect(lambda: self.set_led((0, 0, 0, 0)))  # type: ignore
        led_layout.addWidget(clear_led_button)

        layout.addWidget(led_groupbox, 0, 0, 3, 1)

        # ==========================
        # Servos
        servos_groupbox = QtWidgets.QGroupBox("Servos")
        servos_layout = QtWidgets.QVBoxLayout()
        servos_groupbox.setLayout(servos_layout)

        servo_all_layout = QtWidgets.QHBoxLayout()

        servo_all_open_button = QtWidgets.QPushButton("Open all")
        servo_all_open_button.clicked.connect(lambda: self.set_servo_all("open"))  # type: ignore
        servo_all_layout.addWidget(servo_all_open_button)

        servo_all_close_button = QtWidgets.QPushButton("Close all")
        servo_all_close_button.clicked.connect(lambda: self.set_servo_all("close"))  # type: ignore
        servo_all_layout.addWidget(servo_all_close_button)

        servos_layout.addLayout(servo_all_layout)

        servo_1_groupbox = QtWidgets.QGroupBox("Servo 1")
        servo_1_layout = QtWidgets.QHBoxLayout()
        servo_1_groupbox.setLayout(servo_1_layout)

        servo_1_open_button = QtWidgets.QPushButton("Open")
        servo_1_open_button.clicked.connect(lambda: self.set_servo(0, "open"))  # type: ignore
        servo_1_layout.addWidget(servo_1_open_button)

        servo_1_close_button = QtWidgets.QPushButton("Close")
        servo_1_close_button.clicked.connect(lambda: self.set_servo(0, "close"))  # type: ignore
        servo_1_layout.addWidget(servo_1_close_button)

        servos_layout.addWidget(servo_1_groupbox)

        servo_2_groupbox = QtWidgets.QGroupBox("Servo 2")
        servo_2_layout = QtWidgets.QHBoxLayout()
        servo_2_groupbox.setLayout(servo_2_layout)

        servo_2_open_button = QtWidgets.QPushButton("Open")
        servo_2_open_button.clicked.connect(lambda: self.set_servo(1, "open"))  # type: ignore
        servo_2_layout.addWidget(servo_2_open_button)

        servo_2_close_button = QtWidgets.QPushButton("Close")
        servo_2_close_button.clicked.connect(lambda: self.set_servo(1, "close"))  # type: ignore
        servo_2_layout.addWidget(servo_2_close_button)

        servos_layout.addWidget(servo_2_groupbox)

        servo_3_groupbox = QtWidgets.QGroupBox("Servo 3")
        servo_3_layout = QtWidgets.QHBoxLayout()
        servo_3_groupbox.setLayout(servo_3_layout)

        servo_3_open_button = QtWidgets.QPushButton("Open")
        servo_3_open_button.clicked.connect(lambda: self.set_servo(2, "open"))  # type: ignore
        servo_3_layout.addWidget(servo_3_open_button)

        servo_3_close_button = QtWidgets.QPushButton("Close")
        servo_3_close_button.clicked.connect(lambda: self.set_servo(2, "close"))  # type: ignore
        servo_3_layout.addWidget(servo_3_close_button)

        servos_layout.addWidget(servo_3_groupbox)

        servo_4_groupbox = QtWidgets.QGroupBox("Servo 4")
        servo_4_layout = QtWidgets.QHBoxLayout()
        servo_4_groupbox.setLayout(servo_4_layout)

        servo_4_open_button = QtWidgets.QPushButton("Open")
        servo_4_open_button.clicked.connect(lambda: self.set_servo(3, "open"))  # type: ignore
        servo_4_layout.addWidget(servo_4_open_button)

        servo_4_close_button = QtWidgets.QPushButton("Close")
        servo_4_close_button.clicked.connect(lambda: self.set_servo(3, "close"))  # type: ignore
        servo_4_layout.addWidget(servo_4_close_button)

        servos_layout.addWidget(servo_4_groupbox)

        layout.addWidget(servos_groupbox, 0, 1, 3, 3)

        # ==========================
        # Autonomous mode
        autonomous_groupbox = QtWidgets.QGroupBox("Autonomous")
        autonomous_layout = QtWidgets.QHBoxLayout()
        autonomous_groupbox.setLayout(autonomous_layout)

        autonomous_enable_button = QtWidgets.QPushButton("Enable")
        autonomous_enable_button.clicked.connect(lambda: self.set_autonomous(True))  # type: ignore
        autonomous_layout.addWidget(autonomous_enable_button)

        autonomous_disable_button = QtWidgets.QPushButton("Disable")
        autonomous_disable_button.clicked.connect(lambda: self.set_autonomous(False))  # type: ignore
        autonomous_layout.addWidget(autonomous_disable_button)

        layout.addWidget(autonomous_groupbox, 3, 0, 1, 3)

        # ==========================
        # PCC Reset
        reset_groupbox = QtWidgets.QGroupBox("Reset")
        reset_layout = QtWidgets.QVBoxLayout()
        reset_groupbox.setLayout(reset_layout)

        reset_button = QtWidgets.QPushButton("Reset Peripheals")
        reset_button.setStyleSheet("background-color: yellow")
        reset_button.clicked.connect(lambda: self.send_message("vrc/pcm/reset", VrcPcmResetPayload()))  # type: ignore
        reset_layout.addWidget(reset_button)

        layout.addWidget(reset_groupbox, 3, 3, 1, 1)

    def set_servo(self, number: int, action: Literal["open", "close"]) -> None:
        """
        Set a servo state
        """
        self.send_message(
            "vrc/pcm/set_servo_open_close",
            VrcPcmSetServoOpenClosePayload(servo=number, action=action),
        )

    def set_servo_all(self, action: Literal["open", "close"]) -> None:
        """
        Set all servos to the same state
        """
        for i in range(4):
            self.set_servo(i, action)

    def set_led(self, color: Tuple[int, int, int, int]) -> None:
        """
        Set LED color
        """
        self.send_message(
            "vrc/pcm/set_base_color", VrcPcmSetBaseColorPayload(wrgb=color)
        )

    def set_autonomous(self, state: bool) -> None:
        """
        Set autonomous mode
        """
        self.send_message("vrc/autonomous", VrcAutonomousPayload(enable=state))
