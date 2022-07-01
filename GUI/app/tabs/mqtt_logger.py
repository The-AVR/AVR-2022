from __future__ import annotations

import csv
import datetime
import os
from io import TextIOWrapper
from typing import Optional

from app.lib.config import config
from app.tabs.base import BaseTabWidget
from PySide6 import QtCore, QtGui, QtWidgets


class LogFileViewWidget(QtWidgets.QTreeView):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # setting this environment variable will allow the file size to be
        # automatically updated after the file handle is closed
        os.environ["QT_FILESYSTEMMODEL_WATCH_FILES"] = "True"

        self.filesystem_model = QtWidgets.QFileSystemModel()
        self.filesystem_model.setRootPath(config.log_file_directory)
        self.filesystem_model.setNameFilters(["*.csv"])
        self.filesystem_model.setNameFilterDisables(False)

        self.setModel(self.filesystem_model)
        self.setRootIndex(self.filesystem_model.index(config.log_file_directory))

        # dont allow nested folders to be expanded
        self.setItemsExpandable(False)

        self.setSortingEnabled(True)
        self.sortByColumn(0, QtCore.Qt.DescendingOrder)

        # open files on double click
        self.doubleClicked.connect(lambda index: os.startfile(self.filesystem_model.filePath(index)))  # type: ignore

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        # override the normal right click event.
        menu = QtWidgets.QMenu(self)

        # needs to be done before the menu is poped up, otherwise the QEvent will expire
        selected_index = self.indexAt(event.pos())

        # check if anything is selected
        if selected_index.row() == -1:
            return

        # add delete action
        delete_file_action = QtGui.QAction("Delete", self)
        delete_file_action.triggered.connect(lambda: self.filesystem_model.remove(selected_index))  # type: ignore
        menu.addAction(delete_file_action)

        menu.popup(QtGui.QCursor.pos())


class MQTTLoggerWidget(BaseTabWidget):
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

        self.setWindowTitle("MQTT Logger")

        # Access the Filesystem
        os.makedirs(config.log_file_directory, exist_ok=True)

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

        self.file_tree = LogFileViewWidget(self)
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
            self.csv_writer.writerow(["Timestamp", "Topic", "Payload"])

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
