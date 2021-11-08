from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

from PySide6 import QtCore, QtGui, QtWidgets

from pcc_library import VRC_Peripheral

import sys, glob
import serial


def list_serial_ports() -> List[str]:
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

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

        self.setup_window = StartupWidget(self)
        self.setup_window.build()
        self.setup_window.connect_button.clicked.connect(self.connect) # type: ignore
        self.setup_window.exec()

    def build(self) -> None:
        pass

    def connect(self) -> None:
        self.pcc_connection = VRC_Peripheral(int(self.setup_window.com_port_combo.currentText()), use_serial=True)
        self.setup_window.close()

    def update_led(self) -> None:
        red = self.red_led_slider.value()
        green = self.green_led_slider.value()
        blue = self.blue_led_slider.value()

        self.pcc_connection.set_base_color([0, red, green, blue])

class StartupWidget(QtWidgets.QDialog):
    def __init__(self, parent: MainWidget) -> None:
        self.parent_ = parent
        super().__init__()

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
