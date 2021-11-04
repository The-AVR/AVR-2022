# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'UI_pcc.ui'
##
## Created by: Qt User Interface Compiler version 6.0.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_VRC_PCC(object):
    def setupUi(self, VRC_PCC):
        if not VRC_PCC.objectName():
            VRC_PCC.setObjectName(u"VRC_PCC")
        VRC_PCC.resize(659, 832)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(VRC_PCC.sizePolicy().hasHeightForWidth())
        VRC_PCC.setSizePolicy(sizePolicy)
        VRC_PCC.setMinimumSize(QSize(600, 760))
        font = QFont()
        font.setFamily(u"Arial Black")
        VRC_PCC.setFont(font)
        VRC_PCC.setCursor(QCursor(Qt.ArrowCursor))
        VRC_PCC.setAutoFillBackground(False)
        VRC_PCC.setStyleSheet(u"QMainWindow {\n"
"background: transparent; \n"
"	background-color: rgba(20, 0, 62, 100);\n"
"}\n"
"QToolTip {\n"
"	color: #ffffff;\n"
"	background-color: rgba(27, 29, 35, 160);\n"
"	border: 1px solid rgb(40, 40, 40);\n"
"	border-radius: 2px;\n"
"}\n"
"")
        self.actionManual_Control = QAction(VRC_PCC)
        self.actionManual_Control.setObjectName(u"actionManual_Control")
        self.actionProfile_1 = QAction(VRC_PCC)
        self.actionProfile_1.setObjectName(u"actionProfile_1")
        self.actionProfile_2 = QAction(VRC_PCC)
        self.actionProfile_2.setObjectName(u"actionProfile_2")
        self.actionCOM1 = QAction(VRC_PCC)
        self.actionCOM1.setObjectName(u"actionCOM1")
        self.actionCOM2 = QAction(VRC_PCC)
        self.actionCOM2.setObjectName(u"actionCOM2")
        self.actionCOM3 = QAction(VRC_PCC)
        self.actionCOM3.setObjectName(u"actionCOM3")
        self.actionCOM4 = QAction(VRC_PCC)
        self.actionCOM4.setObjectName(u"actionCOM4")
        self.actionCOM5 = QAction(VRC_PCC)
        self.actionCOM5.setObjectName(u"actionCOM5")
        self.actionCOM6 = QAction(VRC_PCC)
        self.actionCOM6.setObjectName(u"actionCOM6")
        self.actionCOM7 = QAction(VRC_PCC)
        self.actionCOM7.setObjectName(u"actionCOM7")
        self.action115200 = QAction(VRC_PCC)
        self.action115200.setObjectName(u"action115200")
        self.actionEnter = QAction(VRC_PCC)
        self.actionEnter.setObjectName(u"actionEnter")
        self.actionEnter_2 = QAction(VRC_PCC)
        self.actionEnter_2.setObjectName(u"actionEnter_2")
        self.centralwidget = QWidget(VRC_PCC)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setMinimumSize(QSize(0, 650))
        font1 = QFont()
        font1.setFamily(u"Arial Black")
        font1.setPointSize(8)
        font1.setBold(True)
        font1.setItalic(False)
        self.centralwidget.setFont(font1)
        self.centralwidget.setStyleSheet(u"background: transparent;\n"
"")
        self.horizontalLayout_6 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.frame_6 = QFrame(self.centralwidget)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setMinimumSize(QSize(400, 800))
        font2 = QFont()
        font2.setFamily(u"Arial Black")
        font2.setPointSize(15)
        font2.setBold(False)
        font2.setItalic(False)
        self.frame_6.setFont(font2)
        self.frame_6.setStyleSheet(u"background-color: rgb(99, 99, 99);\n"
"QLabel {\n"
"	border-radius: 3px;\n"
"	border: 2px solid rgb(27, 29, 35);\n"
"	padding-left: 5px;\n"
"};\n"
"\n"
"")
        self.frame_6.setFrameShape(QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.gridLayout = QGridLayout(self.frame_6)
        self.gridLayout.setObjectName(u"gridLayout")
        self.frame_10 = QFrame(self.frame_6)
        self.frame_10.setObjectName(u"frame_10")
        self.frame_10.setMinimumSize(QSize(300, 170))
        self.frame_10.setFrameShape(QFrame.StyledPanel)
        self.frame_10.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.frame_10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setSpacing(1)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.frame_16 = QFrame(self.frame_10)
        self.frame_16.setObjectName(u"frame_16")
        self.frame_16.setMinimumSize(QSize(200, 150))
        self.frame_16.setMaximumSize(QSize(16777215, 16777215))
        self.frame_16.setStyleSheet(u"background-color: rgba(86, 81, 100, 200);\n"
"color: rgb(255, 255, 255);")
        self.frame_16.setFrameShape(QFrame.StyledPanel)
        self.frame_16.setFrameShadow(QFrame.Raised)
        self.verticalLayout_12 = QVBoxLayout(self.frame_16)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.actuator_1_label = QLabel(self.frame_16)
        self.actuator_1_label.setObjectName(u"actuator_1_label")
        self.actuator_1_label.setMinimumSize(QSize(125, 25))
        self.actuator_1_label.setMaximumSize(QSize(125, 20))
        font3 = QFont()
        font3.setFamily(u"Arial Black")
        font3.setPointSize(8)
        font3.setBold(False)
        font3.setItalic(False)
        self.actuator_1_label.setFont(font3)
        self.actuator_1_label.setStyleSheet(u"background-color: rgba(255, 255, 255, 0);\n"
"border-radius: 3px;\n"
"border: 2px solid rgb(27, 29, 35);\n"
"padding-left: 5px;")
        self.actuator_1_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_12.addWidget(self.actuator_1_label, 0, Qt.AlignHCenter)

        self.horizontalLayout_24 = QHBoxLayout()
        self.horizontalLayout_24.setSpacing(30)
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.horizontalLayout_24.setContentsMargins(0, 10, 20, 10)
        self.actuator_1_dial = QDial(self.frame_16)
        self.actuator_1_dial.setObjectName(u"actuator_1_dial")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.actuator_1_dial.sizePolicy().hasHeightForWidth())
        self.actuator_1_dial.setSizePolicy(sizePolicy1)
        self.actuator_1_dial.setMinimumSize(QSize(70, 70))
        self.actuator_1_dial.setMaximumSize(QSize(200, 200))
        self.actuator_1_dial.setOrientation(Qt.Horizontal)
        self.actuator_1_dial.setNotchesVisible(True)

        self.horizontalLayout_24.addWidget(self.actuator_1_dial)

        self.actuator_1_lcd = QLCDNumber(self.frame_16)
        self.actuator_1_lcd.setObjectName(u"actuator_1_lcd")
        sizePolicy1.setHeightForWidth(self.actuator_1_lcd.sizePolicy().hasHeightForWidth())
        self.actuator_1_lcd.setSizePolicy(sizePolicy1)
        self.actuator_1_lcd.setMinimumSize(QSize(70, 70))
        self.actuator_1_lcd.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_24.addWidget(self.actuator_1_lcd)


        self.verticalLayout_12.addLayout(self.horizontalLayout_24)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.actuator_1_toggle = QPushButton(self.frame_16)
        self.actuator_1_toggle.setObjectName(u"actuator_1_toggle")
        self.actuator_1_toggle.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.actuator_1_toggle.sizePolicy().hasHeightForWidth())
        self.actuator_1_toggle.setSizePolicy(sizePolicy1)
        self.actuator_1_toggle.setMinimumSize(QSize(100, 100))
        self.actuator_1_toggle.setSizeIncrement(QSize(0, 0))
        self.actuator_1_toggle.setCheckable(True)

        self.horizontalLayout_5.addWidget(self.actuator_1_toggle)


        self.verticalLayout_12.addLayout(self.horizontalLayout_5)


        self.gridLayout_2.addWidget(self.frame_16, 0, 1, 1, 1)

        self.frame_13 = QFrame(self.frame_10)
        self.frame_13.setObjectName(u"frame_13")
        self.frame_13.setMinimumSize(QSize(200, 150))
        self.frame_13.setMaximumSize(QSize(16777215, 16777215))
        self.frame_13.setStyleSheet(u"background-color: rgba(86, 81, 100, 200);\n"
"color: rgb(255, 255, 255);")
        self.frame_13.setFrameShape(QFrame.StyledPanel)
        self.frame_13.setFrameShadow(QFrame.Raised)
        self.verticalLayout_9 = QVBoxLayout(self.frame_13)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.actuator_2_label = QLabel(self.frame_13)
        self.actuator_2_label.setObjectName(u"actuator_2_label")
        self.actuator_2_label.setMinimumSize(QSize(125, 25))
        self.actuator_2_label.setMaximumSize(QSize(125, 20))
        self.actuator_2_label.setFont(font3)
        self.actuator_2_label.setStyleSheet(u"background-color: rgba(255, 255, 255, 0);\n"
"border-radius: 3px;\n"
"border: 2px solid rgb(27, 29, 35);\n"
"padding-left: 5px;")
        self.actuator_2_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_9.addWidget(self.actuator_2_label, 0, Qt.AlignHCenter)

        self.horizontalLayout_21 = QHBoxLayout()
        self.horizontalLayout_21.setSpacing(30)
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.horizontalLayout_21.setContentsMargins(0, 10, 20, 10)
        self.actuator_2_dial = QDial(self.frame_13)
        self.actuator_2_dial.setObjectName(u"actuator_2_dial")
        self.actuator_2_dial.setMinimumSize(QSize(70, 70))
        self.actuator_2_dial.setMaximumSize(QSize(200, 200))
        self.actuator_2_dial.setOrientation(Qt.Horizontal)
        self.actuator_2_dial.setNotchesVisible(True)

        self.horizontalLayout_21.addWidget(self.actuator_2_dial)

        self.actuator_2_lcd = QLCDNumber(self.frame_13)
        self.actuator_2_lcd.setObjectName(u"actuator_2_lcd")
        sizePolicy1.setHeightForWidth(self.actuator_2_lcd.sizePolicy().hasHeightForWidth())
        self.actuator_2_lcd.setSizePolicy(sizePolicy1)
        self.actuator_2_lcd.setMinimumSize(QSize(70, 70))
        self.actuator_2_lcd.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_21.addWidget(self.actuator_2_lcd)


        self.verticalLayout_9.addLayout(self.horizontalLayout_21)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.actuator_2_toggle = QPushButton(self.frame_13)
        self.actuator_2_toggle.setObjectName(u"actuator_2_toggle")
        self.actuator_2_toggle.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.actuator_2_toggle.sizePolicy().hasHeightForWidth())
        self.actuator_2_toggle.setSizePolicy(sizePolicy1)
        self.actuator_2_toggle.setMinimumSize(QSize(100, 100))
        self.actuator_2_toggle.setSizeIncrement(QSize(0, 0))
        self.actuator_2_toggle.setCheckable(True)

        self.horizontalLayout_2.addWidget(self.actuator_2_toggle)


        self.verticalLayout_9.addLayout(self.horizontalLayout_2)


        self.gridLayout_2.addWidget(self.frame_13, 0, 2, 1, 1)

        self.frame_15 = QFrame(self.frame_10)
        self.frame_15.setObjectName(u"frame_15")
        self.frame_15.setMinimumSize(QSize(200, 150))
        self.frame_15.setMaximumSize(QSize(16777215, 1677215))
        self.frame_15.setStyleSheet(u"background-color: rgba(86, 81, 100, 200);\n"
"color: rgb(255, 255, 255);")
        self.frame_15.setFrameShape(QFrame.StyledPanel)
        self.frame_15.setFrameShadow(QFrame.Raised)
        self.verticalLayout_11 = QVBoxLayout(self.frame_15)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.actuator_3_label = QLabel(self.frame_15)
        self.actuator_3_label.setObjectName(u"actuator_3_label")
        self.actuator_3_label.setMinimumSize(QSize(125, 25))
        self.actuator_3_label.setMaximumSize(QSize(125, 20))
        self.actuator_3_label.setFont(font3)
        self.actuator_3_label.setStyleSheet(u"background-color: rgba(255, 255, 255, 0);\n"
"border-radius: 3px;\n"
"border: 2px solid rgb(27, 29, 35);\n"
"padding-left: 5px;")
        self.actuator_3_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_11.addWidget(self.actuator_3_label, 0, Qt.AlignHCenter)

        self.horizontalLayout_23 = QHBoxLayout()
        self.horizontalLayout_23.setSpacing(30)
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.horizontalLayout_23.setContentsMargins(0, 10, 20, 10)
        self.actuator_3_dial = QDial(self.frame_15)
        self.actuator_3_dial.setObjectName(u"actuator_3_dial")
        self.actuator_3_dial.setMinimumSize(QSize(70, 70))
        self.actuator_3_dial.setMaximumSize(QSize(200, 200))
        self.actuator_3_dial.setOrientation(Qt.Horizontal)
        self.actuator_3_dial.setNotchesVisible(True)

        self.horizontalLayout_23.addWidget(self.actuator_3_dial)

        self.actuator_3_lcd = QLCDNumber(self.frame_15)
        self.actuator_3_lcd.setObjectName(u"actuator_3_lcd")
        sizePolicy1.setHeightForWidth(self.actuator_3_lcd.sizePolicy().hasHeightForWidth())
        self.actuator_3_lcd.setSizePolicy(sizePolicy1)
        self.actuator_3_lcd.setMinimumSize(QSize(70, 70))
        self.actuator_3_lcd.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_23.addWidget(self.actuator_3_lcd)


        self.verticalLayout_11.addLayout(self.horizontalLayout_23)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.actuator_3_toggle = QPushButton(self.frame_15)
        self.actuator_3_toggle.setObjectName(u"actuator_3_toggle")
        self.actuator_3_toggle.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.actuator_3_toggle.sizePolicy().hasHeightForWidth())
        self.actuator_3_toggle.setSizePolicy(sizePolicy1)
        self.actuator_3_toggle.setMinimumSize(QSize(100, 100))
        self.actuator_3_toggle.setSizeIncrement(QSize(0, 0))
        self.actuator_3_toggle.setCheckable(True)

        self.horizontalLayout_4.addWidget(self.actuator_3_toggle)


        self.verticalLayout_11.addLayout(self.horizontalLayout_4)


        self.gridLayout_2.addWidget(self.frame_15, 1, 1, 1, 1)

        self.frame_14 = QFrame(self.frame_10)
        self.frame_14.setObjectName(u"frame_14")
        self.frame_14.setMinimumSize(QSize(200, 150))
        self.frame_14.setMaximumSize(QSize(16777215, 16777215))
        self.frame_14.setStyleSheet(u"background-color: rgba(86, 81, 100, 200);\n"
"color: rgb(255, 255, 255);")
        self.frame_14.setFrameShape(QFrame.StyledPanel)
        self.frame_14.setFrameShadow(QFrame.Raised)
        self.verticalLayout_10 = QVBoxLayout(self.frame_14)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.actuator_4_label = QLabel(self.frame_14)
        self.actuator_4_label.setObjectName(u"actuator_4_label")
        self.actuator_4_label.setMinimumSize(QSize(125, 25))
        self.actuator_4_label.setMaximumSize(QSize(125, 20))
        self.actuator_4_label.setFont(font3)
        self.actuator_4_label.setStyleSheet(u"background-color: rgba(255, 255, 255, 0);\n"
"border-radius: 3px;\n"
"border: 2px solid rgb(27, 29, 35);\n"
"padding-left: 5px;")
        self.actuator_4_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_10.addWidget(self.actuator_4_label, 0, Qt.AlignHCenter)

        self.horizontalLayout_22 = QHBoxLayout()
        self.horizontalLayout_22.setSpacing(30)
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.horizontalLayout_22.setContentsMargins(0, 10, 20, 10)
        self.actuator_4_dial = QDial(self.frame_14)
        self.actuator_4_dial.setObjectName(u"actuator_4_dial")
        self.actuator_4_dial.setMinimumSize(QSize(70, 70))
        self.actuator_4_dial.setMaximumSize(QSize(200, 200))
        self.actuator_4_dial.setOrientation(Qt.Horizontal)
        self.actuator_4_dial.setNotchesVisible(True)

        self.horizontalLayout_22.addWidget(self.actuator_4_dial)

        self.actuator_4_lcd = QLCDNumber(self.frame_14)
        self.actuator_4_lcd.setObjectName(u"actuator_4_lcd")
        sizePolicy1.setHeightForWidth(self.actuator_4_lcd.sizePolicy().hasHeightForWidth())
        self.actuator_4_lcd.setSizePolicy(sizePolicy1)
        self.actuator_4_lcd.setMinimumSize(QSize(70, 70))

        self.horizontalLayout_22.addWidget(self.actuator_4_lcd)


        self.verticalLayout_10.addLayout(self.horizontalLayout_22)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.actuator_4_toggle = QPushButton(self.frame_14)
        self.actuator_4_toggle.setObjectName(u"actuator_4_toggle")
        self.actuator_4_toggle.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.actuator_4_toggle.sizePolicy().hasHeightForWidth())
        self.actuator_4_toggle.setSizePolicy(sizePolicy1)
        self.actuator_4_toggle.setMinimumSize(QSize(100, 100))
        self.actuator_4_toggle.setSizeIncrement(QSize(0, 0))
        self.actuator_4_toggle.setCheckable(True)

        self.horizontalLayout_3.addWidget(self.actuator_4_toggle)


        self.verticalLayout_10.addLayout(self.horizontalLayout_3)


        self.gridLayout_2.addWidget(self.frame_14, 1, 2, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout_2)

        self.frame_7 = QFrame(self.frame_10)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setMinimumSize(QSize(300, 110))
        self.frame_7.setMaximumSize(QSize(5000, 300))
        self.frame_7.setStyleSheet(u"background-color: rgba(86, 81, 100, 200);\n"
"color: rgb(255, 255, 255);")
        self.frame_7.setFrameShape(QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_8 = QHBoxLayout(self.frame_7)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.rgb_strip_label = QLabel(self.frame_7)
        self.rgb_strip_label.setObjectName(u"rgb_strip_label")
        self.rgb_strip_label.setMinimumSize(QSize(125, 25))
        self.rgb_strip_label.setMaximumSize(QSize(16777215, 20))
        self.rgb_strip_label.setFont(font3)
        self.rgb_strip_label.setStyleSheet(u"background-color: rgba(255, 255, 255, 0);\n"
"border-radius: 3px;\n"
"border: 2px solid rgb(27, 29, 35);\n"
"padding-left: 5px;")
        self.rgb_strip_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.rgb_strip_label)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.frame_2 = QFrame(self.frame_7)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.formLayout = QFormLayout(self.frame_2)
        self.formLayout.setObjectName(u"formLayout")
        self.GL_direction_label_2 = QLabel(self.frame_2)
        self.GL_direction_label_2.setObjectName(u"GL_direction_label_2")
        self.GL_direction_label_2.setMinimumSize(QSize(100, 25))
        self.GL_direction_label_2.setMaximumSize(QSize(100, 20))
        self.GL_direction_label_2.setFont(font3)
        self.GL_direction_label_2.setStyleSheet(u"border-radius: 3px;\n"
"border: 2px solid rgb(27, 29, 35);\n"
"padding-left: 5px;")
        self.GL_direction_label_2.setAlignment(Qt.AlignCenter)

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.GL_direction_label_2)

        self.red_led_slider = QSlider(self.frame_2)
        self.red_led_slider.setObjectName(u"red_led_slider")
        self.red_led_slider.setMaximum(255)
        self.red_led_slider.setOrientation(Qt.Horizontal)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.red_led_slider)

        self.GL_direction_label_3 = QLabel(self.frame_2)
        self.GL_direction_label_3.setObjectName(u"GL_direction_label_3")
        self.GL_direction_label_3.setMinimumSize(QSize(100, 25))
        self.GL_direction_label_3.setMaximumSize(QSize(100, 20))
        self.GL_direction_label_3.setFont(font3)
        self.GL_direction_label_3.setStyleSheet(u"border-radius: 3px;\n"
"border: 2px solid rgb(27, 29, 35);\n"
"padding-left: 5px;")
        self.GL_direction_label_3.setAlignment(Qt.AlignCenter)

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.GL_direction_label_3)

        self.green_led_slider = QSlider(self.frame_2)
        self.green_led_slider.setObjectName(u"green_led_slider")
        self.green_led_slider.setMaximum(255)
        self.green_led_slider.setOrientation(Qt.Horizontal)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.green_led_slider)

        self.GL_direction_label_4 = QLabel(self.frame_2)
        self.GL_direction_label_4.setObjectName(u"GL_direction_label_4")
        self.GL_direction_label_4.setMinimumSize(QSize(100, 25))
        self.GL_direction_label_4.setMaximumSize(QSize(100, 20))
        self.GL_direction_label_4.setFont(font3)
        self.GL_direction_label_4.setStyleSheet(u"border-radius: 3px;\n"
"border: 2px solid rgb(27, 29, 35);\n"
"padding-left: 5px;")
        self.GL_direction_label_4.setAlignment(Qt.AlignCenter)

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.GL_direction_label_4)

        self.blue_led_slider = QSlider(self.frame_2)
        self.blue_led_slider.setObjectName(u"blue_led_slider")
        self.blue_led_slider.setMaximum(255)
        self.blue_led_slider.setOrientation(Qt.Horizontal)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.blue_led_slider)


        self.horizontalLayout.addWidget(self.frame_2)

        self.frame = QFrame(self.frame_7)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.rgb_r_cmd = QSpinBox(self.frame)
        self.rgb_r_cmd.setObjectName(u"rgb_r_cmd")
        self.rgb_r_cmd.setMaximumSize(QSize(50, 16777215))
        font4 = QFont()
        font4.setFamily(u"Arial Black")
        font4.setPointSize(11)
        font4.setBold(False)
        font4.setItalic(False)
        self.rgb_r_cmd.setFont(font4)
        self.rgb_r_cmd.setMaximum(255)

        self.verticalLayout_2.addWidget(self.rgb_r_cmd)

        self.rgb_g_cmd = QSpinBox(self.frame)
        self.rgb_g_cmd.setObjectName(u"rgb_g_cmd")
        self.rgb_g_cmd.setMaximumSize(QSize(50, 16777215))
        self.rgb_g_cmd.setFont(font4)
        self.rgb_g_cmd.setMaximum(255)

        self.verticalLayout_2.addWidget(self.rgb_g_cmd)

        self.rgb_b_cmd = QSpinBox(self.frame)
        self.rgb_b_cmd.setObjectName(u"rgb_b_cmd")
        self.rgb_b_cmd.setMaximumSize(QSize(50, 16777215))
        self.rgb_b_cmd.setFont(font4)
        self.rgb_b_cmd.setMaximum(255)

        self.verticalLayout_2.addWidget(self.rgb_b_cmd)


        self.horizontalLayout.addWidget(self.frame)


        self.verticalLayout_3.addLayout(self.horizontalLayout)


        self.horizontalLayout_8.addLayout(self.verticalLayout_3)


        self.verticalLayout.addWidget(self.frame_7)


        self.gridLayout.addWidget(self.frame_10, 1, 0, 1, 1)

        self.Title = QLabel(self.frame_6)
        self.Title.setObjectName(u"Title")
        self.Title.setMinimumSize(QSize(200, 30))
        self.Title.setMaximumSize(QSize(16777215, 25))
        font5 = QFont()
        font5.setFamily(u"Arial Black")
        font5.setPointSize(14)
        font5.setBold(False)
        font5.setItalic(False)
        self.Title.setFont(font5)
        self.Title.setStyleSheet(u"font: 87 14pt \"Arial Black\";\n"
"background-color: rgba(86, 81, 100, 200);\n"
"color: rgb(255, 255, 255);\n"
"border-radius: 3px;\n"
"border: 2px solid rgb(27, 29, 35);\n"
"padding-left: 5px;\n"
"")
        self.Title.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.Title, 0, 0, 1, 1)


        self.horizontalLayout_6.addWidget(self.frame_6)

        VRC_PCC.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(VRC_PCC)
        self.statusbar.setObjectName(u"statusbar")
        sizePolicy1.setHeightForWidth(self.statusbar.sizePolicy().hasHeightForWidth())
        self.statusbar.setSizePolicy(sizePolicy1)
        self.statusbar.setStyleSheet(u"")
        VRC_PCC.setStatusBar(self.statusbar)

        self.retranslateUi(VRC_PCC)
        self.red_led_slider.valueChanged.connect(self.rgb_r_cmd.setValue)
        self.rgb_r_cmd.valueChanged.connect(self.red_led_slider.setValue)
        self.green_led_slider.valueChanged.connect(self.rgb_g_cmd.setValue)
        self.rgb_g_cmd.valueChanged.connect(self.green_led_slider.setValue)
        self.blue_led_slider.valueChanged.connect(self.rgb_b_cmd.setValue)
        self.rgb_b_cmd.valueChanged.connect(self.blue_led_slider.setValue)
        self.actuator_1_dial.valueChanged.connect(self.actuator_1_lcd.display)
        self.actuator_2_dial.valueChanged.connect(self.actuator_2_lcd.display)
        self.actuator_3_dial.valueChanged.connect(self.actuator_3_lcd.display)
        self.actuator_4_dial.valueChanged.connect(self.actuator_4_lcd.display)

        QMetaObject.connectSlotsByName(VRC_PCC)
    # setupUi

    def retranslateUi(self, VRC_PCC):
        VRC_PCC.setWindowTitle(QCoreApplication.translate("VRC_PCC", u"VRC Peripheral Control Computer", None))
        self.actionManual_Control.setText(QCoreApplication.translate("VRC_PCC", u"Manual Control", None))
        self.actionProfile_1.setText(QCoreApplication.translate("VRC_PCC", u"Profile 1", None))
        self.actionProfile_2.setText(QCoreApplication.translate("VRC_PCC", u"Profile 2", None))
        self.actionCOM1.setText(QCoreApplication.translate("VRC_PCC", u"COM1", None))
        self.actionCOM2.setText(QCoreApplication.translate("VRC_PCC", u"COM2", None))
        self.actionCOM3.setText(QCoreApplication.translate("VRC_PCC", u"COM3", None))
        self.actionCOM4.setText(QCoreApplication.translate("VRC_PCC", u"COM4", None))
        self.actionCOM5.setText(QCoreApplication.translate("VRC_PCC", u"COM5", None))
        self.actionCOM6.setText(QCoreApplication.translate("VRC_PCC", u"COM6", None))
        self.actionCOM7.setText(QCoreApplication.translate("VRC_PCC", u"COM7", None))
        self.action115200.setText(QCoreApplication.translate("VRC_PCC", u"115200", None))
        self.actionEnter.setText(QCoreApplication.translate("VRC_PCC", u"Enter...", None))
        self.actionEnter_2.setText(QCoreApplication.translate("VRC_PCC", u"Enter...", None))
        self.actuator_1_label.setText(QCoreApplication.translate("VRC_PCC", u"Actuator 1", None))
        self.actuator_1_toggle.setText(QCoreApplication.translate("VRC_PCC", u"Toggle Open/Close", None))
        self.actuator_2_label.setText(QCoreApplication.translate("VRC_PCC", u"Actuator 2", None))
        self.actuator_2_toggle.setText(QCoreApplication.translate("VRC_PCC", u"Toggle Open/Close", None))
        self.actuator_3_label.setText(QCoreApplication.translate("VRC_PCC", u"Actuator 3", None))
        self.actuator_3_toggle.setText(QCoreApplication.translate("VRC_PCC", u"Toggle Open/Close", None))
        self.actuator_4_label.setText(QCoreApplication.translate("VRC_PCC", u"Actuator 4", None))
        self.actuator_4_toggle.setText(QCoreApplication.translate("VRC_PCC", u"Toggle Open/Close", None))
        self.rgb_strip_label.setText(QCoreApplication.translate("VRC_PCC", u"LED Strip", None))
        self.GL_direction_label_2.setText(QCoreApplication.translate("VRC_PCC", u"Red", None))
        self.GL_direction_label_3.setText(QCoreApplication.translate("VRC_PCC", u"Green", None))
        self.GL_direction_label_4.setText(QCoreApplication.translate("VRC_PCC", u"Blue", None))
        self.Title.setText(QCoreApplication.translate("VRC_PCC", u"VRC PCC Test Tool", None))
    # retranslateUi

