from __future__ import annotations

import contextlib
import json
from typing import Any, Dict, List, Optional, Tuple

from PySide6 import QtCore, QtGui, QtWidgets

from .base import BaseTabWidget


def _get_or_create_child(
    parent: QtWidgets.QTreeWidgetItem, name: str
) -> QtWidgets.QTreeWidgetItem:
    """
    Gets the child QTreeWidgetItem of a QTreeWidgetItem matching the given name.
    If one does not exists, creates and returns a new one.
    """
    # try to find matching item in parent
    for i in range(parent.childCount()):
        child = parent.child(i)
        if child.text(0) == name:
            return child

    # create new item
    return QtWidgets.QTreeWidgetItem(parent, [name])


def _get_parents(item: QtWidgets.QTreeWidgetItem) -> List[QtWidgets.QTreeWidgetItem]:
    """
    Gets a list of parent QTreeWidgetItems of a QTreeWidgetItem.
    The list will be in order from top down, and include the original item.
    """
    # skip if selected item is None
    if item is None:
        return []

    # build a list of the parents
    parents = [item]

    parent = item.parent()
    while parent is not None:
        parents.insert(0, parent)
        item = parent
        parent = item.parent()

    return parents


def _rebuild_topic(item: QtWidgets.QTreeWidgetItem) -> str:
    """
    Rebuild the MQTT topic of a QTreeWidgetItem.
    """
    return "/".join(p.text(0) for p in _get_parents(item))


class ExpandCollapseQTreeWidget(QtWidgets.QTreeWidget):
    # This widget is a subclass of QTreeWidget with a right-click menu
    # to expand/collapse all/children.

    copy_topic: QtCore.SignalInstance = QtCore.Signal(object)  # type: ignore
    copy_payload: QtCore.SignalInstance = QtCore.Signal(object)  # type: ignore
    preload_data: QtCore.SignalInstance = QtCore.Signal(object)  # type: ignore

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        # override the normal right click event. This only works on the TreeWidget
        # itself and not TreeWidgetItems
        menu = QtWidgets.QMenu(self)

        expand_all_action = QtGui.QAction("Expand All", self)
        expand_all_action.triggered.connect(self.expandAll)  # type: ignore
        menu.addAction(expand_all_action)

        collapse_all_action = QtGui.QAction("Collapse All", self)
        collapse_all_action.triggered.connect(self.collapseAll)  # type: ignore
        menu.addAction(collapse_all_action)

        menu.addSeparator()

        # needs to be done before the menu is poped up, otherwise the QEvent will expire
        selected_item = self.itemAt(event.pos())

        expand_children_action = QtGui.QAction("Expand Children", self)
        expand_children_action.triggered.connect(lambda: self.expand_children(selected_item, True))  # type: ignore
        menu.addAction(expand_children_action)

        collapse_children_action = QtGui.QAction("Collapse Children", self)
        collapse_children_action.triggered.connect(lambda: self.expand_children(selected_item, False))  # type: ignore
        menu.addAction(collapse_children_action)

        menu.addSeparator()

        copy_topic_action = QtGui.QAction("Copy Topic", self)
        copy_topic_action.triggered.connect(lambda: self.copy_topic.emit(selected_item))  # type: ignore
        menu.addAction(copy_topic_action)

        copy_payload_action = QtGui.QAction("Copy Payload", self)
        copy_payload_action.triggered.connect(lambda: self.copy_payload.emit(selected_item))  # type: ignore
        menu.addAction(copy_payload_action)

        preload_data_action = QtGui.QAction("Preload Data", self)
        preload_data_action.triggered.connect(lambda: self.preload_data.emit(selected_item))  # type: ignore
        menu.addAction(preload_data_action)

        menu.popup(QtGui.QCursor.pos())

    def expand_children(self, item: QtWidgets.QTreeWidgetItem, expand: bool) -> None:
        """
        Expand/collapse children of a given QTreeWidgetItem
        """
        # https://doc.qt.io/qt-5/qtreeview.html#expandRecursively
        # expandRecursively exists, but not collapseRecursively, so reimplement
        # it ourselves

        # set root item
        item.setExpanded(expand)

        # expand child items
        for i in range(item.childCount()):
            child = item.child(i)
            child.setExpanded(expand)
            self.expand_children(child, expand)


