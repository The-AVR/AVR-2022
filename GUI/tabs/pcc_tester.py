from __future__ import annotations

from typing import List, Literal

from lib.pcc_library import PeripheralControlComputer
from PySide6 import QtCore, QtWidgets

from .base import BaseTabWidget
from .connection.serial import SerialClient


class PCCTesterWidget(BaseTabWidget):
    def __init__(self, parent: QtWidgets.QWidget, client: SerialClient) -> None:
        super().__init__(parent)

        self.setWindowTitle("PCC Tester")

        self.client = PeripheralControlComputer(client.client)

    def build(self) -> None:
        """
        Build the GUI layout
        """
        layout = QtWidgets.QGridLayout(self)
        self.setLayout(layout)

        # ==========================
        # Servo 1
        servo_1_groupbox = QtWidgets.QGroupBox("Servo 1")
        servo_1_layout = QtWidgets.QGridLayout()
        servo_1_groupbox.setLayout(servo_1_layout)

        self.servo_1_dial = QtWidgets.QDial()
        self.servo_1_dial.setNotchesVisible(True)
        self.servo_1_dial.setRange(0, 100)
        servo_1_layout.addWidget(self.servo_1_dial, 0, 0, 1, 1)

        self.servo_1_number = QtWidgets.QLCDNumber()
        self.servo_1_dial.valueChanged.connect(self.servo_1_number.display)  # type: ignore
        self.servo_1_dial.valueChanged.connect(self.update_servos)  # type: ignore
        servo_1_layout.addWidget(self.servo_1_number, 0, 1, 1, 1)

        servo_1_button = QtWidgets.QPushButton("Toggle Open/Close")
        servo_1_button.clicked.connect(lambda: self.toggle_servo(0))  # type: ignore
        servo_1_layout.addWidget(servo_1_button, 1, 0, 1, 2)

        layout.addWidget(servo_1_groupbox, 0, 0, 2, 2)

        # ==========================
        # Servo 2
        servo_2_groupbox = QtWidgets.QGroupBox("Servo 2")
        servo_2_layout = QtWidgets.QGridLayout()
        servo_2_groupbox.setLayout(servo_2_layout)

        self.servo_2_dial = QtWidgets.QDial()
        self.servo_2_dial.setNotchesVisible(True)
        self.servo_2_dial.setRange(0, 100)
        servo_2_layout.addWidget(self.servo_2_dial, 0, 0, 1, 1)

        self.servo_2_number = QtWidgets.QLCDNumber()
        self.servo_2_dial.valueChanged.connect(self.servo_2_number.display)  # type: ignore
        self.servo_2_dial.valueChanged.connect(self.update_servos)  # type: ignore
        servo_2_layout.addWidget(self.servo_2_number, 0, 1, 1, 1)

        servo_2_button = QtWidgets.QPushButton("Toggle Open/Close")
        servo_2_button.clicked.connect(lambda: self.toggle_servo(1))  # type: ignore
        servo_2_layout.addWidget(servo_2_button, 1, 0, 1, 2)

        layout.addWidget(servo_2_groupbox, 0, 2, 2, 2)

        # ==========================
        # Servo 3
        servo_3_groupbox = QtWidgets.QGroupBox("Servo 3")
        servo_3_layout = QtWidgets.QGridLayout()
        servo_3_groupbox.setLayout(servo_3_layout)

        self.servo_3_dial = QtWidgets.QDial()
        self.servo_3_dial.setNotchesVisible(True)
        self.servo_3_dial.setRange(0, 100)
        servo_3_layout.addWidget(self.servo_3_dial, 0, 0, 1, 1)

        self.servo_3_number = QtWidgets.QLCDNumber()
        self.servo_3_dial.valueChanged.connect(self.servo_3_number.display)  # type: ignore
        self.servo_3_dial.valueChanged.connect(self.update_servos)  # type: ignore
        servo_3_layout.addWidget(self.servo_3_number, 0, 1, 1, 1)

        servo_3_button = QtWidgets.QPushButton("Toggle Open/Close")
        servo_3_button.clicked.connect(lambda: self.toggle_servo(2))  # type: ignore
        servo_3_layout.addWidget(servo_3_button, 1, 0, 1, 2)

        layout.addWidget(servo_3_groupbox, 2, 0, 2, 2)

        # ==========================
        # Servo 4
        servo_4_groupbox = QtWidgets.QGroupBox("Servo 4")
        servo_4_layout = QtWidgets.QGridLayout()
        servo_4_groupbox.setLayout(servo_4_layout)

        self.servo_4_dial = QtWidgets.QDial()
        self.servo_4_dial.setNotchesVisible(True)
        self.servo_4_dial.setRange(0, 100)
        servo_4_layout.addWidget(self.servo_4_dial, 0, 0, 1, 1)

        self.servo_4_number = QtWidgets.QLCDNumber()
        self.servo_4_dial.valueChanged.connect(self.servo_4_number.display)  # type: ignore
        self.servo_4_dial.valueChanged.connect(self.update_servos)  # type: ignore
        servo_4_layout.addWidget(self.servo_4_number, 0, 1, 1, 1)

        servo_4_button = QtWidgets.QPushButton("Toggle Open/Close")
        servo_4_button.clicked.connect(lambda: self.toggle_servo(3))  # type: ignore
        servo_4_layout.addWidget(servo_4_button, 1, 0, 1, 2)

        layout.addWidget(servo_4_groupbox, 2, 2, 2, 2)

        # ==========================
        # LEDs
        led_groupbox = QtWidgets.QGroupBox("LED Strip")
        led_layout = QtWidgets.QGridLayout()
        led_groupbox.setLayout(led_layout)

        red_led_label = QtWidgets.QLabel("Red")
        led_layout.addWidget(red_led_label, 0, 0, 1, 1)

        self.red_led_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.red_led_slider.setRange(0, 255)
        led_layout.addWidget(self.red_led_slider, 0, 1, 1, 5)

        red_led_spinbox = QtWidgets.QSpinBox()
        red_led_spinbox.setRange(0, 255)
        red_led_spinbox.valueChanged.connect(self.red_led_slider.setValue)  # type: ignore
        self.red_led_slider.valueChanged.connect(red_led_spinbox.setValue)  # type: ignore
        self.red_led_slider.valueChanged.connect(self.update_leds)  # type: ignore
        led_layout.addWidget(red_led_spinbox, 0, 6, 1, 1)

        green_led_label = QtWidgets.QLabel("Green")
        led_layout.addWidget(green_led_label, 1, 0, 1, 1)

        self.green_led_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.green_led_slider.setRange(0, 255)
        led_layout.addWidget(self.green_led_slider, 1, 1, 1, 5)

        green_led_spinbox = QtWidgets.QSpinBox()
        green_led_spinbox.setRange(0, 255)
        green_led_spinbox.valueChanged.connect(self.green_led_slider.setValue)  # type: ignore
        self.green_led_slider.valueChanged.connect(green_led_spinbox.setValue)  # type: ignore
        self.green_led_slider.valueChanged.connect(self.update_leds)  # type: ignore
        led_layout.addWidget(green_led_spinbox, 1, 6, 1, 1)

        blue_led_label = QtWidgets.QLabel("Blue")
        led_layout.addWidget(blue_led_label, 2, 0, 1, 1)

        self.blue_led_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.blue_led_slider.setRange(0, 255)
        led_layout.addWidget(self.blue_led_slider, 2, 1, 1, 5)

        blue_led_spinbox = QtWidgets.QSpinBox()
        blue_led_spinbox.setRange(0, 255)
        blue_led_spinbox.valueChanged.connect(self.blue_led_slider.setValue)  # type: ignore
        self.blue_led_slider.valueChanged.connect(blue_led_spinbox.setValue)  # type: ignore
        self.blue_led_slider.valueChanged.connect(self.update_leds)  # type: ignore
        led_layout.addWidget(blue_led_spinbox, 2, 6, 1, 1)

        layout.addWidget(led_groupbox, 4, 0, 1, 4)

        self.reset_button = QtWidgets.QPushButton("Reset All")
        self.reset_button.clicked.connect(self.reset_all)  # type: ignore

        layout.addWidget(self.reset_button, 5, 0, 1, 4)

        self.servo_states: List[Literal["open", "close"]] = ["close"] * 4
        self.servo_dials = {
            0: (self.servo_1_dial, self.servo_1_number),
            1: (self.servo_2_dial, self.servo_2_number),
            2: (self.servo_3_dial, self.servo_3_number),
            3: (self.servo_4_dial, self.servo_4_number),
        }

    def update_leds(self) -> None:
        """
        Update the value of the LEDs based on the current position of the sliders
        """
        red = self.red_led_slider.value()
        green = self.green_led_slider.value()
        blue = self.blue_led_slider.value()

        self.client.set_base_color([0, red, green, blue])

    def update_servos(self) -> None:
        """
        Update the position of the servos based on the current position of the dials
        """
        self.client.set_servo_pct(0, self.servo_1_dial.value())
        self.client.set_servo_pct(1, self.servo_2_dial.value())
        self.client.set_servo_pct(2, self.servo_3_dial.value())
        self.client.set_servo_pct(3, self.servo_4_dial.value())

    def toggle_servo(self, servo: int) -> None:
        """
        Toggle a servo open or closed
        """
        if self.servo_states[servo] == "open":
            self.servo_states[servo] = "close"
            pct = 0
        else:
            self.servo_states[servo] = "open"
            pct = 100

        # send update to pcc
        self.client.set_servo_open_close(servo, self.servo_states[servo])

        # manually update dial and lcd without triggering valueChanged
        self.servo_dials[servo][0].blockSignals(True)
        self.servo_dials[servo][0].setValue(pct)
        self.servo_dials[servo][1].display(pct)
        self.servo_dials[servo][0].blockSignals(False)

    def reset_all(self) -> None:
        """
        Reset all values back to 0.
        """
        self.servo_1_dial.setValue(0)
        self.servo_2_dial.setValue(0)
        self.servo_3_dial.setValue(0)
        self.servo_4_dial.setValue(0)

        self.red_led_slider.setValue(0)
        self.green_led_slider.setValue(0)
        self.blue_led_slider.setValue(0)
