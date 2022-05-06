from __future__ import annotations

import csv
import datetime
import os
from io import TextIOWrapper
from typing import Optional

from lib.config import config
from PySide6 import QtCore, QtWidgets

from .base import BaseTabWidget


class MQTTLoggerWidget(BaseTabWidget):
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

        self.setWindowTitle("MQTT Logger")

        # Access the Filesystem
        os.makedirs(config.log_file_directory, exist_ok=True)

        # setting this environment variable will allow the file size to be
        # automatically updated after the file handle is closed
        os.environ["QT_FILESYSTEMMODEL_WATCH_FILES"] = "True"

        self.filesystem_model = QtWidgets.QFileSystemModel()
        self.filesystem_model.setRootPath(config.log_file_directory)

        # stop/start state
        self.recording = False

        # active file handles
        self.file_handle: Optional[TextIOWrapper] = None
        self.csv_writer = None

    def build(self) -> None:
        """
        Build the layout
        """
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)

        self.directory_label = QtWidgets.QLabel(config.log_file_directory)
        layout.addWidget(self.directory_label)

        self.file_tree = QtWidgets.QTreeView()
        self.file_tree.setModel(self.filesystem_model)
        self.file_tree.setRootIndex(self.filesystem_model.index(config.log_file_directory))
        self.file_tree.setSortingEnabled(True)
        self.file_tree.sortByColumn(0, QtCore.Qt.DescendingOrder)
        layout.addWidget(self.file_tree)

        self.recording_button = QtWidgets.QPushButton("Start Recording")
        layout.addWidget(self.recording_button)

        self.recording_button.clicked.connect(self.toggle_recording)  # type: ignore

    def clear(self) -> None:
        """
        Clear data out of the widget.
        """
        # reset recording state
        self.recording = False
        self.recording_button.setText("Record")

        # close file handle
        if self.file_handle is not None:
            self.file_handle.close()

    def toggle_recording(self) -> None:
        """
        Toggle the running state.
        """
        self.recording = not self.recording

        if self.recording:
            # generate new file name
            filename = os.path.join(
                config.log_file_directory,
                f"MQTTLog_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv",
            )

            # open file
            self.file_handle = open(filename, "w", newline="")

            # create CSV writer
            self.csv_writer = csv.writer(self.file_handle)
            self.csv_writer.writerow(["Timestamp", "Topic", "Message"])

            # set button text
            self.recording_button.setText("Stop Recording")

        else:
            # close file handle
            if self.file_handle is not None:
                self.file_handle.close()

            # set button text
            self.recording_button.setText("Record")

    def process_message(self, topic: str, payload: str) -> None:
        """
        Process a new message on a topic.
        """
        # do nothing if paused
        if not self.recording:
            return

        # Write time_stamp, topic, payload to log file
        if self.csv_writer is not None:
            self.csv_writer.writerow(
                [datetime.datetime.now().isoformat(), topic, payload]
            )
