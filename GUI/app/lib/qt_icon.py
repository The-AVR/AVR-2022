import os

from PySide6 import QtGui, QtWidgets

from .config import IMG_DIR


def set_icon(widget: QtWidgets.QWidget) -> None:
    """
    Set a QtWidget window icon.
    """
    widget.setWindowIcon(QtGui.QIcon(os.path.join(IMG_DIR, "logo.png")))
