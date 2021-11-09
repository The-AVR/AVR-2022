from __future__ import annotations

import glob
import sys
from typing import List, Literal

import serial
from pcc_library import VRC_Peripheral
from PySide6 import QtCore, QtWidgets
from qt_icon import set_icon


def list_serial_ports() -> List[str]:
    """
    Returns a list of serial ports on the system
    """
    if sys.platform.startswith("win"):
        ports = ["COM%s" % (i + 1) for i in range(256)]
    elif sys.platform.startswith("linux") or sys.platform.startswith("cygwin"):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob("/dev/tty[A-Za-z]*")
    elif sys.platform.startswith("darwin"):
        ports = glob.glob("/dev/tty.*")
    else:
        raise EnvironmentError("Unsupported platform")

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass

    return result


class MainWidget(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.setup_widget = ConnectWidget(self)
        self.setup_widget.build()
        self.setup_widget.connect_button.clicked.connect(self.connect)  # type: ignore
        self.setup_widget.exec()

        self.control_widget = ControlWidget(self)
        self.control_widget.build()
        self.control_widget.show()

    def connect(self) -> None:
        """
        Creates the connection to the PCC
        """
        try:
            self.pcc_connection = VRC_Peripheral(
                self.setup_widget.com_port_combo.currentText(), use_serial=True
            )
            self.setup_widget.close()
        except:
            QtWidgets.QMessageBox.critical(
                self, "Serial Error", "Could not connect to serial device."
            )
            sys.exit(1)


class ControlWidget(QtWidgets.QWidget):
    def __init__(self, parent: MainWidget) -> None:
        self.parent_ = parent
        super().__init__()

        self.setWindowTitle("Bell VRC PCC Tester")
        set_icon(self)

        self.servo_states: List[Literal["open", "close"]] = ["open"] * 4

    def build(self) -> None:
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        # ==========================
        # Servo 1
        servo_1_groupbox = QtWidgets.QGroupBox("Servo 1")
        servo_1_layout = QtWidgets.QGridLayout()
        servo_1_groupbox.setLayout(servo_1_layout)

        self.servo_1_dial = QtWidgets.QDial()
        self.servo_1_dial.setNotchesVisible(True)
        servo_1_layout.addWidget(self.servo_1_dial, 0, 0, 1, 1)

        servo_1_number = QtWidgets.QLCDNumber()
        self.servo_1_dial.valueChanged.connect(servo_1_number.display)  # type: ignore
        self.servo_1_dial.valueChanged.connect(self.update_servos)  # type: ignore
        servo_1_layout.addWidget(servo_1_number, 0, 1, 1, 1)

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
        servo_2_layout.addWidget(self.servo_2_dial, 0, 0, 1, 1)

        servo_2_number = QtWidgets.QLCDNumber()
        self.servo_2_dial.valueChanged.connect(servo_2_number.display)  # type: ignore
        self.servo_2_dial.valueChanged.connect(self.update_servos)  # type: ignore
        servo_2_layout.addWidget(servo_2_number, 0, 1, 1, 1)

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
        servo_3_layout.addWidget(self.servo_3_dial, 0, 0, 1, 1)

        servo_3_number = QtWidgets.QLCDNumber()
        self.servo_3_dial.valueChanged.connect(servo_3_number.display)  # type: ignore
        self.servo_3_dial.valueChanged.connect(self.update_servos)  # type: ignore
        servo_3_layout.addWidget(servo_3_number, 0, 1, 1, 1)

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
        servo_4_layout.addWidget(self.servo_4_dial, 0, 0, 1, 1)

        servo_4_number = QtWidgets.QLCDNumber()
        self.servo_4_dial.valueChanged.connect(servo_4_number.display)  # type: ignore
        self.servo_4_dial.valueChanged.connect(self.update_servos)  # type: ignore
        servo_4_layout.addWidget(servo_4_number, 0, 1, 1, 1)

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

    def update_leds(self) -> None:
        """
        Update the value of the LEDs based on the current position of the sliders
        """
        red = self.red_led_slider.value()
        green = self.green_led_slider.value()
        blue = self.blue_led_slider.value()

        self.parent_.pcc_connection.set_base_color([0, red, green, blue])

    def update_servos(self) -> None:
        """
        Update the position of the servos based on the current position of the dials
        """
        self.parent_.pcc_connection.set_servo_pct(0, self.servo_1_dial.value())
        self.parent_.pcc_connection.set_servo_pct(1, self.servo_2_dial.value())
        self.parent_.pcc_connection.set_servo_pct(2, self.servo_3_dial.value())
        self.parent_.pcc_connection.set_servo_pct(3, self.servo_4_dial.value())

    def toggle_servo(self, servo: int) -> None:
        """
        Toggle a servo open or closed
        """
        if self.servo_states[servo] == "open":
            self.servo_states[servo] = "close"
        else:
            self.servo_states[servo] = "open"

        self.parent_.pcc_connection.set_servo_open_close(
            servo, self.servo_states[servo]
        )


class ConnectWidget(QtWidgets.QDialog):
    def __init__(self, parent: MainWidget) -> None:
        self.parent_ = parent
        super().__init__()

        self.setWindowTitle("Bell VRC PCC Connection")
        set_icon(self)

    def build(self) -> None:
        layout = QtWidgets.QFormLayout()
        self.setLayout(layout)

        com_port_label = QtWidgets.QLabel("COM Port")
        self.com_port_combo = QtWidgets.QComboBox()
        layout.addRow(com_port_label, self.com_port_combo)

        # baud_rate_label = QtWidgets.QLabel("Baud Rate")
        # self.baud_rate_combo = QtWidgets.QComboBox()
        # layout.addRow(baud_rate_label, self.baud_rate_combo)

        self.connect_button = QtWidgets.QPushButton("Connect")
        layout.addWidget(self.connect_button)

        self.com_port_combo.addItems(list_serial_ports())


def main() -> None:
    # create Qt Application instance
    app = QtWidgets.QApplication()

    # create the main widget
    MainWidget()

    # run
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
