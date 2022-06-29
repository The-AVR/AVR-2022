import json
import os

from bell.avr.mqtt.payloads import (
    AvrFcmAttitudeEulerPayload,
    AvrFcmLocationLocalPayload,
)
from lib.config import DATA_DIR
from PySide6 import QtGui, QtWidgets, QtCore

from .base import BaseTabWidget


class MovingMapWidget(BaseTabWidget):
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

        # canvas size
        # self.width_ = 300
        # self.height_ = self.width_

        # how many pixels per meter
        self.pixels_per_meter = 50
        # how many meters per grid line
        self.line_meter_spacing = 1
        # number of grid lines to draw
        self.number_of_grid_lines = 20

        self._outer_limit = (
            self.pixels_per_meter * self.line_meter_spacing * self.number_of_grid_lines
        )

        self.setWindowTitle("Moving Map")

    def build(self) -> None:
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.canvas = QtWidgets.QGraphicsScene()

        self.view = QtWidgets.QGraphicsView(self.canvas)
        # self.view.setGeometry(0, 0, self.width_, self.height_)

        layout.addWidget(self.view)

        # build a grid
        grid_pen = QtGui.QPen(QtGui.QColor(0, 0, 0, 122))
        grid_pen.setWidth(1)
        grid_pen.setDashPattern([5.0, 5.0])

        # vertical lines
        for x in range(
            -self._outer_limit,
            self._outer_limit + 1,
            self.line_meter_spacing * self.pixels_per_meter,
        ):
            line = self.canvas.addLine(
                x, -self._outer_limit, x, self._outer_limit, grid_pen
            )
            line.setZValue(-999)

        # horizontal lines
        for y in range(
            -self._outer_limit,
            self._outer_limit + 1,
            self.line_meter_spacing * self.pixels_per_meter,
        ):
            line = self.canvas.addLine(
                -self._outer_limit, y, self._outer_limit, y, grid_pen
            )
            line.setZValue(-999)

        # add drone icon
        drone_pixmap = QtGui.QPixmap(
            os.path.join(DATA_DIR, "assets", "img", "drone_icon.svg")
        )
        drone_pixmap.scaled(20, 20, QtCore.Qt.KeepAspectRatio)
        self.drone_icon = self.canvas.addPixmap(drone_pixmap)

        # center it
        self.drone_icon.setPos(
            -self.drone_icon.pixmap().width() / 2,
            -self.drone_icon.pixmap().height() / 2,
        )
        self.drone_icon.setZValue(999)

    def update_local_location(self, payload: AvrFcmLocationLocalPayload) -> None:
        """
        Update local location information
        """
        # drone XYZ is NED
        # Qt however consider top left 0, 0

        current_drone_corner_x = self.drone_icon.x()
        current_drone_corner_y = self.drone_icon.y()

        current_drone_center_x = current_drone_corner_x + (
            self.drone_icon.pixmap().width() / 2
        )
        current_drone_center_y = current_drone_corner_y + (
            self.drone_icon.pixmap().height() / 2
        )

        new_drone_center_x = payload["dY"] * self.pixels_per_meter
        new_drone_center_y = -payload["dX"] * self.pixels_per_meter

        new_drone_corner_x = new_drone_center_x - (self.drone_icon.pixmap().width() / 2)
        new_drone_corner_y = new_drone_center_y - (
            self.drone_icon.pixmap().height() / 2
        )

        # draw track
        track_pen = QtGui.QPen(QtGui.QColor(255, 0, 0, 255))
        track_pen.setWidth(3)
        self.canvas.addLine(
            current_drone_center_x,
            current_drone_center_y,
            new_drone_center_x,
            new_drone_center_y,
            track_pen,
        )

        # move icon
        self.drone_icon.setPos(new_drone_corner_x, new_drone_corner_y)

    def update_euler_attitude(self, payload: AvrFcmAttitudeEulerPayload) -> None:
        """
        Update euler attitude information
        """
        self.drone_icon.setRotation(payload["yaw"])

    def process_message(self, topic: str, payload: str) -> None:
        """
        Process an incoming message and update the appropriate component
        """
        topic_map = {
            "avr/fcm/location/local": self.update_local_location,
            "avr/fcm/attitude/euler": self.update_euler_attitude,
        }

        # discard topics we don't recognize
        if topic in topic_map:
            data = json.loads(payload)
            topic_map[topic](data)
