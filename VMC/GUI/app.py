from __future__ import annotations

import json
import base64
import os
import sys
import time
import threading
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import paho.mqtt.client as mqtt
from PySide6 import QtCore, QtGui, QtWidgets
from qt_icon import IMG_DIR, set_icon

try:
    from thermalview import VRC_ThermalView # type: ignore
except ImportError:
    from .thermalview import VRC_ThermalView


class MQTTClient(QtCore.QObject):
    # This class MUST inherit from QObject in order for the signals to work

    # This class exists seperately from the main application window, as the MQTT client
    # runs in a seperate thread. The callbacks from the MQTT client run in the same
    # thread as the client and thus those cannot update the GUI, as only the
    # thread that started the GUI is allowed to update it. Thus, set up the
    # MQTT client in a seperate class with signals that are emitted and connected to
    # so the data gets passed back to the GUI thread.

    # Once the Signal objects are created, they transform into SignalInstance objects
    connection_status: QtCore.SignalInstance = QtCore.Signal(bool)  # type: ignore
    message: QtCore.SignalInstance = QtCore.Signal(str, str)  # type: ignore
    disconnect: QtCore.SignalInstance = QtCore.Signal()  # type: ignore

    def __init__(self) -> None:
        super().__init__()

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        rc: int,
        properties: mqtt.Properties = None,
    ) -> None:
        """
        Callback when the MQTT client connects
        """
        # subscribe to all topics
        client.subscribe("#")

    def on_message(
        self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage
    ) -> None:
        """
        Callback for every MQTT message
        """
        if msg.topic=="vrc/pcm/thermal_reading":
            self.message.emit(msg.topic, msg.payload)
            print("emitting message")
        else:
            self.message.emit(msg.topic, msg.payload.decode("utf-8"))

    def on_disconnect(
        self,
        client: mqtt.Client,
        userdata: Any,
        rc: int,
    ) -> None:
        """
        Callback when the MQTT client disconnects
        """
        self.disconnect.emit()

    def login(self, host: str) -> None:
        """
        Connect the MQTT client to the server. This method cannot be named "connect"
        as this conflicts with the connect methods of the Signals
        """
        port = 18830

        try:
            # try to connect to MQTT server
            self.client.connect(host=host, port=port, keepalive=60)
            self.client.loop_start()
        except:
            # display error on failed connection
            self.connection_status.emit(False)

        # show message for successful connection
        self.connection_status.emit(True)

    def publish(self, *args, **kwargs) -> None:
        """
        Publish an MQTT message. Proxy function to the underlying client
        """
        self.client.publish(*args, **kwargs)




