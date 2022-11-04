from __future__ import annotations

import functools
from typing import List

from bell.avr.mqtt.payloads import (
    AvrAutonomousBuildingDropPayload,
    AvrAutonomousEnablePayload,
)
from PySide6 import QtCore, QtWidgets

from ..lib.color import wrap_text
from .base import BaseTabWidget


class AutonomyWidget(BaseTabWidget):
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

        self.setWindowTitle("Autonomy")

    def build(self) -> None:
        """
        Build the GUI layout
        """
        layout = QtWidgets.QGridLayout(self)
        self.setLayout(layout)

        # ==========================
        # Autonomous mode
        autonomous_groupbox = QtWidgets.QGroupBox("Autonomous")
        autonomous_layout = QtWidgets.QHBoxLayout()
        autonomous_groupbox.setLayout(autonomous_layout)

        autonomous_enable_button = QtWidgets.QPushButton("Enable")
        autonomous_enable_button.clicked.connect(lambda: self.set_autonomous(True))  # type: ignore
        autonomous_layout.addWidget(autonomous_enable_button)

        autonomous_disable_button = QtWidgets.QPushButton("Disable")
        autonomous_disable_button.clicked.connect(lambda: self.set_autonomous(False))  # type: ignore
        autonomous_layout.addWidget(autonomous_disable_button)

        self.autonomous_label = QtWidgets.QLabel()
        self.autonomous_label.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        autonomous_layout.addWidget(self.autonomous_label)

        layout.addWidget(autonomous_groupbox, 0, 0, 1, 1)

        # ==========================
        # Buildings
        self.number_of_buildings = 6
        self.building_labels: List[QtWidgets.QLabel] = []

        buildings_groupbox = QtWidgets.QGroupBox("Buildings")
        buildings_layout = QtWidgets.QVBoxLayout()
        buildings_groupbox.setLayout(buildings_layout)

        building_all_layout = QtWidgets.QHBoxLayout()

        building_all_enable_button = QtWidgets.QPushButton("Enable All Drops")
        building_all_enable_button.clicked.connect(lambda: self.set_building_all(True))  # type: ignore
        building_all_layout.addWidget(building_all_enable_button)

        building_all_disable_button = QtWidgets.QPushButton("Disable All Drops")
        building_all_disable_button.clicked.connect(lambda: self.set_building_all(False))  # type: ignore
        building_all_layout.addWidget(building_all_disable_button)

        buildings_layout.addLayout(building_all_layout)

        for i in range(self.number_of_buildings):
            building_groupbox = QtWidgets.QGroupBox(f"Building {i}")
            building_layout = QtWidgets.QHBoxLayout()
            building_groupbox.setLayout(building_layout)

            building_enable_button = QtWidgets.QPushButton("Enable Drop")
            building_enable_button.clicked.connect(functools.partial(self.set_building, i, True))  # type: ignore
            building_layout.addWidget(building_enable_button)

            building_disable_button = QtWidgets.QPushButton("Disable Drop")
            building_disable_button.clicked.connect(functools.partial(self.set_building, i, False))  # type: ignore
            building_layout.addWidget(building_disable_button)

            building_label = QtWidgets.QLabel()
            building_label.setAlignment(
                QtCore.Qt.AlignmentFlag.AlignRight
                | QtCore.Qt.AlignmentFlag.AlignVCenter
            )
            building_layout.addWidget(building_label)
            self.building_labels.append(building_label)

            buildings_layout.addWidget(building_groupbox)

        layout.addWidget(buildings_groupbox, 1, 0, 4, 1)

    def set_building(self, number: int, state: bool) -> None:
        # sourcery skip: assign-if-exp
        """
        Set a building state
        """
        self.send_message(
            "avr/autonomous/building/drop",
            AvrAutonomousBuildingDropPayload(id=number, enabled=state),
        )

        if state:
            text = "Drop Enabled"
            color = "green"
        else:
            text = "Drop Disabled"
            color = "red"

        self.building_labels[number].setText(wrap_text(text, color))

    def set_building_all(self, state: bool) -> None:
        """
        Set all building states at once
        """
        for i in range(self.number_of_buildings):
            self.set_building(i, state)

    def set_autonomous(self, state: bool) -> None:
        """
        Set autonomous mode
        """
        self.send_message(
            "avr/autonomous/enable", AvrAutonomousEnablePayload(enabled=state)
        )

        if state:
            text = "Autonomous Enabled"
            color = "green"
        else:
            text = "Autonomous Disabled"
            color = "red"

        self.autonomous_label.setText(wrap_text(text, color))
