from PySide6 import QtGui, QtWidgets


class IntLineEdit(QtWidgets.QLineEdit):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setValidator(QtGui.QIntValidator(0, 1000000, self))
