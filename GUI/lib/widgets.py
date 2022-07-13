import contextlib
import os
from typing import Optional

from PySide6 import QtGui, QtWidgets

from .qt_icon import IMG_DIR


class IntLineEdit(QtWidgets.QLineEdit):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setValidator(QtGui.QIntValidator(0, 1000000, self))


class DisplayLineEdit(QtWidgets.QLineEdit):
    def __init__(self, *args, round_digits: Optional[int] = 4, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.round_digits = round_digits

        self.setReadOnly(True)
        self.setStyleSheet("background-color: rgb(220, 220, 220)")
        self.setMaximumWidth(100)

    def setText(self, arg__1: str) -> None:
        # round incoming float values
        if self.round_digits is not None:
            with contextlib.suppress(ValueError):
                arg__1 = str(round(float(arg__1), self.round_digits))

        return super().setText(arg__1)


class StatusLabel(QtWidgets.QWidget):
    # Combination of 2 QLabels to add a status icon
    def __init__(self, text: str):
        super().__init__()

        # create a horizontal layout
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # create a label for the icon
        self.icon = QtWidgets.QLabel()
        self.icon.setFixedWidth(20)
        layout.addWidget(self.icon)
        self.set_health(False)

        # add text label
        layout.addWidget(QtWidgets.QLabel(text))

    def set_health(self, healthy: bool) -> None:
        """
        Set the health state of the status label
        """
        if healthy:
            self.icon.setPixmap(QtGui.QPixmap(os.path.join(IMG_DIR, "green.png")))
        else:
            self.icon.setPixmap(QtGui.QPixmap(os.path.join(IMG_DIR, "red.png")))
