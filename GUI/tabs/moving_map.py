import json
import math
import os
from typing import List, Union

from bell.avr.mqtt.payloads import (
    AvrFcmAttitudeEulerPayload,
    AvrFcmLocationLocalPayload,
)
from lib.calc import normalize_value
from lib.color import smear_color
from lib.config import IMG_DIR
from PySide6 import QtCore, QtGui, QtSvgWidgets, QtWidgets

from .base import BaseTabWidget


class AttitudeIndicator(QtWidgets.QGraphicsView):
    # adapted from https://github.com/UlusoyRobotic/PyQt---Stm32F4-Real-Time-Flight-Data-Pitch-and-Roll-Simulator/blob/6edc80de1f054a8a8bcddc984e3be0b3c73d29cd/qfi/qfi_ADI.py

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # maintain persistent values
        self._roll = 0
        self._pitch = 0

        self._face_delta_x_new = 0
        self._face_delta_x_old = 0
        self._face_delta_y_new = 0
        self._face_delta_y_old = 0

        # constants
        self._original_width = 240
        self._original_height = 240

        self._original_pizel_per_deg = 1.7
        self._original_center = QtCore.QPointF(
            self._original_width / 2, self._original_height / 2
        )

        self._back_z = -30
        self._face_z = -20
        self._ring_z = -10
        self._case_z = 10

        # styling
        self.setFixedSize(self._original_width, self._original_height)
        self.setStyleSheet("background: transparent; border: none")
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # create a graphics scene to draw on
        self._scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self._scene)

        self._scale_x = self.width() / self._original_width
        self._scale_y = self.height() / self._original_height

        # SVG files from https://github.com/marek-cel/QFlightinstruments
        # under MIT license

        self._item_back = QtSvgWidgets.QGraphicsSvgItem(
            os.path.join(IMG_DIR, "attitude_indicator_back.svg")
        )
        self._item_back.setZValue(self._back_z)
        self._item_back.setTransform(
            QtGui.QTransform.fromScale(self._scale_x, self._scale_y), True
        )
        self._item_back.setTransformOriginPoint(self._original_center)
        self._scene.addItem(self._item_back)

        self._item_face = QtSvgWidgets.QGraphicsSvgItem(
            os.path.join(IMG_DIR, "attitude_indicator_face.svg")
        )
        self._item_face.setZValue(self._face_z)
        self._item_face.setTransform(
            QtGui.QTransform.fromScale(self._scale_x, self._scale_y), True
        )
        self._item_face.setTransformOriginPoint(self._original_center)
        self._scene.addItem(self._item_face)

        self._item_ring = QtSvgWidgets.QGraphicsSvgItem(
            os.path.join(IMG_DIR, "attitude_indicator_ring.svg")
        )
        self._item_ring.setZValue(self._ring_z)
        self._item_ring.setTransform(
            QtGui.QTransform.fromScale(self._scale_x, self._scale_y), True
        )
        self._item_ring.setTransformOriginPoint(self._original_center)
        self._scene.addItem(self._item_ring)

        self._item_case = QtSvgWidgets.QGraphicsSvgItem(
            os.path.join(IMG_DIR, "attitude_indicator_case.svg")
        )
        self._item_case.setZValue(self._case_z)
        self._item_case.setTransform(
            QtGui.QTransform.fromScale(self._scale_x, self._scale_y), True
        )
        self._item_case.setTransformOriginPoint(self._original_center)
        self._scene.addItem(self._item_case)

        # center on the middle of the scene
        self.centerOn(self.width() / 2, self.height() / 2)
        self._update_view()

    def update(self) -> None:
        """
        Trigger a re-draw of the indicator.
        """
        self._update_view()
        self._face_delta_x_old = self._face_delta_x_new
        self._face_delta_y_old = self._face_delta_y_new

    def set_roll(self, roll: float) -> None:
        """
        Set the current roll value.
        """
        self._roll = roll
        self._roll = max(self._roll, -180)
        self._roll = min(self._roll, 180)

    def set_pitch(self, pitch: float) -> None:
        """
        Set the current pitch value.
        """
        self._pitch = pitch
        self._pitch = max(self._pitch, -25)
        self._pitch = min(self._pitch, 25)

    def reset(self) -> None:
        """
        Reset the indicator back to a 0 roll and 0 pitch.
        """
        self.set_pitch(0)
        self.set_roll(0)
        self.update()

    def _update_view(self) -> None:
        """
        Re-draw the indicator.
        """
        self._scale_x = self.width() / self._original_width
        self._scale_y = self.height() / self._original_height

        self._item_back.setRotation(-self._roll)
        self._item_ring.setRotation(-self._roll)
        self._item_face.setRotation(-self._roll)

        roll_rad = math.radians(self._roll)
        delta = self._original_pizel_per_deg * self._pitch

        self._face_delta_x_new = self._scale_x * delta * math.sin(roll_rad)
        self._face_delta_y_new = self._scale_y * delta * math.cos(roll_rad)

        self._item_face.moveBy(
            self._face_delta_x_new - self._face_delta_x_old,
            self._face_delta_y_new - self._face_delta_y_old,
        )

        self._scene.update()


