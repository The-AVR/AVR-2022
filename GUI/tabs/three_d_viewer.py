import json
import os

import numpy as np
import stl
from bell.avr.mqtt.payloads import (
    AvrFcmAttitudeEulerPayload,
    AvrFcmLocationLocalPayload,
)
from pyqtgraph.opengl import GLGridItem, GLMeshItem, GLViewWidget, MeshData
from PySide6 import QtGui, QtWidgets

from ..lib.config import DATA_DIR
from .base import BaseTabWidget


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
        stl_mesh = stl.mesh.Mesh.from_file(os.path.join(DATA_DIR, "assets", "stl", "cube.stl"))
        points = stl_mesh.points.reshape(-1, 3)
        faces = np.arange(points.shape[0]).reshape(-1, 3)

        drone_mesh_data = MeshData(vertexes=points, faces=faces)
        self.drone_mesh = GLMeshItem(
            meshdata=drone_mesh_data,
            smooth=True,
            drawFaces=True,
            drawEdges=False,
            edgeColor=(0, 1, 0, 1),
        )
        self.view_widget.addItem(self.drone_mesh)

        # build the infinite floor
        self.view_widget.addItem(GLGridItem(QtGui.QVector3D(1000, 1000, 1)))

    def update_local_location(self, payload: AvrFcmLocationLocalPayload) -> None:
        """
        Update local location information
        """
        self.drone_mesh.translate(payload["dX"], payload["dY"], payload["dZ"])

    def update_euler_attitude(self, payload: AvrFcmAttitudeEulerPayload) -> None:
        """
        Update euler attitude information
        """
        self.drone_mesh.rotate(payload["roll"], 1, 0, 0)
        self.drone_mesh.rotate(payload["pitch"], 0, 1, 0)
        self.drone_mesh.rotate(payload["yaw"], 0, 0, 1)

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