class MainWidget(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()

        set_icon(self)

        self.mqtt_client = MQTTClient()

        self.control_widget = ControlWidget(self)
        self.control_widget.build()
        self.control_widget.show()

        self.mqtt_view_widget = MQTTViewWidget(self)
        self.mqtt_view_widget.build()
        self.mqtt_view_widget.show()

        self.thermal_view_widget = ThermalViewWidget(self, self.control_widget)

        self.connect_mqtt()

    def connect_mqtt(self) -> None:
        """
        Perform the MQTT connection flow with the user.
        """
        settings = {}
        settings_file = os.path.join(os.path.dirname(__file__), "settings.json")

        mqtt_host = ""

        # try to load last saved settings from file
        if os.path.exists(settings_file):
            try:
                with open(settings_file, "r") as fp:
                    settings = json.load(fp)
                    mqtt_host = settings["mqtt_host"]
            except:
                # if file is corrupt, delete it
                os.remove(settings_file)

        # ask for input
        mqtt_host = QtWidgets.QInputDialog.getText(  # type: ignore
            self, "MQTT Host", "Enter MQTT Host:", text=mqtt_host
        )[0]

        # if no selection made
        if mqtt_host == "":
            sys.exit(0)

        def connection(success: bool) -> None:
            if success:
                QtWidgets.QMessageBox.information(
                    self, "MQTT Status", "Connected to MQTT server."
                )

            else:
                QtWidgets.QMessageBox.critical(
                    self, "MQTT Error", "Could not connect to MQTT server."
                )
                sys.exit(1)

        self.mqtt_client.connection_status.connect(connection)
        self.mqtt_client.disconnect.connect(lambda: connection(False))
        self.mqtt_client.login(mqtt_host)

        # save settings
        settings["mqtt_host"] = mqtt_host
        with open(settings_file, "w") as fp:
            json.dump(settings, fp)

        # connect message signals
        self.mqtt_client.message.connect(self.mqtt_view_widget.process_message)
        self.mqtt_client.message.connect(self.thermal_view_widget.process_message)
        self.mqtt_client.message.connect(self.control_widget.process_message)


class StatusLabel(QtWidgets.QWidget):
    # Combination of 2 QLabels to add a status icon
    def __init__(self, text: str):
        super().__init__()

        # create a horizontal layout
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # create a label for the icon
        self.icon = QtWidgets.QLabel()
        self.icon.setFixedWidth(20)
        layout.addWidget(self.icon)
        self.set_health(False)

        # add text label
        layout.addWidget(QtWidgets.QLabel(text))

    def set_health(self, healthy: bool) -> None:
        """
        Set the health state of the status label
        """
        if healthy:
            self.icon.setPixmap(QtGui.QPixmap(os.path.join(IMG_DIR, "green.png")))
        else:
            self.icon.setPixmap(QtGui.QPixmap(os.path.join(IMG_DIR, "red.png")))

class Direction(Enum):
    Left = 0
    Right = 1
    Up = 2
    Down = 3

class Joystick(QtWidgets.QWidget):
    def __init__(self, mqtt_client: MQTTClient, parent=None):
        super(Joystick, self).__init__(parent)
        self.mqtt_client = mqtt_client
        self.setMinimumSize(100, 100)
        self.movingOffset = QtCore.QPointF(0, 0)
        self.grabCenter = False
        self.__maxDistance = 50
        self.current_y = 0
        self.current_x = 0
        self.lasttime = 0
        self.servoxmin = 10
        self.servoymin = 10
        self.servoxmax = 99
        self.servoymax = 99


    def map_value(self,x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def move_gimbal(self, x_servo_percent, y_servo_percent):

        payload = {"servo": 2, "percent": x_servo_percent}
        self.mqtt_client.publish("vrc/pcm/set_servo_pct", payload=json.dumps(payload))
        payload = {"servo": 3, "percent": y_servo_percent}
        self.mqtt_client.publish("vrc/pcm/set_servo_pct", payload=json.dumps(payload))

    def update_servos(self):
        ms = int(round(time.time() * 1000))
        timesince = ms - self.lasttime
        if (timesince<50):
            return
        self.lasttime = ms
        y_reversed = 100 - self.current_y 
        
        x_servo_percent = round(self.map_value(self.current_x, 0, 100, 10, 99) )
        y_servo_percent = round(self.map_value(y_reversed, 0, 100, 10, 99) )


        if (x_servo_percent<self.servoxmin): return
        if (y_servo_percent<self.servoymin): return
        if (x_servo_percent>self.servoxmax): return
        if (y_servo_percent>self.servoymax): return

        self.move_gimbal(x_servo_percent, y_servo_percent)
    


    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        bounds = QtCore.QRectF(-self.__maxDistance, -self.__maxDistance, self.__maxDistance * 2, self.__maxDistance * 2).translated(self._center())
        #painter.drawEllipse(bounds)
        painter.drawRect(bounds)
        painter.setBrush(QtCore.Qt.black)
        painter.drawEllipse(self._centerEllipse())

    def _centerEllipse(self):
        if self.grabCenter:
            return QtCore.QRectF(-20, -20, 40, 40).translated(self.movingOffset)
        return QtCore.QRectF(-20, -20, 40, 40).translated(self._center())

    def _center(self):
        return QtCore.QPointF(self.width()/2, self.height()/2)


    def _boundJoystick(self, point):

        if (point.x()>(self._center().x() + self.__maxDistance)):
            point.setX(self._center().x() + self.__maxDistance)
        elif (point.x()<(self._center().x() - self.__maxDistance)):
            point.setX(self._center().x() - self.__maxDistance)

        if (point.y()>(self._center().y() + self.__maxDistance)):
            point.setY(self._center().y() + self.__maxDistance)
        elif (point.y()<(self._center().y() - self.__maxDistance)):
            point.setY(self._center().y() - self.__maxDistance)
        return point

    def joystickDirection(self):
        if not self.grabCenter:
            return 0
        normVector = QtCore.QLineF(self._center(), self.movingOffset)
        currentDistance = normVector.length()
        angle = normVector.angle()

        distance = min(currentDistance / self.__maxDistance, 1.0)
        if 45 <= angle < 135:
            return (Direction.Up, distance)
        elif 135 <= angle < 225:
            return (Direction.Left, distance)
        elif 225 <= angle < 315:
            return (Direction.Down, distance)
        return (Direction.Right, distance)


    def mousePressEvent(self, ev):
        self.grabCenter = self._centerEllipse().contains(ev.pos())
        return super().mousePressEvent(ev)

    def mouseReleaseEvent(self, event):
       # self.grabCenter = False
       # self.movingOffset = QtCore.QPointF(0, 0)
        self.update()

    def mouseMoveEvent(self, event):
        if self.grabCenter:
            self.movingOffset = self._boundJoystick(event.pos())
            self.update()
        #print(self.joystickDirection())
        self.current_x = self.movingOffset.x() - self._center().x() + self.__maxDistance
        self.current_y = self.movingOffset.y() - self._center().y() + self.__maxDistance
        self.update_servos()
        
class ControlWidget(QtWidgets.QWidget):
    # This is the primary control widget for the drone. This allows the user
    # to set LED color, open/close servos etc.

    def __init__(self, parent: MainWidget) -> None:
        self.parent_ = parent
        super().__init__()

        self.setWindowTitle("Bell VRC Control")
        set_icon(self)

    def  laser_on(self):
        payload = {}
        self.publish_message("vrc/pcm/set_laser_on", {})

    def  laser_off(self):
        payload = {}
        self.publish_message("vrc/pcm/set_laser_off", {})



    def  request_thermal_reading(self):
        self.publish_message(  
                    "vrc/thermal/request_thermal_reading",
                    "{}",
                    retain=False,
                    qos=0,
             )


    def build(self) -> None:
        """
        Build the GUI layout
        """
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        # ==========================
        # LEDs
        led_groupbox = QtWidgets.QGroupBox("LEDs")
        led_layout = QtWidgets.QVBoxLayout()
        led_groupbox.setLayout(led_layout)

        red_led_button = QtWidgets.QPushButton("Red")
        red_led_button.setStyleSheet("background-color: red")
        red_led_button.clicked.connect(lambda: self.set_led((255, 255, 0, 0)))  # type: ignore
        led_layout.addWidget(red_led_button)

        green_led_button = QtWidgets.QPushButton("Green")
        green_led_button.setStyleSheet("background-color: green")
        green_led_button.clicked.connect(lambda: self.set_led((255, 0, 255, 0)))  # type: ignore
        led_layout.addWidget(green_led_button)

        blue_led_button = QtWidgets.QPushButton("Blue")
        blue_led_button.setStyleSheet("background-color: blue; color: white")
        blue_led_button.clicked.connect(lambda: self.set_led((255, 0, 0, 255)))  # type: ignore
        led_layout.addWidget(blue_led_button)

        clear_led_button = QtWidgets.QPushButton("Clear")
        clear_led_button.setStyleSheet("background-color: white")
        clear_led_button.clicked.connect(lambda: self.set_led((0, 0, 0, 0)))  # type: ignore
        led_layout.addWidget(clear_led_button)

        layout.addWidget(led_groupbox, 0, 0, 3, 1)

        # ==========================
        # Servos
        servos_groupbox = QtWidgets.QGroupBox("Servos")
        servos_layout = QtWidgets.QVBoxLayout()
        servos_groupbox.setLayout(servos_layout)

        servo_all_layout = QtWidgets.QHBoxLayout()

        servo_all_open_button = QtWidgets.QPushButton("Open all")
        servo_all_open_button.clicked.connect(lambda: self.set_servo_all("open"))  # type: ignore
        servo_all_layout.addWidget(servo_all_open_button)

        servo_all_close_button = QtWidgets.QPushButton("Close all")
        servo_all_close_button.clicked.connect(lambda: self.set_servo_all("close"))  # type: ignore
        servo_all_layout.addWidget(servo_all_close_button)

        servos_layout.addLayout(servo_all_layout)

        servo_1_groupbox = QtWidgets.QGroupBox("Servo 1")
        servo_1_layout = QtWidgets.QHBoxLayout()
        servo_1_groupbox.setLayout(servo_1_layout)

        servo_1_open_button = QtWidgets.QPushButton("Open")
        servo_1_open_button.clicked.connect(lambda: self.set_servo(0, "open"))  # type: ignore
        servo_1_layout.addWidget(servo_1_open_button)

        servo_1_close_button = QtWidgets.QPushButton("Close")
        servo_1_close_button.clicked.connect(lambda: self.set_servo(0, "close"))  # type: ignore
        servo_1_layout.addWidget(servo_1_close_button)

        servos_layout.addWidget(servo_1_groupbox)

        servo_2_groupbox = QtWidgets.QGroupBox("Servo 2")
        servo_2_layout = QtWidgets.QHBoxLayout()
        servo_2_groupbox.setLayout(servo_2_layout)

        servo_2_open_button = QtWidgets.QPushButton("Open")
        servo_2_open_button.clicked.connect(lambda: self.set_servo(1, "open"))  # type: ignore
        servo_2_layout.addWidget(servo_2_open_button)

        servo_2_close_button = QtWidgets.QPushButton("Close")
        servo_2_close_button.clicked.connect(lambda: self.set_servo(1, "close"))  # type: ignore
        servo_2_layout.addWidget(servo_2_close_button)

        servos_layout.addWidget(servo_2_groupbox)

        servo_3_groupbox = QtWidgets.QGroupBox("Servo 3")
        servo_3_layout = QtWidgets.QHBoxLayout()
        servo_3_groupbox.setLayout(servo_3_layout)

        servo_3_open_button = QtWidgets.QPushButton("Open")
        servo_3_open_button.clicked.connect(lambda: self.set_servo(2, "open"))  # type: ignore
        servo_3_layout.addWidget(servo_3_open_button)

        servo_3_close_button = QtWidgets.QPushButton("Close")
        servo_3_close_button.clicked.connect(lambda: self.set_servo(2, "close"))  # type: ignore
        servo_3_layout.addWidget(servo_3_close_button)

        servos_layout.addWidget(servo_3_groupbox)

        servo_4_groupbox = QtWidgets.QGroupBox("Servo 4")
        servo_4_layout = QtWidgets.QHBoxLayout()
        servo_4_groupbox.setLayout(servo_4_layout)

        servo_4_open_button = QtWidgets.QPushButton("Open")
        servo_4_open_button.clicked.connect(lambda: self.set_servo(3, "open"))  # type: ignore
        servo_4_layout.addWidget(servo_4_open_button)

        servo_4_close_button = QtWidgets.QPushButton("Close")
        servo_4_close_button.clicked.connect(lambda: self.set_servo(3, "close"))  # type: ignore
        servo_4_layout.addWidget(servo_4_close_button)

        servos_layout.addWidget(servo_4_groupbox)

        layout.addWidget(servos_groupbox, 0, 1, 3, 3)

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

        layout.addWidget(autonomous_groupbox, 3, 0, 1, 3)

        # ==========================
        # PCC Reset
        reset_groupbox = QtWidgets.QGroupBox("Reset")
        reset_layout = QtWidgets.QVBoxLayout()
        reset_groupbox.setLayout(reset_layout)

        reset_button = QtWidgets.QPushButton("Reset Peripheals")
        reset_button.setStyleSheet("background-color: yellow")
        reset_button.clicked.connect(lambda: self.publish_message("vrc/pcm/reset", {}))  # type: ignore
        reset_layout.addWidget(reset_button)

        layout.addWidget(reset_groupbox, 3, 3, 1, 1)

        # ==========================
        # Status
        status_groupbox = QtWidgets.QGroupBox("Status")
        status_layout = QtWidgets.QHBoxLayout()
        status_groupbox.setLayout(status_layout)

        # data structure to hold the topic prefixes and the corresponding widget
        self.topic_status_map: Dict[str, StatusLabel] = {}
        # data structure to hold timers to reset services to unhealthy
        self.topic_timer: Dict[str, QtCore.QTimer] = {}

        fcc_status = StatusLabel("FCM")
        self.topic_status_map["vrc/fcm"] = fcc_status
        status_layout.addWidget(fcc_status)

        # pcc_status = StatusLabel("PCC")
        # self.topic_status_map["vrc/pcm"] = pcc_status
        # status_layout.addWidget(pcc_status)

        vio_status = StatusLabel("VIO")
        self.topic_status_map["vrc/vio"] = vio_status
        status_layout.addWidget(vio_status)

        at_status = StatusLabel("AT")
        self.topic_status_map["vrc/apriltag"] = at_status
        status_layout.addWidget(at_status)

        fus_status = StatusLabel("FUS")
        self.topic_status_map["vrc/fusion"] = fus_status
        status_layout.addWidget(fus_status)

        layout.addWidget(status_groupbox, 4, 0, 1, 4)

# ==========================
        #Gimbal 
        gimbal_groupbox = QtWidgets.QGroupBox("Camera/Laser Gimbal")
        gimbal_layout = QtWidgets.QVBoxLayout()
        gimbal_groupbox.setLayout(gimbal_layout)

         # Create joystick 
        joystick = Joystick(self.parent_.mqtt_client)

        gimbal_layout.addWidget(joystick)

        laser_enable_button = QtWidgets.QPushButton("Laser On")
        laser_enable_button.clicked.connect(lambda: self.laser_on())  # type: ignore
        gimbal_layout.addWidget(laser_enable_button)

        laser_disable_button = QtWidgets.QPushButton("Laser Off")
        laser_disable_button.clicked.connect(lambda: self.laser_off())  # type: ignore
        gimbal_layout.addWidget(laser_disable_button)


        layout.addWidget(gimbal_groupbox, 5, 0, 1, 5)


         # ==========================
        # Thermal Heatmap
        thermal_groupbox = QtWidgets.QGroupBox("Thermal Map")
        thermal_layout = QtWidgets.QHBoxLayout()
        thermal_groupbox.setLayout(thermal_layout)


    def publish_message(self, topic: str, payload: dict) -> None:
        """
        Publish a message to a topic
        """
        self.parent_.mqtt_client.publish(topic=topic, payload=json.dumps(payload))

    def set_servo(self, number: int, action: str) -> None:
        """
        Set a servo state
        """
        self.publish_message(
            "vrc/pcm/set_servo_open_close", {"servo": number, "action": action}
        )

    def set_servo_all(self, action: str) -> None:
        """
        Set all servos to the same state
        """
        for i in range(4):
            self.set_servo(i, action)

    def set_led(self, color: Tuple[int, int, int, int]) -> None:
        """
        Set LED color
        """
        self.publish_message("vrc/pcm/set_base_color", {"wrgb": color})

    def set_autonomous(self, state: bool) -> None:
        """
        Set autonomous mode
        """
        self.publish_message("vrc/autonomous", {"enable": state})

    def process_message(self, topic: str, payload: str) -> None:
        """
        Process a new message on a topic
        """
        for status_prefix in self.topic_status_map.keys():
            if topic.startswith(status_prefix):
                # set icon to healthy
                status_label = self.topic_status_map[status_prefix]
                status_label.set_health(True)

                # reset existing timer
                if status_prefix in self.topic_timer:
                    timer = self.topic_timer[status_prefix]
                    timer.stop()
                    timer.deleteLater()

                # create a new timer
                # Can't do .singleShot on an exisiting QTimer as that
                # creates a new instance
                timer = QtCore.QTimer()
                timer.timeout.connect(lambda: status_label.set_health(False))  # type: ignore
                timer.setSingleShot(True)
                timer.start(2000)

                self.topic_timer[status_prefix] = timer


class ExpandCollapseQTreeWidget(QtWidgets.QTreeWidget):
    # This widget is a subclass of QTreeWidget with a right-click menu
    # to expand/collapse all/children.
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


class ThermalViewWidget():
    # This is a window to show the thermal camera view

    def __init__(self, parent: MainWidget, control: ControlWidget) -> None:
        self.thermalview = VRC_ThermalView()
        self.control = control
        #set up a continuing request for an update to the thermal reading
    
        
        
    #Request to updated the thermal image -- 
    # a vrc/pcc/therml_reading message should be sent back soon
    def update_thermal(self):
        while (True) : 
            self.control.request_thermal_reading()
            time.sleep(0.25)
    
    
    def map_value(self,x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def process_message(self, topic: str, payload: str) -> None:
        """
        Process a new message on a topic.
        """
        if topic=="vrc/thermal/thermal_reading":
            payload_json = json.loads(payload)
            datapayload = payload_json['reading']

            #A lot of decoding -- maybe too many steps??
            base64Decoded = datapayload.encode('utf-8')
            asbytes = base64.b64decode(base64Decoded)
            b = bytearray(asbytes)
            int_values = [x for x in b]
            #print(int_values)
            #back on scale
           # pixels = [self.map_value(p, 0, 255, 15.0, 40.0) for p in int_values]
           # pixels = pixels[0:64]
            #update the image
            self.thermalview.update(int_values)



class MQTTViewWidget(QtWidgets.QWidget):
    # This widget is an effective clone of MQTT Explorer for diagnostic purposes.
    # Displays the latest MQTT message for every topic in a tree view.

    def __init__(self, parent: MainWidget) -> None:
        self.parent_ = parent
        super().__init__()

        self.setWindowTitle("Bell VRC MQTT Explorer")
        set_icon(self)

        # secondary data store to maintain dict of topics and the last message recieved
        self.topic_payloads: Dict[str, Any] = {}

        # data structure to hold timers to blink item
        self.topic_timer: Dict[str, QtCore.QTimer] = {}

        # maintain the topic currently displayed in the data view.
        self.connected_topic: Optional[str] = None

    def build(self) -> None:
        """
        Build the layout
        """
        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        self.tree_widget = ExpandCollapseQTreeWidget()
        self.tree_widget.setHeaderLabels(["Topic", "# Messages"])
        self.tree_widget.setSortingEnabled(True)
        self.tree_widget.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.tree_widget.setAnimated(True)
        self.tree_widget.setIndentation(10)
        self.tree_widget.clicked.connect(self.connect_topic_to_display)  # type: ignore
        layout.addWidget(self.tree_widget)

        self.data_view = QtWidgets.QTextEdit()
        self.data_view.setReadOnly(True)
        self.data_view.setStyleSheet("background-color: rgb(220, 220, 220)")
        layout.addWidget(self.data_view)

    def _get_or_create_child(
        self, parent: QtWidgets.QTreeWidgetItem, name: str
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

    def _get_parents(
        self, item: QtWidgets.QTreeWidgetItem
    ) -> List[QtWidgets.QTreeWidgetItem]:
        """
        Gets a list of parent QTreeWidgetItems of a QTreeWidgetItem.
        The list will be in order from top down, and include the original item.
        """
        parents = [item]

        parent = item.parent()
        while parent is not None:
            parents.insert(0, parent)
            item = parent
            parent = item.parent()

        return parents

    def process_message(self, topic: str, payload: str) -> None:
        """
        Process a new message on a topic.
        """
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
            if not count:  # sourcery skip
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

    def connect_topic_to_display(self, idx: QtCore.QModelIndex) -> None:
        """
        When an item is clicked, get the topic for it, and connect it to the data view
        """
        # get the selected item
        item = self.tree_widget.currentItem()
        # rebuild the topic name
        topic = "/".join(p.text(0) for p in self._get_parents(item))

        # if the selected item isn't a real topic, clear
        if topic not in self.topic_payloads.keys():
            self.connected_topic = None

        # mark the topic as connected
        self.connected_topic = topic
        # force update data
        self.display_data(self.connected_topic)

    def display_data(self, topic: str) -> None:
        """
        Display data from a topic to the data view
        """
        # get the last known data for the topic
        if topic not in self.topic_payloads:
            payload = ""
        else:
            payload = self.topic_payloads[topic]

        try:
            # try to format valid JSON
            payload_json = json.loads(payload)
            payload = json.dumps(payload_json, indent=4)
        except json.JSONDecodeError:
            pass

        # set the data
        self.data_view.setText(payload)

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
            item.setBackground(0, QtGui.QColor(220, 220, 220))

        # start new timer to clear background
        timer = QtCore.QTimer()
        timer.timeout.connect(lambda: item.setBackground(0, QtGui.QColor(255, 255, 255)))  # type: ignore
        timer.setSingleShot(True)
        timer.start(100)

        self.topic_timer[topic] = timer


def main() -> None:
    # create Qt Application instance
    app = QtWidgets.QApplication()

    # create the main widget
    MainWidget()

    # run
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
