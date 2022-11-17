from __future__ import annotations

import contextlib
import json
import functools
from typing import Any, Dict, List, Optional, Tuple, Union

from bell.avr.mqtt.constants import MQTTTopicPayload, MQTTTopics
from PySide6 import QtCore, QtGui, QtWidgets

from .base import BaseTabWidget


class MQTTQTreeWidgetItem(QtWidgets.QTreeWidgetItem):

    @functools.lru_cache()
    def topic(self) -> str:
        """
        Rebuild the MQTT topic of a QTreeWidgetItem.
        """
        # build a list of the parents
        parents: List[QtWidgets.QTreeWidgetItem] = [self]

        parent = self.parent()
        while parent is not None:
            parents.insert(0, parent)
            item = parent
            parent = item.parent()

        # rejoin everything by slashes
        return "/".join(p.text(0) for p in parents)

class ExpandCollapseQTreeWidget(QtWidgets.QTreeWidget):
    # This widget is a subclass of QTreeWidget with a right-click menu
    # to expand/collapse all/children.

    copy_topic: QtCore.SignalInstance = QtCore.Signal(object)  # type: ignore
    copy_payload: QtCore.SignalInstance = QtCore.Signal(object)  # type: ignore
    preload_data: QtCore.SignalInstance = QtCore.Signal(object)  # type: ignore

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

    def currentItem(self) -> MQTTQTreeWidgetItem:
        return super().currentItem() # type: ignore

    def all_items(self, parent: Optional[Union[MQTTQTreeWidgetItem, ExpandCollapseQTreeWidget]] = None) -> List[MQTTQTreeWidgetItem]:
        if parent is None:
            parent  = self

        items = []
        for i in parent.childCount():
            item = parent.child(i)
            items.append(item)
            items.extend(self.all_items(item))

        return items

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

        main_layout = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        layout.addWidget(main_layout)

        # viewing widget
        viewer_widget = QtWidgets.QGroupBox("Viewer")
        viewer_layout = QtWidgets.QVBoxLayout()
        viewer_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        viewer_widget.setLayout(viewer_layout)

        topic_filter_layout = QtWidgets.QFormLayout()
        self.topic_filter_line_edit = QtWidgets.QLineEdit()
        topic_filter_layout.addRow(QtWidgets.QLabel("Filter:"), self.topic_filter_line_edit)
        viewer_layout.addLayout(topic_filter_layout)

        self.tree_widget = ExpandCollapseQTreeWidget(self)
        self.tree_widget.setHeaderLabels(["Topic", "# Messages"])
        self.tree_widget.setSortingEnabled(True)
        self.tree_widget.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)
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

        self.topic_combo_box = QtWidgets.QComboBox()
        self.topic_combo_box.addItems(list(MQTTTopics))
        # allow custom text, but don't modify the original data set
        self.topic_combo_box.setEditable(True)
        self.topic_combo_box.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        # change completer to have a popup
        self.topic_combo_box.completer().setCompletionMode(
            QtWidgets.QCompleter.CompletionMode.PopupCompletion
        )
        self.topic_combo_box.setCurrentText("")
        sender_layout.addRow(QtWidgets.QLabel("Topic:"), self.topic_combo_box)

        self.payload_text_edit_interaction = False
        self.payload_text_edit = QtWidgets.QPlainTextEdit()
        sender_layout.addRow(QtWidgets.QLabel("Payload:"), self.payload_text_edit)

        self.send_button = QtWidgets.QPushButton("Send")
        sender_layout.addRow(self.send_button)

        main_layout.addWidget(sender_widget)

        # connections
        self.tree_widget.copy_topic.connect(self.copy_topic)
        self.tree_widget.copy_payload.connect(self.copy_payload)
        self.tree_widget.preload_data.connect(self.preload_data)

        self.topic_combo_box.textActivated.connect(self.topic_selected)  # type: ignore
        self.payload_text_edit.textChanged.connect(self.reset_payload_text_edit_interaction)  # type: ignore
        self.send_button.clicked.connect(  # type: ignore
            lambda: self.send_message(
                self.topic_combo_box.currentText(), self.payload_text_edit.toPlainText()
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

    def _get_or_create_child(
        self, parent: QtWidgets.QTreeWidgetItem, name: str
    ) -> MQTTQTreeWidgetItem:
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
        return MQTTQTreeWidgetItem(parent, [name])


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
            item = self._get_or_create_child(item, part)

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
        topic = self.tree_widget.currentItem().topic()

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

    def copy_topic(self, item: MQTTQTreeWidgetItem) -> None:
        """
        Copy the topic of a given QTreeWidgetItem to the clipboard
        """
        self.clipboard.clear(mode=self.clipboard.Mode.Clipboard)
        self.clipboard.setText(item.topic(), mode=self.clipboard.Mode.Clipboard)

    def copy_payload(self, item: MQTTQTreeWidgetItem) -> None:
        """
        Copy the payload of a given QTreeWidgetItem to the clipboard
        """
        payload = self.get_payload(item.topic())

        self.clipboard.clear(mode=self.clipboard.Mode.Clipboard)
        self.clipboard.setText(payload, mode=self.clipboard.Mode.Clipboard)

    def preload_data(self, item: MQTTQTreeWidgetItem) -> None:
        """
        Preload data into the sender from a selected QTreeWidgetItem.
        """
        payload = self.get_payload(item.topic())

        self.topic_combo_box.setCurrentText(item.topic())
        self.payload_text_edit.setPlainText(payload)

    def reset_payload_text_edit_interaction(self) -> None:
        """
        When the user changes text in the text edit, consider it to have been
        interacted with. Only exception is if it has been blanked.
        """
        # if there is already text, consider the user to have interacted
        # if there is no text, reset interaction tracker
        self.payload_text_edit_interaction = self.payload_text_edit.toPlainText() != ""

    def topic_selected(self, text: str) -> None:
        """
        When a topic is selected from QCompletor, create an empty JSON structure
        to help the user.
        """
        # skip if the user has edited text since we last set it
        if self.payload_text_edit_interaction:
            return

        payload = MQTTTopicPayload[self.topic_combo_box.currentText()]
        starter_data = {key: None for key in payload.__required_keys__}

        self.payload_text_edit.blockSignals(True)
        self.payload_text_edit.setPlainText(json.dumps(starter_data, indent=4))
        self.payload_text_edit.blockSignals(False)

        self.payload_text_edit_interaction = False

    def filter_topic(self) -> None:
        """
        Filter items in the QTreeWidget based on the given filter.
        """
