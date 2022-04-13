import os
import sys

from PySide6 import QtGui, QtWidgets

if getattr(sys, "frozen", False):
    IMG_DIR = os.path.join(sys._MEIPASS, "img")  # type: ignore
else:
    IMG_DIR = os.path.join(os.path.dirname(__file__), "img")


def set_icon(widget: QtWidgets.QWidget) -> None:
    """
    Set a QtWidget window icon.
    """
    widget.setWindowIcon(QtGui.QIcon(os.path.join(IMG_DIR, "logo.png")))
