import base64
import json
import math
import time
from enum import Enum, auto
from typing import List, Optional, Tuple

import colour
import numpy as np
import scipy.interpolate
from bell.avr.mqtt.payloads import AvrPcmFireLaserPayload, AvrPcmSetServoPctPayload
from PySide6 import QtCore, QtGui, QtWidgets

from .base import BaseTabWidget


def map_value(
    x: float, in_min: float, in_max: float, out_min: float, out_max: float
) -> float:
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def constrain(val: int, min_val: int, max_val: int) -> int:
    return min(max_val, max(min_val, val))


class Direction(Enum):
    Left = auto()
    Right = auto()
    Up = auto()
    Down = auto()


class ThermalView(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

        # canvas size
        self.width_ = 300
        self.height_ = self.width_

        # pixels within canvas
        self.pixels_x = 30
        self.pixels_y = self.pixels_x

        self.pixel_width = self.width_ / self.pixels_x
        self.pixel_height = self.height_ / self.pixels_y

        # low range of the sensor (this will be blue on the screen)
        self.MINTEMP = 20.0

        # high range of the sensor (this will be red on the screen)
        self.MAXTEMP = 32.0

        # how many color values we can have
        self.COLORDEPTH = 1024

        # how many pixels the camera is
        self.camera_x = 8
        self.camera_y = self.camera_x
        self.camera_total = self.camera_x * self.camera_y

        # create list of x/y points
        self.points = [
            (math.floor(ix / self.camera_x), (ix % self.camera_y))
            for ix in range(self.camera_total)
        ]
        # i'm not fully sure what this does
        self.grid_x, self.grid_y = np.mgrid[
            0 : self.camera_x - 1 : self.camera_total / 2j,
            0 : self.camera_y - 1 : self.camera_total / 2j,
        ]

        # create avaiable colors
        self.colors = [
            (int(c.red * 255), int(c.green * 255), int(c.blue * 255))
            for c in list(
                colour.Color("indigo").range_to(colour.Color("red"), self.COLORDEPTH)
            )
        ]

        # create canvas
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.canvas = QtWidgets.QGraphicsScene()
        self.view = QtWidgets.QGraphicsView(self.canvas)
        self.view.setGeometry(0, 0, self.width_, self.height_)

        layout.addWidget(self.view)

        # need a bit of padding for the edges of the canvas
        self.setFixedSize(self.width_ + 50, self.height_ + 50)

    def update_canvas(self, pixels: List[int]) -> None:
        float_pixels = [
            map_value(p, self.MINTEMP, self.MAXTEMP, 0, self.COLORDEPTH - 1)
            for p in pixels
        ]

        bicubic = scipy.interpolate.griddata(
            self.points, float_pixels, (self.grid_x, self.grid_y), method="cubic"
        )

        pen = QtGui.QPen(QtCore.Qt.NoPen)
        self.canvas.clear()

        for ix, row in enumerate(bicubic):
            for jx, pixel in enumerate(row):
                brush = QtGui.QBrush(
                    QtGui.QColor(
                        *self.colors[constrain(int(pixel), 0, self.COLORDEPTH - 1)]
                    )
                )
                self.canvas.addRect(
                    self.pixel_width * jx,
                    self.pixel_height * ix,
                    self.pixel_width,
                    self.pixel_height,
                    pen,
                    brush,
                )


class JoystickWidget(BaseTabWidget):
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

        self.setFixedSize(150, 150)

        self.movingOffset = QtCore.QPointF(0, 0)

        self.grabCenter = False
        self.__maxDistance = 50

        self.lasttime = 0

        self.current_y = 0
        self.current_x = 0

        self.servoxmin = 10
        self.servoymin = 10
        self.servoxmax = 99
        self.servoymax = 99

    def _center(self) -> QtCore.QPointF:
        """
        Return the center of the widget.
        """
        return QtCore.QPointF(self.width() / 2, self.height() / 2)

    def move_gimbal(self, x_servo_percent: int, y_servo_percent: int) -> None:
        self.send_message(
            "avr/pcm/set_servo_pct",
            AvrPcmSetServoPctPayload(servo=2, percent=x_servo_percent),
        )
        self.send_message(
            "avr/pcm/set_servo_pct",
            AvrPcmSetServoPctPayload(servo=3, percent=y_servo_percent),
        )

    def update_servos(self) -> None:
        """
        Update the servos on joystick movement.
        """
        ms = int(round(time.time() * 1000))
        timesince = ms - self.lasttime
        if timesince < 50:
            return
        self.lasttime = ms

        y_reversed = 100 - self.current_y

        x_servo_percent = round(map_value(self.current_x, 0, 100, 10, 99))
        y_servo_percent = round(map_value(y_reversed, 0, 100, 10, 99))

        if x_servo_percent < self.servoxmin:
            return
        if y_servo_percent < self.servoymin:
            return
        if x_servo_percent > self.servoxmax:
            return
        if y_servo_percent > self.servoymax:
            return

        self.move_gimbal(x_servo_percent, y_servo_percent)

    def _centerEllipse(self) -> QtCore.QRectF:
        # sourcery skip: assign-if-exp
        if self.grabCenter:
            center = self.movingOffset
        else:
            center = self._center()

        return QtCore.QRectF(-20, -20, 40, 40).translated(center)

    def _bound_joystick(self, point: QtCore.QPoint) -> QtCore.QPoint:
        """
        If the joystick is leaving the widget, bound it to the edge of the widget.
        """
        if point.x() > (self._center().x() + self.__maxDistance):
            point.setX(int(self._center().x() + self.__maxDistance))
        elif point.x() < (self._center().x() - self.__maxDistance):
            point.setX(int(self._center().x() - self.__maxDistance))

        if point.y() > (self._center().y() + self.__maxDistance):
            point.setY(int(self._center().y() + self.__maxDistance))
        elif point.y() < (self._center().y() - self.__maxDistance):
            point.setY(int(self._center().y() - self.__maxDistance))
        return point

    def joystick_direction(self) -> Optional[Tuple[Direction, float]]:
        """
        Retrieve the direction the joystick is moving
        """
        if not self.grabCenter:
            return None

        normVector = QtCore.QLineF(self._center(), self.movingOffset)
        currentDistance = normVector.length()
        angle = normVector.angle()

        distance = min(currentDistance / self.__maxDistance, 1.0)

        if 45 <= angle < 135:
            return (Direction.Up, distance)
        elif 135 <= angle < 225:
            return (Direction.Left, distance)
        elif 225 <= angle < 315:
            return (Direction.Down, distance)

        return (Direction.Right, distance)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        bounds = QtCore.QRectF(
            -self.__maxDistance,
            -self.__maxDistance,
            self.__maxDistance * 2,
            self.__maxDistance * 2,
        ).translated(self._center())

        # painter.drawEllipse(bounds)
        painter.drawRect(bounds)
        painter.setBrush(QtCore.Qt.black)

        painter.drawEllipse(self._centerEllipse())

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> QtGui.QMouseEvent:
        """
        On a mouse press, check if we've clicked on the center of the joystick.
        """
        self.grabCenter = self._centerEllipse().contains(event.pos())
        return event

    def mouseReleaseEvent(self, event: QtCore.QEvent) -> None:
        # self.grabCenter = False
        # self.movingOffset = QtCore.QPointF(0, 0)
        self.update()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.grabCenter:
            self.movingOffset = self._bound_joystick(event.pos())
            self.update()

        # print(self.joystick_direction())
        self.current_x = self.movingOffset.x() - self._center().x() + self.__maxDistance
        self.current_y = self.movingOffset.y() - self._center().y() + self.__maxDistance
        self.update_servos()


class ThermalViewControlWidget(BaseTabWidget):
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

        self.setWindowTitle("Thermal View/Control")

    def build(self) -> None:
        """
        Build the GUI layout
        """
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)

        # viewer
        viewer_groupbox = QtWidgets.QGroupBox("Viewer")
        viewer_layout = QtWidgets.QHBoxLayout()
        viewer_groupbox.setLayout(viewer_layout)

        self.viewer = ThermalView(self)
        viewer_layout.addWidget(self.viewer)

        layout.addWidget(viewer_groupbox)

        # joystick
        joystick_groupbox = QtWidgets.QGroupBox("Joystick")
        joystick_layout = QtWidgets.QVBoxLayout()
        joystick_groupbox.setLayout(joystick_layout)

        sub_joystick_layout = QtWidgets.QHBoxLayout()
        joystick_layout.addLayout(sub_joystick_layout)

        joystick = JoystickWidget(self)
        sub_joystick_layout.addWidget(joystick)

        fire_laser_button = QtWidgets.QPushButton("Laser On")
        joystick_layout.addWidget(fire_laser_button)

        layout.addWidget(joystick_groupbox)

        # connect signals
        joystick.emit_message.connect(self.emit_message.emit)

        fire_laser_button.clicked.connect(  # type: ignore
            lambda: self.send_message("avr/pcm/fire_laser", AvrPcmFireLaserPayload())
        )

        # don't allow us to shrink below size hint
        self.setMinimumSize(self.sizeHint())

    def process_message(self, topic: str, payload: str) -> None:
        """
        Process an incoming message and update the appropriate component
        """
        # discard topics we don't recognize
        if topic != "avr/thermal/reading":
            return

        data = json.loads(payload)["data"]

        # decode the payload
        base64Decoded = data.encode("utf-8")
        asbytes = base64.b64decode(base64Decoded)
        pixel_ints = list(bytearray(asbytes))

        # update the canvase
        # pixel_ints = data
        self.viewer.update_canvas(pixel_ints)
