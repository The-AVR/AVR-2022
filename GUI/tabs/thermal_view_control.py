import json
import time
from enum import Enum, auto
from typing import Optional, Tuple

from lib.mqtt_library import VrcPcmSetServoPctMessage
from PySide6 import QtCore, QtGui, QtWidgets

from .base import BaseTabWidget


class Direction(Enum):
    Left = auto()
    Right = auto()
    Up = auto()
    Down = auto()


class JoystickWidget(QtWidgets.QWidget):

    send_message: QtCore.SignalInstance = QtCore.Signal(str, str)  # type: ignore

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

        self.setMinimumSize(100, 100)
        self.movingOffset = QtCore.QPointF(0, 0)
        self.grabCenter = False
        self.__maxDistance = 50
        self.current_y = 0
        self.current_x = 0
        self.lasttime = 0
        self.servoxmin = 10
        self.servoymin = 10
        self.servoxmax = 99
        self.servoymax = 99

    def map_value(
        self, x: float, in_min: int, in_max: int, out_min: int, out_max: int
    ) -> float:
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def move_gimbal(self, x_servo_percent: int, y_servo_percent: int) -> None:
        self.send_message.emit(
            "vrc/pcm/set_servo_pct",
            json.dumps(VrcPcmSetServoPctMessage(servo=2, percent=x_servo_percent)),
        )
        self.send_message.emit(
            "vrc/pcm/set_servo_pct",
            json.dumps(VrcPcmSetServoPctMessage(servo=3, percent=y_servo_percent)),
        )

    def update_servos(self) -> None:
        ms = int(round(time.time() * 1000))
        timesince = ms - self.lasttime
        if timesince < 50:
            return
        self.lasttime = ms
        y_reversed = 100 - self.current_y

        x_servo_percent = round(self.map_value(self.current_x, 0, 100, 10, 99))
        y_servo_percent = round(self.map_value(y_reversed, 0, 100, 10, 99))

        if x_servo_percent < self.servoxmin:
            return
        if y_servo_percent < self.servoymin:
            return
        if x_servo_percent > self.servoxmax:
            return
        if y_servo_percent > self.servoymax:
            return

        self.move_gimbal(x_servo_percent, y_servo_percent)

    def paintEvent(self) -> None:
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

    def _centerEllipse(self) -> QtCore.QRectF:
        if self.grabCenter:
            return QtCore.QRectF(-20, -20, 40, 40).translated(self.movingOffset)
        return QtCore.QRectF(-20, -20, 40, 40).translated(self._center())

    def _center(self) -> QtCore.QPointF:
        return QtCore.QPointF(self.width() / 2, self.height() / 2)

    def _boundJoystick(self, point: QtCore.QPoint) -> QtCore.QPoint:

        if point.x() > (self._center().x() + self.__maxDistance):
            point.setX(int(self._center().x() + self.__maxDistance))
        elif point.x() < (self._center().x() - self.__maxDistance):
            point.setX(int(self._center().x() - self.__maxDistance))

        if point.y() > (self._center().y() + self.__maxDistance):
            point.setY(int(self._center().y() + self.__maxDistance))
        elif point.y() < (self._center().y() - self.__maxDistance):
            point.setY(int(self._center().y() - self.__maxDistance))
        return point

    def joystickDirection(self) -> Optional[Tuple[Direction, float]]:
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

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> QtGui.QMouseEvent:
        self.grabCenter = self._centerEllipse().contains(event.pos())
        return event

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        # self.grabCenter = False
        # self.movingOffset = QtCore.QPointF(0, 0)
        self.update()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.grabCenter:
            self.movingOffset = self._boundJoystick(event.pos())
            self.update()
        # print(self.joystickDirection())
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

        joystick = JoystickWidget(self)
        layout.addWidget(joystick)
