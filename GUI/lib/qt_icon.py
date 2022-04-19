import os

from PySide6 import QtGui, QtWidgets

from .config import DATA_DIR

IMG_DIR = os.path.join(DATA_DIR, "lib", "img")


def set_icon(widget: QtWidgets.QWidget) -> None:
    """
    Set a QtWidget window icon.
    """
    widget.setWindowIcon(QtGui.QIcon(os.path.join(IMG_DIR, "logo.png")))
