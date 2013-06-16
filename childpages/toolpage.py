#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from PyQt4 import QtGui
from PyQt4 import QtCore
from basepage import BasePage
from guiutil import set_skin


class ToolPage(BasePage):
    def __init__(self, parent=None):
        super(ToolPage, self).__init__(parent)
        self.parent = parent
        self.createButtons()

    def createButtons(self):
        self.ToolButtons = [
            [u'BackGroundColor', u'BackGroundImage'],
            ['ButtonColor', 'ButtonImage'],
        ]
        self.buttontext = {
            'BackGroundColor': u'窗口背景颜色',
            'BackGroundImage': u'窗口背景图片',
            'ButtonColor': u'磁贴背景颜色',
            'ButtonImage': u'磁贴背景图片',
        }
        buttonLayout = QtGui.QGridLayout()
        for buttons in self.ToolButtons:
            for item in buttons:
                button = item + 'Button'
                setattr(self, button, QtGui.QPushButton(self.buttontext[item]))
                getattr(self, button).setObjectName(button)
                getattr(self, button).clicked.connect(getattr(self, 'set_' + item))
                buttonLayout.addWidget(getattr(self, button), self.ToolButtons.index(buttons), buttons.index(item))

        self.setLayout(buttonLayout)
        set_skin(self, os.sep.join(['skin', 'qss', 'MetroToolPage.qss']))

    def set_BackGroundColor(self):
        self.colordialog = QtGui.QColorDialog()
        bgcolor = self.colordialog.getColor()
        style = 'QMainWindow {background : rgb(%s,%s,%s);}' % (bgcolor.red(), bgcolor.green(), bgcolor.blue())
        set_skin(self.parent.parent(), os.sep.join(['skin', 'qss', 'MetroMainwindow.qss']), style)

    def set_BackGroundImage(self):
        self.openFilesPath = QtCore.QString(os.getcwd() + os.sep + 'images')
        filename = QtGui.QFileDialog.getOpenFileName(self,
            "Choose a picture", self.openFilesPath,
            "All Files (*);; Images (*.png *.bmp *.jpg)")
        style = 'QMainWindow {border-image : url(%s);}' % str(QtCore.QDir(QtCore.QDir.currentPath()).relativeFilePath(filename))
        set_skin(self.parent.parent(), os.sep.join(['skin', 'qss', 'MetroMainwindow.qss']), style)

    def set_ButtonColor(self):
        self.colordialog = QtGui.QColorDialog()
        bgcolor = self.colordialog.getColor()
        style = 'QPushButton {background : rgb(%s,%s,%s);}' % (bgcolor.red(), bgcolor.green(), bgcolor.blue())
        set_skin(self.parent, os.sep.join(['skin', 'qss', 'MetroNavigationPage.qss']), style)
        set_skin(self, os.sep.join(['skin', 'qss', 'MetroToolBar.qss']), style)

    def set_ButtonImage(self):
        self.openFilesPath = QtCore.QString(os.getcwd() + os.sep + 'images')
        filename = QtGui.QFileDialog.getOpenFileName(self,
            "Choose a picture", self.openFilesPath,
            "All Files (*);; Images (*.png *.bmp *.jpg)")
        style = 'QPushButton {border-image : url(%s);}' % str(QtCore.QDir(QtCore.QDir.currentPath()).relativeFilePath(filename))
        set_skin(self.parent, os.sep.join(['skin', 'qss', 'MetroNavigationPage.qss']), style)
