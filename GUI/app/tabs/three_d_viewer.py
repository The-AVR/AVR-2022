import json
import os

import numpy as np
import stl
from app.tabs.base import BaseTabWidget
from bell.avr.mqtt.payloads import (
    AvrFcmAttitudeEulerPayload,
    AvrFcmLocationLocalPayload,
)
from app.lib.config import DATA_DIR
from pyqtgraph.opengl import GLGridItem, GLMeshItem, GLViewWidget, MeshData
from PySide6 import Qt3DRender, QtGui, QtWidgets


class AbsoluteGLMeshItem(GLMeshItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.origin = (0,0,0)

        self._current_x = 0
        self._current_y = 0
        self._current_z = 0

        self._current_r = 0
        self._current_p = 0
        self._current_yaw = 0

    def set_position(self, x, y, z):
        self.translate(x - self._current_x, y - self._current_y, z - self._current_z)
        self._current_x = x
        self._current_y = y
        self._current_z = z

    def set_rotation(self, r, p, y):
        # record current position
        x_before = self._current_x
        y_before = self._current_y
        z_before = self._current_z

        # move to 0,0,0 so we can rotate around the origin
        self.set_position(*self.origin)

        # rotate all three axes
        self.rotate(r - self._current_r, 1, 0, 0)
        self.rotate(p - self._current_p, 0, 1, 0)
        self.rotate(y - self._current_yaw, 0, 0, 1)

        # reset position to previous position
        self.set_position(x_before, y_before, z_before)

        self._current_r = r
        self._current_p = p
        self._current_yaw = y


class ThreeDViewerWidget(BaseTabWidget):
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

        self.setWindowTitle("3D Viewer")

    def build(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)

        self.view_widget = GLViewWidget()
        layout.addWidget(self.view_widget)

        # build the drone model
        stl_mesh = stl.mesh.Mesh.from_file(
            os.path.join(DATA_DIR, "assets", "stl", "arrow.stl")
        )
        points = stl_mesh.points.reshape(-1, 3)
        faces = np.arange(points.shape[0]).reshape(-1, 3)

        drone_mesh_data = MeshData(vertexes=points, faces=faces)
        self.drone_mesh = AbsoluteGLMeshItem(
            meshdata=drone_mesh_data,
            smooth=True,
            drawFaces=True,
            drawEdges=True,
            edgeColor=(0, 0, 0, 1),
        )
        self.drone_mesh.origin = (0, 0, 0.5)
        self.drone_mesh.scale(0.1, 0.1, 0.1)
        self.view_widget.addItem(self.drone_mesh)

        # build the infinite floor
        grid = GLGridItem(QtGui.QVector3D(1000, 1000, 1))
        grid.setSpacing(10, 10, 1)
        self.view_widget.addItem(grid)

    def update_local_location(self, payload: AvrFcmLocationLocalPayload) -> None:
        """
        Update local location information
        """
        # drone XYZ is NED
        # https://learnopengl.com/Getting-started/Coordinate-Systems
        self.drone_mesh.set_position(payload["dY"], payload["dX"], -payload["dZ"])

    def update_euler_attitude(self, payload: AvrFcmAttitudeEulerPayload) -> None:
        """
        Update euler attitude information
        """
        self.drone_mesh.set_rotation(payload["pitch"], payload["roll"], -payload["yaw"])

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