class DroneAltitudeWidget(QtWidgets.QWidget):

    GROUND_WIDTH = 3

    DRONE_ICON_WIDTH = 50
    DRONE_ICON_HEIGHT = 50

    CANVAS_HEIGHT = 240
    CANVAS_WIDTH = 120

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        self.canvas = QtWidgets.QGraphicsScene(self)
        self.view = QtWidgets.QGraphicsView(self.canvas)
        self.view.setSceneRect(
            0, 0, self.CANVAS_WIDTH, self.CANVAS_HEIGHT + self.GROUND_WIDTH
        )
        self.view.setStyleSheet("border: 0px")

        layout.addWidget(self.view)

        # add drone icon
        drone_pixmap = QtGui.QIcon(os.path.join(IMG_DIR, "drone_side_icon.png")).pixmap(
            self.DRONE_ICON_WIDTH, self.DRONE_ICON_HEIGHT
        )
        self.drone_icon = self.canvas.addPixmap(drone_pixmap)

        # add ground
        ground_pen = QtGui.QPen(QtGui.QColor(120, 90, 8, 255))
        ground_pen.setWidth(self.GROUND_WIDTH)
        self.canvas.addLine(
            0, self.CANVAS_HEIGHT, self.CANVAS_WIDTH, self.CANVAS_HEIGHT, ground_pen
        )

        sub_layout = QtWidgets.QVBoxLayout()
        sub_layout.addStretch()

        # add altimeter
        self.altitude_number = QtWidgets.QLCDNumber(self)
        self.altitude_number.setFixedHeight(30)
        sub_layout.addWidget(self.altitude_number)

        # add altimeter label
        sub_layout.addWidget(QtWidgets.QLabel("Meters"))
        sub_layout.addStretch()

        layout.addLayout(sub_layout)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        # put drone on the ground
        self.set_altitude(0)

    def set_altitude(self, altitude: float) -> None:
        # flip because negative is up
        altitude *= -1

        # normalize value
        norm_altitude = normalize_value(altitude, 0, 20)

        self.drone_icon.setPos(
            (self.CANVAS_WIDTH / 2) - (self.DRONE_ICON_WIDTH / 2),
            (
                (self.CANVAS_HEIGHT * (1 - norm_altitude))
                - (self.GROUND_WIDTH / 2)
                - self.DRONE_ICON_HEIGHT
            ),
        )
        self.altitude_number.display(altitude)

    def reset(self) -> None:
        self.set_altitude(0)


class MovingMapGraphicsView(QtWidgets.QGraphicsView):
    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        """
        Override the default scroll event to allow zoom in and out
        """
        scroll_factor = 0.2

        if event.angleDelta().y() > 0:
            self.scale(1 + scroll_factor, 1 + scroll_factor)
        else:
            self.scale(1 - scroll_factor, 1 - scroll_factor)

    def enable_panning(self) -> None:
        """
        Enable panning within the view.
        """
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

    def disable_panning(self) -> None:
        """
        Disable panning within the view, if the viewport is being
        driven programmatically
        """
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)


