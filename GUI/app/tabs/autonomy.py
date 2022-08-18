from __future__ import annotations

from bell.avr.mqtt.payloads import AvrAutonomousPayload, AvrGameBuildingStatePayload
from PySide6 import QtWidgets

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

        layout.addWidget(autonomous_groupbox, 0, 0, 1, 1)

        # ==========================
        # Buildings
        buildings_groupbox = QtWidgets.QGroupBox("All Buildings")
        buildings_layout = QtWidgets.QVBoxLayout()
        buildings_groupbox.setLayout(buildings_layout)

        building_all_layout = QtWidgets.QHBoxLayout()

        building_all_open_button = QtWidgets.QPushButton("All on fire")
        building_all_open_button.clicked.connect(lambda: self.set_building_all(True))  # type: ignore
        building_all_layout.addWidget(building_all_open_button)

        building_all_close_button = QtWidgets.QPushButton("All NOT on fire")
        building_all_close_button.clicked.connect(lambda: self.set_building_all(False))  # type: ignore
        building_all_layout.addWidget(building_all_close_button)

        buildings_layout.addLayout(building_all_layout)

        building_1_groupbox = QtWidgets.QGroupBox("Building 1")
        building_1_layout = QtWidgets.QHBoxLayout()
        building_1_groupbox.setLayout(building_1_layout)

        building_1_open_button = QtWidgets.QPushButton("On fire")
        building_1_open_button.clicked.connect(lambda: self.set_building(0, True))  # type: ignore
        building_1_layout.addWidget(building_1_open_button)

        building_1_close_button = QtWidgets.QPushButton("NOT on fire")
        building_1_close_button.clicked.connect(lambda: self.set_building(0, False))  # type: ignore
        building_1_layout.addWidget(building_1_close_button)

        buildings_layout.addWidget(building_1_groupbox)

        building_2_groupbox = QtWidgets.QGroupBox("Building 2")
        building_2_layout = QtWidgets.QHBoxLayout()
        building_2_groupbox.setLayout(building_2_layout)

        building_2_open_button = QtWidgets.QPushButton("On fire")
        building_2_open_button.clicked.connect(lambda: self.set_building(1, True))  # type: ignore
        building_2_layout.addWidget(building_2_open_button)

        building_2_close_button = QtWidgets.QPushButton("NOT on fire")
        building_2_close_button.clicked.connect(lambda: self.set_building(1, False))  # type: ignore
        building_2_layout.addWidget(building_2_close_button)

        buildings_layout.addWidget(building_2_groupbox)

        building_3_groupbox = QtWidgets.QGroupBox("Building 3")
        building_3_layout = QtWidgets.QHBoxLayout()
        building_3_groupbox.setLayout(building_3_layout)

        building_3_open_button = QtWidgets.QPushButton("On fire")
        building_3_open_button.clicked.connect(lambda: self.set_building(2, True))  # type: ignore
        building_3_layout.addWidget(building_3_open_button)

        building_3_close_button = QtWidgets.QPushButton("NOT on fire")
        building_3_close_button.clicked.connect(lambda: self.set_building(2, False))  # type: ignore
        building_3_layout.addWidget(building_3_close_button)

        buildings_layout.addWidget(building_3_groupbox)

        building_4_groupbox = QtWidgets.QGroupBox("Building 4")
        building_4_layout = QtWidgets.QHBoxLayout()
        building_4_groupbox.setLayout(building_4_layout)

        building_4_open_button = QtWidgets.QPushButton("On fire")
        building_4_open_button.clicked.connect(lambda: self.set_building(3, True))  # type: ignore
        building_4_layout.addWidget(building_4_open_button)

        building_4_close_button = QtWidgets.QPushButton("NOT on fire")
        building_4_close_button.clicked.connect(lambda: self.set_building(3, False))  # type: ignore
        building_4_layout.addWidget(building_4_close_button)

        buildings_layout.addWidget(building_4_groupbox)

        layout.addWidget(buildings_groupbox, 1, 0, 4, 1)

    def set_building(self, number: int, on_fire: bool) -> None:
        """
        Set a building state
        """
        self.send_message(
            "avr/game/building/state",
            AvrGameBuildingStatePayload(id=number, on_fire=on_fire),
        )

    def set_building_all(self, on_fire: bool) -> None:
        """
        Set all building states at once
        """
        for i in range(4):
            self.set_building(i, on_fire)

    def set_autonomous(self, state: bool) -> None:
        """
        Set autonomous mode
        """
        self.send_message("avr/autonomous", AvrAutonomousPayload(enable=state))
