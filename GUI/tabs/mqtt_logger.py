from __future__ import annotations
from enum import unique

import os
from datetime import datetime
from tkinter import W
from typing import Any, Dict

from PySide6 import QtCore, QtWidgets

from .base import BaseTabWidget

import csv

GUI_DIR = os.path.join(os.path.dirname(__file__), "..")

class MQTTLoggerWidget(BaseTabWidget):
    # This widget is a logger of MQTT messages
    # Logs the messages from MQTT to a csv that and can be used for debugging or data analysis.

    send_message: QtCore.SignalInstance = QtCore.Signal(str, str)  # type: ignore

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

        self.clipboard = QtWidgets.QApplication.clipboard()

        self.setWindowTitle("MQTT Logger")

        # secondary data store to maintain dict of topics and the last message recieved
        self.topic_payloads: Dict[str, Any] = {}

        # Access the Filesystem
        self.filesystem = QtWidgets.QFileSystemModel()
        self.filesystem.setRootPath(GUI_DIR)

        # stop/start state
        self.recording = False

    def build(self) -> None:
        """
        Build the layout
        """
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)

        main_layout = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        layout.addWidget(main_layout)

        # File viewing widget
        file_viewer_widget = QtWidgets.QGroupBox("Log Explorer")
        file_viewer_layout = QtWidgets.QVBoxLayout()
        file_viewer_widget.setLayout(file_viewer_layout)

        self.file_tree = QtWidgets.QTreeView()
        self.file_tree.setModel(self.filesystem)
        self.file_tree.setRootIndex(self.filesystem.index("logs"))
        self.file_tree.setSortingEnabled(True)
        self.file_tree.sortByColumn(0, QtCore.Qt.DescendingOrder)
        file_viewer_layout.addWidget(self.file_tree)

        self.recording_button = QtWidgets.QPushButton("Start Recording")
        file_viewer_layout.addWidget(self.recording_button)
        self.recording_button.clicked.connect(self.toggle_recording)  # type: ignore

        main_layout.addWidget(file_viewer_widget)

    def clear(self) -> None:
        """
        Clear data out of the widget.
        """
        self.topic_payloads = {}

        self.recording = False
        self.recording_button.setText("Record")

    def toggle_recording(self) -> None:
        """
        Toggle the running state.
        """
        self.recording = not self.recording

        unique_log = datetime.now().strftime("%Y-%m-%d_%H%M-%S")
        file_name = os.path.join(GUI_DIR, "logs",
            "MQTTlog_{}.csv".format(unique_log)
            )
        print(file_name)
        if self.recording:
            # open new log file
            with open(file_name,mode='w') as log_file:
                self.log_writer = csv.writer(log_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                self.log_writer.writerow(["TimeDate","Topic","Message"])
            self.recording_button.setText("Stop Recording")
        else:
            self.recording_button.setText("Record")

    def process_message(self, topic: str, payload: str) -> None:
        # sourcery skip: assign-if-exp
        """
        Process a new message on a topic.
        """
        # do nothing if paused
        if not self.recording:
            return

        # insert into secondary storage
        self.topic_payloads[topic] = payload

        # Write time_stamp, topic, payload to log file
        time_stamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        self.log_writer.writerow([time_stamp, topic, payload])