import sys

from lib.enums import ConnectionState
from lib.qt_icon import set_icon
from loguru import logger
from PySide6 import QtCore, QtGui, QtWidgets
from tabs.connection.main import MainConnectionWidget
from tabs.mqtt_debug import MQTTDebugWidget
from tabs.pcc_tester import PCCTesterWidget
from tabs.thermal_view_control import ThermalViewControlWidget
from tabs.vmc_control import VMCControlWidget
from tabs.vmc_telemetry import VMCTelemetryWidget


class TabBar(QtWidgets.QTabBar):
    """
    Custom QTabBar for a QTabWidget to allow the tabs to be popped in/out
    from an external window.
    """

    pop_out: QtCore.SignalInstance = QtCore.Signal(int)  # type: ignore

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tabBarDoubleClicked.connect(self.pop_out)  # type: ignore

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        menu = QtWidgets.QMenu(self)

        # needs to be done before the menu is poped up, otherwise the QEvent will expire
        selected_item = self.tabAt(event.pos())

        pop_out_action = QtGui.QAction("Pop Out", self)
        pop_out_action.triggered.connect(lambda: self.pop_out.emit(selected_item))  # type: ignore
        menu.addAction(pop_out_action)

        menu.popup(QtGui.QCursor.pos())


class TabWidget(QtWidgets.QTabWidget):
    """
    Custom QTabWidget that allows the tab to be popped in/out from an external window.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tab_bar = TabBar(self)
        self.setTabBar(self.tab_bar)
        self.setMovable(True)

        self.tab_bar.pop_out.connect(self.pop_out)

    def pop_out(self, index: int) -> None:
        """
        Pop a tab out into a new window.
        """
        tab = self.widget(index)
        logger.debug(f"Pop out requested on tab {index}, {tab}")

        # don't allow user to pop out last tab
        visible = [i for i in range(self.count()) if self.isTabVisible(i)]
        logger.debug(f"Visible tabs: {visible}")
        if len(visible) <= 1:
            logger.warning("Not popping out last visible tab")
            return

        # don't allow user to pop out the last enabled, visible tab
        enabled_visible = [i for i in visible if self.isTabEnabled(i)]
        logger.debug(f"Enabled visible tabs: {enabled_visible}")
        if len(enabled_visible) <= 1 and index in enabled_visible:
            logger.warning("Not popping out last visible enabled tab")
            return

        self.setTabVisible(index, False)
        tab.setWindowFlags(QtCore.Qt.Window)  # type: ignore
        tab.show()

    def pop_in(self, widget: QtWidgets.QWidget) -> None:
        """
        Pop a tab out into a new window.
        """
        index = self.indexOf(widget)
        logger.debug(f"Popping in tab {index}, {widget}")

        widget.setWindowFlags(QtCore.Qt.Widget)  # type: ignore
        self.setTabVisible(index, True)


class MainWindow(QtWidgets.QWidget):
    """
    This is the main application class.
    """

    def __init__(self) -> None:
        super().__init__()

        set_icon(self)
        self.setWindowTitle("VRC GUI")

        self.mqtt_connected = False
        self.serial_connected = False

    def build(self) -> None:
        """
        Build the GUI layout
        """
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)

        self.tabs = TabWidget(self)
        layout.addWidget(self.tabs)

        # add tabs

        self.main_connection_widget = MainConnectionWidget(self)
        self.main_connection_widget.build()
        self.main_connection_widget.pop_in.connect(self.tabs.pop_in)
        self.tabs.addTab(
            self.main_connection_widget, self.main_connection_widget.windowTitle()
        )

        self.mqtt_debug_widget = MQTTDebugWidget(self)
        self.mqtt_debug_widget.build()
        self.mqtt_debug_widget.pop_in.connect(self.tabs.pop_in)
        self.tabs.addTab(self.mqtt_debug_widget, self.mqtt_debug_widget.windowTitle())

        self.vmc_control_widget = VMCControlWidget(self)
        self.vmc_control_widget.build()
        self.vmc_control_widget.pop_in.connect(self.tabs.pop_in)
        self.tabs.addTab(self.vmc_control_widget, self.vmc_control_widget.windowTitle())

        self.vmc_telemetry_widget = VMCTelemetryWidget(self)
        self.vmc_telemetry_widget.build()
        self.vmc_telemetry_widget.pop_in.connect(self.tabs.pop_in)
        self.tabs.addTab(
            self.vmc_telemetry_widget, self.vmc_telemetry_widget.windowTitle()
        )

        self.thermal_view_control_widget = ThermalViewControlWidget(self)
        self.thermal_view_control_widget.build()
        self.thermal_view_control_widget.pop_in.connect(self.tabs.pop_in)
        self.tabs.addTab(
            self.thermal_view_control_widget,
            self.thermal_view_control_widget.windowTitle(),
        )

        self.pcc_tester_widget = PCCTesterWidget(
            self, self.main_connection_widget.serial_connection_widget.serial_client
        )
        self.pcc_tester_widget.build()
        self.pcc_tester_widget.pop_in.connect(self.tabs.pop_in)
        self.tabs.addTab(self.pcc_tester_widget, self.pcc_tester_widget.windowTitle())

        # configure connections

        self.main_connection_widget.mqtt_connection_widget.connection_state.connect(
            self.set_mqtt_connected_state
        )
        self.main_connection_widget.mqtt_connection_widget.mqtt_client.message.connect(
            self.mqtt_debug_widget.process_message
        )
        self.main_connection_widget.serial_connection_widget.connection_state.connect(
            self.set_serial_connected_state
        )

        self.mqtt_debug_widget.send_message.connect(
            self.main_connection_widget.mqtt_connection_widget.mqtt_client.publish
        )

        self.vmc_control_widget.send_message.connect(
            self.main_connection_widget.mqtt_connection_widget.mqtt_client.publish
        )

        self.main_connection_widget.mqtt_connection_widget.mqtt_client.message.connect(
            self.vmc_telemetry_widget.process_message
        )

        # set initial state

        self.set_mqtt_connected_state(ConnectionState.disconnected)
        self.set_serial_connected_state(ConnectionState.disconnected)

    def set_mqtt_connected_state(self, connection_state: ConnectionState) -> None:
        self.mqtt_connected = connection_state == ConnectionState.connected

        # list of widgets that are mqtt connected
        widgets = [
            self.mqtt_debug_widget,
            self.vmc_control_widget,
            self.vmc_telemetry_widget,
            self.thermal_view_control_widget,
        ]

        # disable/enable widgets
        for widget in widgets:
            idx = self.tabs.indexOf(widget)
            self.tabs.setTabEnabled(idx, self.mqtt_connected)
            if not self.mqtt_connected:
                self.tabs.setTabToolTip(idx, "MQTT not connected")
            else:
                self.tabs.setTabToolTip(idx, "")

        # telemetry stuff is special case
        if not self.mqtt_connected:
            self.mqtt_debug_widget.clear()
            self.vmc_telemetry_widget.clear()

    def set_serial_connected_state(self, connection_state: ConnectionState) -> None:
        self.serial_connected = connection_state == ConnectionState.connected

        # deal with pcc tester
        idx = self.tabs.indexOf(self.pcc_tester_widget)
        self.tabs.setTabEnabled(idx, self.serial_connected)
        if not self.serial_connected:
            self.pcc_tester_widget.reset_all()
            self.tabs.setTabToolTip(idx, "Serial not connected")
        else:
            self.tabs.setTabToolTip(idx, "")

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """
        Override close event to close all connections.
        """
        if self.mqtt_connected:
            self.main_connection_widget.mqtt_connection_widget.mqtt_client.logout()

        if self.serial_connected:
            self.main_connection_widget.serial_connection_widget.serial_client.logout()

        event.accept()


def main() -> None:
    # create Qt Application instance
    app = QtWidgets.QApplication()

    # create the main window
    w = MainWindow()
    w.build()
    w.show()

    # run
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
