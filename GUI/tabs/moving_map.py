import json
import math
import os
from typing import List, Union

from bell.avr.mqtt.payloads import (
    AvrFcmAttitudeEulerPayload,
    AvrFcmLocationLocalPayload,
)
from lib.color import smear_color
from lib.config import DATA_DIR
from PySide6 import QtCore, QtGui, QtSvgWidgets, QtWidgets

from .base import BaseTabWidget


class ADI(QtWidgets.QGraphicsView):
    # adapted from https://github.com/UlusoyRobotic/PyQt---Stm32F4-Real-Time-Flight-Data-Pitch-and-Roll-Simulator/blob/6edc80de1f054a8a8bcddc984e3be0b3c73d29cd/qfi/qfi_ADI.py

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.m_roll = 0
        self.m_pitch = 0

        self.m_faceDeltaX_new = 0
        self.m_faceDeltaX_old = 0
        self.m_faceDeltaY_new = 0
        self.m_faceDeltaY_old = 0

        self.m_originalHeight = 240
        self.m_originalWidth = 240

        self.setFixedSize(self.m_originalWidth, self.m_originalHeight)

        self.m_originalPixPerDeg = 1.7

        self.m_originalAdiCtr = QtCore.QPointF(120, 120)

        self.m_backZ = -30
        self.m_faceZ = -20
        self.m_ringZ = -10
        self.m_caseZ = 10

        self.setStyleSheet("background: transparent; border: none")
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.setInteractive(False)
        self.setEnabled(False)

        self.m_scene = QtWidgets.QGraphicsScene(self)

        self.setScene(self.m_scene)

        self.m_scaleX = self.width() / self.m_originalWidth
        self.m_scaleY = self.height() / self.m_originalHeight

        # SVG files from https://github.com/marek-cel/QFlightinstruments
        # under MIT license

        self.m_itemBack = QtSvgWidgets.QGraphicsSvgItem(
            os.path.join(DATA_DIR, "assets", "img", "adi_back.svg")
        )
        self.m_itemBack.setCacheMode(QtWidgets.QGraphicsItem.NoCache)
        self.m_itemBack.setZValue(self.m_backZ)
        self.m_itemBack.setTransform(
            QtGui.QTransform.fromScale(self.m_scaleX, self.m_scaleY), True
        )
        self.m_itemBack.setTransformOriginPoint(self.m_originalAdiCtr)
        self.m_scene.addItem(self.m_itemBack)

        self.m_itemFace = QtSvgWidgets.QGraphicsSvgItem(
            os.path.join(DATA_DIR, "assets", "img", "adi_face.svg")
        )
        self.m_itemFace.setCacheMode(QtWidgets.QGraphicsItem.NoCache)
        self.m_itemFace.setZValue(self.m_faceZ)
        self.m_itemFace.setTransform(
            QtGui.QTransform.fromScale(self.m_scaleX, self.m_scaleY), True
        )
        self.m_itemFace.setTransformOriginPoint(self.m_originalAdiCtr)
        self.m_scene.addItem(self.m_itemFace)

        self.m_itemRing = QtSvgWidgets.QGraphicsSvgItem(
            os.path.join(DATA_DIR, "assets", "img", "adi_ring.svg")
        )
        self.m_itemRing.setCacheMode(QtWidgets.QGraphicsItem.NoCache)
        self.m_itemRing.setZValue(self.m_ringZ)
        self.m_itemRing.setTransform(
            QtGui.QTransform.fromScale(self.m_scaleX, self.m_scaleY), True
        )
        self.m_itemRing.setTransformOriginPoint(self.m_originalAdiCtr)
        self.m_scene.addItem(self.m_itemRing)

        self.m_itemCase = QtSvgWidgets.QGraphicsSvgItem(
            os.path.join(DATA_DIR, "assets", "img", "adi_case.svg")
        )
        self.m_itemCase.setCacheMode(QtWidgets.QGraphicsItem.NoCache)
        self.m_itemCase.setZValue(self.m_caseZ)
        self.m_itemCase.setTransform(
            QtGui.QTransform.fromScale(self.m_scaleX, self.m_scaleY), True
        )
        self.m_itemCase.setTransformOriginPoint(self.m_originalAdiCtr)
        self.m_scene.addItem(self.m_itemCase)

        self.centerOn(self.width() / 2, self.height() / 2)

        self.updateView()

    def update(self) -> None:
        self.updateView()
        self.m_faceDeltaX_old = self.m_faceDeltaX_new
        self.m_faceDeltaY_old = self.m_faceDeltaY_new

    def setRoll(self, roll: float) -> None:
        self.m_roll = roll
        self.m_roll = max(self.m_roll, -180)
        self.m_roll = min(self.m_roll, 180)

    def setPitch(self, pitch: float) -> None:
        self.m_pitch = pitch
        self.m_pitch = max(self.m_pitch, -25)
        self.m_pitch = min(self.m_pitch, 25)

    def reset(self) -> None:
        self.setPitch(0)
        self.setRoll(0)
        self.update()

    def updateView(self) -> None:
        self.m_scaleX = self.width() / self.m_originalWidth
        self.m_scaleY = self.height() / self.m_originalHeight

        self.m_itemBack.setRotation(-self.m_roll)
        self.m_itemRing.setRotation(-self.m_roll)
        self.m_itemFace.setRotation(-self.m_roll)

        roll_rad = math.pi * self.m_roll / 180.0
        delta = self.m_originalPixPerDeg * self.m_pitch

        self.m_faceDeltaX_new = self.m_scaleX * delta * math.sin(roll_rad)
        self.m_faceDeltaY_new = self.m_scaleY * delta * math.cos(roll_rad)

        self.m_itemFace.moveBy(
            self.m_faceDeltaX_new - self.m_faceDeltaX_old,
            self.m_faceDeltaY_new - self.m_faceDeltaY_old,
        )

        self.m_scene.update()


class MovingMapGraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        if event.angleDelta().y() > 0:
            self.scale(1.2, 1.2)
        else:
            self.scale(0.8, 0.8)

    def enable_panning(self) -> None:
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

    def disable_panning(self) -> None:
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)


class InfiniteGridGraphicsScene(QtWidgets.QGraphicsScene):
    # how many pixels per meter
    PIXELS_PER_METER = 50
    # how many meters per grid line
    LINE_METER_SPACING = 1

    def drawBackground(
        self, painter: QtGui.QPainter, rect: Union[QtCore.QRectF, QtCore.QRect]
    ) -> None:
        grid_pen = QtGui.QPen(QtGui.QColor(0, 0, 0, 122))
        grid_pen.setWidth(1)

        # dashed line causes weird rendering issues when scrolled off the screen
        # grid_pen.setDashPattern([5.0, 5.0])

        painter.setPen(grid_pen)

        # vertical lines
        for x in range(
            math.floor(rect.topLeft().x()), math.ceil(rect.bottomRight().x())
        ):
            if x % (self.LINE_METER_SPACING * self.PIXELS_PER_METER) == 0:
                painter.drawLine(x, math.ceil(rect.top()), x, math.floor(rect.bottom()))

        # horizontal lines
        for y in range(
            math.floor(rect.topLeft().y()), math.ceil(rect.bottomRight().y())
        ):
            if y % (self.LINE_METER_SPACING * self.PIXELS_PER_METER) == 0:
                painter.drawLine(math.ceil(rect.left()), y, math.floor(rect.right()), y)


class MovingMapGraphicsWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._follow_drone = True

        # record all trails so they can be cleared
        self._tracks: List[QtWidgets.QGraphicsLineItem] = []

        # =========================

        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)

        self.canvas = InfiniteGridGraphicsScene(self)
        self.view = MovingMapGraphicsView(self.canvas)

        layout.addWidget(self.view)

        # add drone icon
        drone_pixmap = QtGui.QIcon(
            os.path.join(DATA_DIR, "assets", "img", "drone_icon.svg")
        ).pixmap(50, 50)
        self.drone_icon = self.canvas.addPixmap(drone_pixmap)
        self.drone_icon.setTransformOriginPoint(
            self.drone_icon.pixmap().width() / 2, self.drone_icon.pixmap().height() / 2
        )

        # center it
        self.drone_icon.setPos(
            -self.drone_icon.pixmap().width() / 2,
            -self.drone_icon.pixmap().height() / 2,
        )
        self.drone_icon.setZValue(999)

    def clear_tracks(self) -> None:
        """
        Clear all tracks.
        """
        for track in self._tracks:
            self.canvas.removeItem(track)

        self._tracks = []

    def follow_drone(self, follow: bool) -> None:
        """
        Enable or disable following the drone.
        """
        self._follow_drone = follow
        if self._follow_drone:
            self.view.disable_panning()
        else:
            self.view.enable_panning()

    def update_drone_location(self, payload: AvrFcmLocationLocalPayload) -> None:
        """
        Update local location information.
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

        new_drone_center_x = payload["dY"] * self.canvas.PIXELS_PER_METER
        new_drone_center_y = -payload["dX"] * self.canvas.PIXELS_PER_METER

        new_drone_corner_x = new_drone_center_x - (self.drone_icon.pixmap().width() / 2)
        new_drone_corner_y = new_drone_center_y - (
            self.drone_icon.pixmap().height() / 2
        )

        color = smear_color(
            (11, 135, 0), (135, 0, 16), value=-payload["dZ"], min_value=0, max_value=20
        )

        # draw track
        track_pen = QtGui.QPen(QtGui.QColor(color[0], color[1], color[2], 122))
        track_pen.setWidth(3)
        self._tracks.append(
            self.canvas.addLine(
                current_drone_center_x,
                current_drone_center_y,
                new_drone_center_x,
                new_drone_center_y,
                track_pen,
            )
        )

        # move icon
        self.drone_icon.setPos(new_drone_corner_x, new_drone_corner_y)

        if self._follow_drone:
            self.view.centerOn(new_drone_center_x, new_drone_center_y)

    def update_drone_attitude(self, payload: AvrFcmAttitudeEulerPayload) -> None:
        """
        Update euler attitude information.
        """
        self.drone_icon.setRotation(payload["yaw"])

    def reset(self) -> None:
        self.drone_icon.setPos(
            -self.drone_icon.pixmap().width() / 2,
            -self.drone_icon.pixmap().height() / 2,
        )

        self.drone_icon.setRotation(0)
        self.clear_tracks()

class MovingMapWidget(BaseTabWidget):
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

        self.follow_drone = True

        self.setWindowTitle("Moving Map")

    def build(self) -> None:
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.moving_map_widget = MovingMapGraphicsWidget(self)
        layout.addWidget(self.moving_map_widget)

        bottom_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(bottom_layout)

        bottom_left_layout = QtWidgets.QVBoxLayout()
        bottom_layout.addLayout(bottom_left_layout)

        self.follow_drone_button = QtWidgets.QPushButton("Unfollow Drone")
        self.follow_drone_button.setMaximumWidth(200)
        self.follow_drone_button.setMinimumHeight(50)
        bottom_left_layout.addWidget(self.follow_drone_button)

        clear_tracks_button = QtWidgets.QPushButton("Clear Tracks")
        clear_tracks_button.setMaximumWidth(200)
        clear_tracks_button.setMinimumHeight(50)
        bottom_left_layout.addWidget(clear_tracks_button)

        self.adi = ADI(self)
        bottom_layout.addWidget(self.adi)

        clear_tracks_button.clicked.connect(self.moving_map_widget.clear_tracks)  # type: ignore
        self.follow_drone_button.clicked.connect(self.toggle_follow_drone)  # type: ignore

    def toggle_follow_drone(self) -> None:
        """
        Toggle the running state.
        """
        self.follow_drone = not self.follow_drone

        if self.follow_drone:
            self.follow_drone_button.setText("Unfollow Drone")
            self.moving_map_widget.follow_drone(True)
        else:
            self.follow_drone_button.setText("Follow Drone")
            self.moving_map_widget.follow_drone(False)

    def update_euler_attitude(self, payload: AvrFcmAttitudeEulerPayload) -> None:
        """
        Update euler attitude information.
        """
        self.moving_map_widget.update_drone_attitude(payload)

        self.adi.setRoll(payload["roll"])
        self.adi.setPitch(payload["pitch"])
        self.adi.update()

    def process_message(self, topic: str, payload: str) -> None:
        """
        Process an incoming message and update the appropriate component
        """
        topic_map = {
            "avr/fcm/location/local": self.moving_map_widget.update_drone_location,
            "avr/fcm/attitude/euler": self.update_euler_attitude,
        }

        # discard topics we don't recognize
        if topic in topic_map:
            data = json.loads(payload)
            topic_map[topic](data)

    def clear(self) -> None:
        self.adi.reset()
        self.moving_map_widget.reset()
