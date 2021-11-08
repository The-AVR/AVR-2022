#Qt GUI application for testing the PCC functionality
#written by Patrick Smith, with guest appearance by Casey Hanner
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtCore import Qt, QThread, Signal, QObject
from PySide6.QtGui import QColor, QPalette, QFont

from UI_pcc import Ui_VRC_PCC
from startup_widget import Ui_VRC_startup
from serial_utils import serial_ports

from pcc_library import VRC_peripheral

import sys
import time

class SetupWindow(QWidget):
    def __init__(self, ports):
        super(SetupWindow, self).__init__()
        self.ui = Ui_VRC_startup()
        self.ui.setupUi(self)

        self.ui.COM_Port_comboBox.addItems(ports)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        #self.Comms = CommThread()
        self.pcc = None
        self.actuator_states = [0,0,0,0]

        # UNCOMMENT THIS FOR CONNECTING TO SERIAL PORT
        self.setup = SetupWindow(serial_ports())
        self.setup.ui.Connect_Button.clicked.connect(self.connectToPCC)
        self.setup.show()
        self.ui = Ui_VRC_PCC()

    def setupMainWindowUi(self):
        self.ui.setupUi(self)

        # update actuator percentage cmd based on slider / spinbox
        self.ui.actuator_1_dial.valueChanged.connect(self.actuator_generator(0))
        self.ui.actuator_2_dial.valueChanged.connect(self.actuator_generator(1))
        self.ui.actuator_3_dial.valueChanged.connect(self.actuator_generator(2))
        self.ui.actuator_4_dial.valueChanged.connect(self.actuator_generator(3))

        # update RGB LED based on sliders
        self.ui.red_led_slider.valueChanged.connect(self.updateRGBcmd)
        self.ui.green_led_slider.valueChanged.connect(self.updateRGBcmd)
        self.ui.blue_led_slider.valueChanged.connect(self.updateRGBcmd)

        #call the special open/close command on button click
        self.ui.actuator_1_toggle.pressed.connect(self.toggleGenerator(0))
        self.ui.actuator_2_toggle.clicked.connect(self.toggleGenerator(1))
        self.ui.actuator_3_toggle.clicked.connect(self.toggleGenerator(2))
        self.ui.actuator_4_toggle.clicked.connect(self.toggleGenerator(3))


    def connectToPCC(self):
        '''
        this function establishes the serial connection to the PCC based on available COM ports
        or shows the debug output if no com ports are found
        '''

        try:
            port = self.setup.ui.COM_Port_comboBox.currentText()
            baud = self.setup.ui.Baud_Rate_comboBox.currentText()

            if port == "":
                self.pcc = VRC_peripheral(port, use_serial=False)
            else:
                self.pcc = VRC_peripheral(port, use_serial=True)

            #TODO - actually write a handshake for the PCC, its all 1 way right now
            #try:
                #self.pcc.handshake(timeout=1)
            #except TimeoutError as e:
                #show error window and close?

            self.setup.close()

            self.setupMainWindowUi()
            self.show()

        except Exception as e:
            print("Error connecting to PCC serial port! ", e)



    def updateActuatorCmd(self, actuator, value):
        '''
        whenever any of the dials change, this function gets called to
        update the PCC with the most current command for all 4 actuators
        '''


        # collect the most current pwm commands
        try:
            self.pcc.set_servo_pct(actuator, value)
        except AttributeError as ae:
            print("Can't sent serial command, Serial Port not set up...")

    def actuator_generator(self, actuator):
        '''
        creates a template of the "updateActuatorCmd" with the actuator hardcoded to "actuator"

        that way the resulting template can take in just the "value" parameter and be used with the Qt callback
        '''

        def updateActuatorCmd(value):
            self.updateActuatorCmd(actuator, value)
        return updateActuatorCmd

    def toggleActuator(self, actuator):
        '''
        toggles the specified actuator (based on appications recorded state, not PCCs internal state)
        '''
        if actuator in range(0,4):
            if self.actuator_states[actuator] == 1:
                self.pcc.set_servo_open_close(actuator, "close")
                self.actuator_states[actuator] = 0
            else:
                self.pcc.set_servo_open_close(actuator, "open")
                self.actuator_states[actuator] = 1

    def toggleGenerator(self, actuator):
        def toggle():
            self.toggleActuator(actuator)
        return toggle

    def updateRGBcmd(self, val):
        '''
        whenever any of the RGB commands change, this function gets called to
        update the PCC with the most current RGB commands for the LED strip
        '''

        # collect the most current pwm commands
        red = self.ui.red_led_slider.value()
        green = self.ui.green_led_slider.value()
        blue = self.ui.blue_led_slider.value()

        # send serial message down serial link to PCC
        try:
            self.pcc.set_base_color([0,red,green,blue])
        except AttributeError as ae:
            print("Can't sent serial command, Serial Port not set up...")





if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()

    app.exec_()

    if window.pcc is not None:
        window.pcc.set_base_color([0,0,0,0])

    sys.exit()

