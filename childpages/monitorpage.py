#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from PyQt4 import QtGui
from PyQt4 import QtCore
from basepage import BasePage


class MonitorPage(BasePage):
    def __init__(self, parent=None):
        super(MonitorPage, self).__init__(parent)
        self.parent = parent
        self.setObjectName('MonitorPage')
        self.createContextMenu()

    def createContextMenu(self):
        '''
        创建右键菜单
        '''
        # 必须将ContextMenuPolicy设置为Qt.CustomContextMenu
        # 否则无法使用customContextMenuRequested信号
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        # 创建QMenu
        self.contextMenu = QtGui.QMenu()
        style_QMenu1 = "QMenu {background-color: #ABABAB; border: 1px solid black;}"
        style_QMenu2 = "QMenu::item {background-color: transparent;}"
        style_QMenu3 = "QMenu::item:selected { /* when user selects item using mouse or keyboard */background-color: #654321;}"
        style_QMenu = QtCore.QString(style_QMenu1 + style_QMenu2 + style_QMenu3)
        self.contextMenu.setStyleSheet(style_QMenu)

        self.action_pointnum = self.contextMenu.addAction(u'载入监控地图(Load image)')

        self.action_pointnum.triggered.connect(self.set_monitormap)

    def showContextMenu(self, pos):
        '''
        右键点击时调用的函数
        '''
        # 菜单显示前，将它移动到鼠标点击的位置
        coursePoint = QtGui.QCursor.pos()  # 获取当前光标的位置
        self.contextMenu.move(coursePoint)
        self.contextMenu.show()

    def set_monitormap(self):
        self.openFilesPath = QtCore.QString(os.getcwd() + os.sep + 'images')
        self.filename = QtGui.QFileDialog.getOpenFileName(self,
            "Choose a picture", self.openFilesPath,
            "All Files (*);; Images (*.png *.bmp *.jpg)")
        if self.filename:
            self.setbg(self.filename)
        else:
            return

    def setbg(self, filename):
        self.setAutoFillBackground(True)
        palette = QtGui.QPalette()
        pixmap = QtGui.QPixmap(filename)
        pixmap = pixmap.scaled(self.size())
        palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(pixmap))
        self.setPalette(palette)

    def resizeEvent(self, event):
        if hasattr(self, 'filename'):
            self.setbg(self.filename)
        else:
            return
