#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from PyQt4 import QtGui
from PyQt4 import QtCore
import json
from guiutil import set_skin
from config import windowsoptions


exitoptions = windowsoptions['exitdialog']


class ExitDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)

        exit_title = exitoptions['exit_title']
        windowicon = exitoptions['windowicon']
        minsize = exitoptions['minsize']
        size = exitoptions['size']
        logo_title = exitoptions['logo_title']
        logo_img_url = exitoptions['logo_img_url']

        self.setWindowTitle(exit_title)
        self.setWindowIcon(QtGui.QIcon(windowicon))  # 设置程序图标
        self.setMinimumSize(minsize[0], minsize[1])
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowMinimizeButtonHint)  # 无边框， 带系统菜单， 可以最小化

        # logo显示
        self.login_logo = QtGui.QWidget()
        login_logo_mainlayout = QtGui.QGridLayout()
        login_bg = QtGui.QLabel(logo_title)
        login_bg.setObjectName('logo_bg')
        login_bg.setAlignment(QtCore.Qt.AlignCenter)
        login_logo_mainlayout.addWidget(login_bg)
        self.login_logo.setLayout(login_logo_mainlayout)
        self.login_bg = logo_img_url
        setbg(self.login_logo, self.login_bg)

        # 退出设置
        self.exitoptwidget = QtGui.QWidget()
        exit_mainlayout = QtGui.QGridLayout()

        self.exitradiogroup = QtGui.QButtonGroup(self.exitoptwidget)
        self.minRadio = QtGui.QRadioButton(u'最小化')
        self.exitRadio = QtGui.QRadioButton(u'退出')
        self.exitsaveRadio = QtGui.QRadioButton(u'退出并保存配置')
        self.exitradiogroup.addButton(self.minRadio)
        self.exitradiogroup.addButton(self.exitRadio)
        self.exitradiogroup.addButton(self.exitsaveRadio)

        exit_mainlayout.addWidget(self.minRadio, 0, 0)
        exit_mainlayout.addWidget(self.exitRadio, 1, 0)
        exit_mainlayout.addWidget(self.exitsaveRadio, 2, 0)
        self.exitoptwidget.setLayout(exit_mainlayout)
        self.exitsaveRadio.setChecked(True)

        # 退出按钮布局
        self.login_lc = QtGui.QWidget()
        self.pbEnter = QtGui.QPushButton(u'确定', self)
        self.pbCancel = QtGui.QPushButton(u'取消', self)
        self.pbEnter.clicked.connect(self.exit)
        self.pbCancel.clicked.connect(self.reject)

        self.login_lc__mainlayout = QtGui.QGridLayout()
        self.login_lc__mainlayout.addWidget(self.pbEnter, 0, 0)
        self.login_lc__mainlayout.addWidget(self.pbCancel, 0, 1)
        self.login_lc.setLayout(self.login_lc__mainlayout)

        mainlayout = QtGui.QVBoxLayout()
        mainlayout.addWidget(self.login_logo)
        mainlayout.addWidget(self.exitoptwidget)
        mainlayout.addWidget(self.login_lc)
        self.setLayout(mainlayout)
        set_skin(self, os.sep.join(['skin', 'qss', 'login.qss']))  # 设置主窗口样式
        self.resize(size[0], size[1])
        self.exitflag = {}

    def exit(self):
        self.accept()  # 关闭对话框并返回1
        for radio in ['minRadio', 'exitRadio', 'exitsaveRadio']:
            if getattr(self, radio) is self.exitradiogroup.checkedButton():
                self.exitflag.update({radio: True})
            else:
                self.exitflag.update({radio: False})

    def resizeEvent(self, event):
        if hasattr(self, 'login_bg'):
            setbg(self.login_logo, self.login_bg)
        else:
            return


def setbg(widget, filename):
    widget.setAutoFillBackground(True)
    palette = QtGui.QPalette()
    pixmap = QtGui.QPixmap(filename)
    pixmap = pixmap.scaled(widget.size())
    palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(pixmap))
    widget.setPalette(palette)


def exit():
    """返回True或False"""
    dialog = ExitDialog()
    if dialog.exec_():
        return dialog.exitflag
    else:
        return dialog.exitflag
