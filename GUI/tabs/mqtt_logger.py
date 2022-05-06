from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict

from PySide6 import QtCore, QtWidgets

from .base import BaseTabWidget

GUI_DIR = os.path.dirname(os.path.dirname(__file__))


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
        self.filesystem.setRootPath(QtCore.QDir(path=GUI_DIR).absolutePath())

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
        self.file_tree.setRootIndex(self.filesystem.index("{}/logs/".format(GUI_DIR)))
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

        file_name = "{}/logs/MQTTlog_{}.csv".format(
            GUI_DIR, datetime.now().strftime("%Y-%m-%d_%H%M-%S")
        )

        if self.recording:
            # open new log file
            log_file = QtCore.QFile(file_name)
            log_file.open(QtCore.QFile.WriteOnly)
            self.log = QtCore.QTextStream(log_file)
            self.log << "TimeDate, Topic, Message\n"

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
        self.log << "{}, {}, {}\n".format(time_stamp, topic, payload)
