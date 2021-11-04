# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'startup_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.0.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_VRC_startup(object):
    def setupUi(self, VRC_startup):
        if not VRC_startup.objectName():
            VRC_startup.setObjectName(u"VRC_startup")
        VRC_startup.resize(234, 210)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(VRC_startup.sizePolicy().hasHeightForWidth())
        VRC_startup.setSizePolicy(sizePolicy)
        VRC_startup.setMinimumSize(QSize(234, 210))
        VRC_startup.setMaximumSize(QSize(234, 210))
        VRC_startup.setStyleSheet(u"background-color: rgb(121, 121, 121);")
        self.formLayout = QFormLayout(VRC_startup)
        self.formLayout.setObjectName(u"formLayout")
        self.Title = QLabel(VRC_startup)
        self.Title.setObjectName(u"Title")
        font = QFont()
        font.setFamily(u"Arial Black")
        font.setPointSize(14)
        font.setBold(False)
        font.setItalic(False)
        self.Title.setFont(font)
        self.Title.setStyleSheet(u"font: 87 14pt \"Arial Black\";\n"
"background-color: rgba(86, 81, 100, 200);\n"
"color: rgb(255, 255, 255);\n"
"border-radius: 3px;\n"
"border: 2px solid rgb(27, 29, 35);\n"
"padding-left: 5px;")
        self.Title.setAlignment(Qt.AlignCenter)

        self.formLayout.setWidget(0, QFormLayout.SpanningRole, self.Title)

        self.COM_Port_Label = QLabel(VRC_startup)
        self.COM_Port_Label.setObjectName(u"COM_Port_Label")
        self.COM_Port_Label.setStyleSheet(u"font: 87 12pt \"Arial Black\";\n"
"color: rgb(255, 255, 255);\n"
"padding-left: 3px;\n"
"")

        self.formLayout.setWidget(1, QFormLayout.SpanningRole, self.COM_Port_Label)

        self.COM_Port_comboBox = QComboBox(VRC_startup)
        self.COM_Port_comboBox.setObjectName(u"COM_Port_comboBox")
        self.COM_Port_comboBox.setStyleSheet(u"font: 12pt \"Arial Narrow\";\n"
"background-color: rgb(235, 235, 235);")
        self.COM_Port_comboBox.setMaxCount(10)

        self.formLayout.setWidget(2, QFormLayout.SpanningRole, self.COM_Port_comboBox)

        self.Baud_Rate_Label = QLabel(VRC_startup)
        self.Baud_Rate_Label.setObjectName(u"Baud_Rate_Label")
        self.Baud_Rate_Label.setStyleSheet(u"font: 87 12pt \"Arial Black\";\n"
"color: rgb(255, 255, 255);\n"
"padding-left: 3px;\n"
"")

        self.formLayout.setWidget(3, QFormLayout.SpanningRole, self.Baud_Rate_Label)

        self.Baud_Rate_comboBox = QComboBox(VRC_startup)
        self.Baud_Rate_comboBox.addItem("")
        self.Baud_Rate_comboBox.setObjectName(u"Baud_Rate_comboBox")
        self.Baud_Rate_comboBox.setAutoFillBackground(False)
        self.Baud_Rate_comboBox.setStyleSheet(u"font: 12pt \"Arial Narrow\";\n"
"background-color: rgb(235, 235, 235);")
        self.Baud_Rate_comboBox.setMaxCount(10)

        self.formLayout.setWidget(4, QFormLayout.SpanningRole, self.Baud_Rate_comboBox)

        self.Connect_Button = QPushButton(VRC_startup)
        self.Connect_Button.setObjectName(u"Connect_Button")
        self.Connect_Button.setMinimumSize(QSize(0, 35))
        self.Connect_Button.setAutoFillBackground(False)
        self.Connect_Button.setStyleSheet(u"font: 87 12pt \"Arial Black\";\n"
"background-color: rgb(255, 85, 0);\n"
"border-radius: 5px;\n"
"padding-left: 5px;\n"
"")
        self.Connect_Button.setCheckable(True)

        self.formLayout.setWidget(5, QFormLayout.SpanningRole, self.Connect_Button)


        self.retranslateUi(VRC_startup)

        QMetaObject.connectSlotsByName(VRC_startup)
    # setupUi

    def retranslateUi(self, VRC_startup):
        VRC_startup.setWindowTitle(QCoreApplication.translate("VRC_startup", u"Form", None))
        self.Title.setText(QCoreApplication.translate("VRC_startup", u"VRC PCC Test Tool", None))
        self.COM_Port_Label.setText(QCoreApplication.translate("VRC_startup", u"COM Port", None))
        self.COM_Port_comboBox.setCurrentText("")
        self.Baud_Rate_Label.setText(QCoreApplication.translate("VRC_startup", u"Baud Rate", None))
        self.Baud_Rate_comboBox.setItemText(0, QCoreApplication.translate("VRC_startup", u"115200", None))

        self.Baud_Rate_comboBox.setCurrentText(QCoreApplication.translate("VRC_startup", u"115200", None))
        self.Connect_Button.setText(QCoreApplication.translate("VRC_startup", u"Connect!", None))
    # retranslateUi