class MQTTDebugWidget(BaseTabWidget):
    # This widget is an effective clone of MQTT Explorer for diagnostic purposes.
    # Displays the latest MQTT message for every topic in a tree view.

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

        self.clipboard = QtWidgets.QApplication.clipboard()

        self.setWindowTitle("MQTT Debugger")

        # secondary data store to maintain dict of topics and the last message recieved
        self.topic_payloads: Dict[str, Any] = {}

        # data structure to hold timers to blink item
        self.topic_timer: Dict[str, QtCore.QTimer] = {}

        # maintain the topic currently displayed in the data view.
        self.connected_topic: Optional[str] = None

        # stop/start state
        self.running = False

    def build(self) -> None:
        """
        Build the layout
        """
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)

        main_layout = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        layout.addWidget(main_layout)

        # viewing widget
        viewer_widget = QtWidgets.QGroupBox("Viewer")
        viewer_layout = QtWidgets.QVBoxLayout()
        viewer_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        viewer_widget.setLayout(viewer_layout)

        self.tree_widget = ExpandCollapseQTreeWidget(self)
        self.tree_widget.setHeaderLabels(["Topic", "# Messages"])
        self.tree_widget.setSortingEnabled(True)
        self.tree_widget.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.tree_widget.setAnimated(True)
        self.tree_widget.setIndentation(10)
        self.tree_widget.itemSelectionChanged.connect(self.connect_topic_to_display)  # type: ignore
        viewer_splitter.addWidget(self.tree_widget)

        self.data_view = QtWidgets.QTextEdit()
        self.data_view.setReadOnly(True)
        self.data_view.setStyleSheet("background-color: rgb(220, 220, 220)")
        viewer_splitter.addWidget(self.data_view)

        viewer_layout.addWidget(viewer_splitter)

        self.running_button = QtWidgets.QPushButton("")
        viewer_layout.addWidget(self.running_button)
        self.running_button.clicked.connect(self.toggle_running)  # type: ignore

        main_layout.addWidget(viewer_widget)

        # sending widget
        sender_widget = QtWidgets.QGroupBox("Sender")
        sender_layout = QtWidgets.QFormLayout()
        sender_widget.setLayout(sender_layout)

        self.topic_line_edit = QtWidgets.QLineEdit()
        sender_layout.addRow(QtWidgets.QLabel("Topic:"), self.topic_line_edit)
        self.payload_text_edit = QtWidgets.QPlainTextEdit()
        sender_layout.addRow(QtWidgets.QLabel("Payload:"), self.payload_text_edit)
        self.send_button = QtWidgets.QPushButton("Send")
        sender_layout.addRow(self.send_button)

        main_layout.addWidget(sender_widget)

        # connections
        self.tree_widget.copy_topic.connect(self.copy_topic)
        self.tree_widget.copy_payload.connect(self.copy_payload)
        self.tree_widget.preload_data.connect(self.preload_data)

        self.send_button.clicked.connect(  # type: ignore
            lambda: self.send_message(
                self.topic_line_edit.text(), self.payload_text_edit.toPlainText()
            )
        )

    def clear(self) -> None:
        """
        Clear data out of the widget.
        """
        self.topic_payloads = {}
        self.tree_widget.clear()

        self.running = True
        self.running_button.setText("Running")

    def toggle_running(self) -> None:
        """
        Toggle the running state.
        """
        self.running = not self.running

        if self.running:
            self.running_button.setText("Running")
        else:
            self.running_button.setText("Paused")

    def process_message(self, topic: str, payload: str) -> None:
        # sourcery skip: assign-if-exp
        """
        Process a new message on a topic.
        """
        # do nothing if paused
        if not self.running:
            return

        # split the topic by parts
        topic_parts = topic.split("/")

        # build the topic tree
        root = self.tree_widget.invisibleRootItem()
        item = root

        for i, part in enumerate(topic_parts):
            # get or create the child
            item = _get_or_create_child(item, part)

            # build the topic name to this part
            partial_topic = "/".join(topic_parts[: i + 1])

            # get the existing count
            count = item.text(1)
            if not count:
                # empty
                count = 0
            else:
                count = int(count)

            # increment the count
            count += 1
            item.setText(1, str(count))

            # blink background to show update for every item in tree
            self.blink_item(item, partial_topic)

        # insert into secondary storage
        self.topic_payloads[topic] = payload
        # self.tree_widget.expandAll()

        # if the topic is already selected, update the data view
        if self.connected_topic == topic:
            self.display_data(topic)

    def connect_topic_to_display(self) -> None:
        """
        When an item is clicked, get the topic for it, and connect it to the data view
        """
        # rebuild the topic name
        topic = _rebuild_topic(self.tree_widget.currentItem())

        # if the selected item isn't a real topic, clear
        if topic not in self.topic_payloads.keys():
            self.connected_topic = None

        # mark the topic as connected
        self.connected_topic = topic
        # force update data
        self.display_data(self.connected_topic)

    def get_payload(self, topic: str) -> str:
        """
        Get the payload for a given topic
        """
        return self.topic_payloads.get(topic, "")

    def display_data(self, topic: str) -> None:
        # sourcery skip: assign-if-exp
        """
        Display data from a topic to the data view
        """
        # get the last known data for the topic
        payload = self.get_payload(topic)

        with contextlib.suppress(json.JSONDecodeError):
            # try to format valid JSON
            payload_json = json.loads(payload)
            payload = json.dumps(payload_json, indent=4)

        # set the data
        self.data_view.setText(payload)

    def set_item_background(
        self, item: QtWidgets.QTreeWidgetItem, color: Tuple[int, int, int]
    ) -> None:
        """
        Set the background color for an item.
        """
        # a runtime error is thrown if the item is already deleted (disconnected)
        with contextlib.suppress(RuntimeError):
            item.setBackground(0, QtGui.QColor(*color))

    def blink_item(self, item: QtWidgets.QTreeWidgetItem, topic: str) -> None:
        """
        Blink the background color of an item
        """
        if topic in self.topic_timer and self.topic_timer[topic].isActive():
            # if a timer already exists to clear the background, delete it
            timer = self.topic_timer[topic]
            timer.stop()
            timer.deleteLater()
        else:
            # otherwise, set background to grey
            self.set_item_background(item, (220, 220, 220))

        # start new timer to clear background
        timer = QtCore.QTimer()
        timer.timeout.connect(lambda: self.set_item_background(item, (255, 255, 255)))  # type: ignore
        timer.setSingleShot(True)
        timer.start(100)

        self.topic_timer[topic] = timer

    def copy_topic(self, item: QtWidgets.QTreeWidgetItem) -> None:
        """
        Copy the topic of a given QTreeWidgetItem to the clipboard
        """
        topic = _rebuild_topic(item)

        self.clipboard.clear(mode=self.clipboard.Clipboard)
        self.clipboard.setText(topic, mode=self.clipboard.Clipboard)

    def copy_payload(self, item: QtWidgets.QTreeWidgetItem) -> None:
        """
        Copy the payload of a given QTreeWidgetItem to the clipboard
        """
        topic = _rebuild_topic(item)
        payload = self.get_payload(topic)

        self.clipboard.clear(mode=self.clipboard.Clipboard)
        self.clipboard.setText(payload, mode=self.clipboard.Clipboard)

    def preload_data(self, item: QtWidgets.QTreeWidgetItem) -> None:
        """
        Preload data into the sender from a selected QTreeWidgetItem.
        """
        topic = _rebuild_topic(item)
        payload = self.get_payload(topic)

        self.topic_line_edit.setText(topic)
        self.payload_text_edit.setPlainText(payload)