class InfiniteGridGraphicsScene(QtWidgets.QGraphicsScene):
    """
    A QGraphicsScene with an infinite grid background.
    """

    # how many pixels per meter
    PIXELS_PER_METER = 50
    # how many meters per grid line
    LINE_METER_SPACING = 1

    def drawBackground(
        self, painter: QtGui.QPainter, rect: Union[QtCore.QRectF, QtCore.QRect]
    ) -> None:
        """
        Draws a grid within the given viewport.
        """
        grid_pen = QtGui.QPen(QtGui.QColor(0, 0, 0, 122))
        grid_pen.setWidth(1)

        # dashed line causes weird rendering issues when scrolled off the screen
        # grid_pen.setDashPattern([5.0, 5.0])

        painter.setPen(grid_pen)

        # Qt thinks in a 0,0 is the top-left corner coordinate system

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

    HOME_ICON_WIDTH = 50
    HOME_ICON_HEIGHT = 50

    DRONE_ICON_WIDTH = 80
    DRONE_ICON_HEIGHT = 80

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # record all trails so they can be cleared
        self._tracks: List[QtWidgets.QGraphicsLineItem] = []

        # =========================

        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)

        self.canvas = InfiniteGridGraphicsScene(self)
        self.view = MovingMapGraphicsView(self.canvas)

        layout.addWidget(self.view)

        # add home icon
        home_pixmap = QtGui.QIcon(os.path.join(IMG_DIR, "home_icon.png")).pixmap(
            self.HOME_ICON_WIDTH, self.HOME_ICON_HEIGHT
        )
        self.home_icon = self.canvas.addPixmap(home_pixmap)
        self.home_icon.setPos(
            -self.HOME_ICON_WIDTH / 2,
            -self.HOME_ICON_HEIGHT / 2,
        )
        self.home_icon.setZValue(-10)

        # add drone icon
        drone_pixmap = QtGui.QIcon(os.path.join(IMG_DIR, "drone_top_icon.svg")).pixmap(
            self.DRONE_ICON_WIDTH, self.DRONE_ICON_HEIGHT
        )
        self.drone_icon = self.canvas.addPixmap(drone_pixmap)
        self.drone_icon.setTransformOriginPoint(
            self.DRONE_ICON_WIDTH / 2, self.DRONE_ICON_HEIGHT / 2
        )

        # center it
        self.drone_icon.setPos(
            -self.DRONE_ICON_WIDTH / 2,
            -self.DRONE_ICON_HEIGHT / 2,
        )
        self.drone_icon.setZValue(999)

        self.follow_drone(True)

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
            self.view.centerOn(self.drone_icon)
        else:
            self.view.enable_panning()

    def update_drone_location(self, x: float, y: float, z: float) -> None:
        """
        Update local location information.
        """
        # drone XYZ is NED
        # Qt however consider top left 0, 0

        # current top-left corner of the drone icon
        current_drone_corner_x = self.drone_icon.x()
        current_drone_corner_y = self.drone_icon.y()

        # current center of the drone icon
        current_drone_center_x = current_drone_corner_x + (self.DRONE_ICON_WIDTH / 2)
        current_drone_center_y = current_drone_corner_y + (self.DRONE_ICON_HEIGHT / 2)

        # new center of the drone icon
        new_drone_center_x = y * self.canvas.PIXELS_PER_METER
        new_drone_center_y = -x * self.canvas.PIXELS_PER_METER

        # new top-left corner of the drone icon
        new_drone_corner_x = new_drone_center_x - (self.DRONE_ICON_WIDTH / 2)
        new_drone_corner_y = new_drone_center_y - (self.DRONE_ICON_HEIGHT / 2)

        # go from brown to blue as the altitude increases
        color = smear_color(
            (120, 90, 8),
            (73, 205, 235),
            value=-z,
            min_value=0,
            max_value=20,
        )

        # draw track
        track_pen = QtGui.QPen(QtGui.QColor(color[0], color[1], color[2], 200))
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

        # set limit on the number of tracks that are drawn
        # too high of a limit will cause track removal to slow noticably
        if len(self._tracks) > 5000:
            self.canvas.removeItem(self._tracks.pop(0))

        # move icon
        self.drone_icon.setPos(new_drone_corner_x, new_drone_corner_y)

        if self._follow_drone:
            # needed to allow time for GraphicsScene to redraw
            QtGui.QGuiApplication.processEvents()
            self.view.centerOn(self.drone_icon)

    def update_drone_attitude(self, yaw: float) -> None:
        """
        Update euler attitude information.
        """
        self.drone_icon.setRotation(yaw)

    def reset(self) -> None:
        """
        Reset the drone icon's position and clear the tracks.
        """
        self.drone_icon.setPos(
            -self.DRONE_ICON_WIDTH / 2,
            -self.DRONE_ICON_HEIGHT / 2,
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

        self.attitude_indicator = AttitudeIndicator(self)
        bottom_layout.addWidget(self.attitude_indicator)

        self.altitude_indicator = DroneAltitudeWidget(self)
        bottom_layout.addWidget(self.altitude_indicator)

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
        self.moving_map_widget.update_drone_attitude(payload["yaw"])

        self.attitude_indicator.set_roll(payload["roll"])
        self.attitude_indicator.set_pitch(payload["pitch"])
        self.attitude_indicator.update()

    def update_location_local(self, payload: AvrFcmLocationLocalPayload) -> None:
        """
        Update euler attitude information.
        """
        self.moving_map_widget.update_drone_location(
            payload["dX"], payload["dY"], payload["dZ"]
        )
        self.altitude_indicator.set_altitude(payload["dZ"])

    def process_message(self, topic: str, payload: str) -> None:
        """
        Process an incoming message and update the appropriate component
        """
        topic_map = {
            "avr/fcm/location/local": self.update_location_local,
            "avr/fcm/attitude/euler": self.update_euler_attitude,
        }

        # discard topics we don't recognize
        if topic in topic_map:
            data = json.loads(payload)
            topic_map[topic](data)

    def clear(self) -> None:
        """
        Reset the widget to a starting state.
        """
        self.attitude_indicator.reset()
        self.moving_map_widget.reset()
        self.altitude_indicator.reset()
