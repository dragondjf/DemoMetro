#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from PyQt4 import QtGui
from PyQt4 import QtCore
import json
from guiutil import set_skin
from config import windowsoptions


loginoptions = windowsoptions['login_window']


class LoginDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)

        login_title = loginoptions['login_title']
        windowicon = loginoptions['windowicon']
        minsize = loginoptions['minsize']
        size = loginoptions['size']
        logo_title = loginoptions['logo_title']
        logo_img_url = loginoptions['logo_img_url']

        self.setWindowTitle(login_title)
        self.setWindowIcon(QtGui.QIcon(windowicon))  # 设置程序图标
        self.setMinimumSize(minsize[0], minsize[1])

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowMinimizeButtonHint)  # 无边框， 带系统菜单， 可以最小化

        self.login_logo = QtGui.QWidget()
        login_logo_mainlayout = QtGui.QGridLayout()
        login_bg = QtGui.QLabel(logo_title)
        login_bg.setObjectName('logo_bg')
        login_bg.setAlignment(QtCore.Qt.AlignCenter)
        login_logo_mainlayout.addWidget(login_bg)
        self.login_logo.setLayout(login_logo_mainlayout)
        self.login_bg = logo_img_url
        setbg(self.login_logo, self.login_bg)

        login_np = QtGui.QWidget()
        login_np_mainlayout = QtGui.QGridLayout()
        login_nameLabel = QtGui.QLabel(u'用户名')
        self.login_name = QtGui.QLineEdit(self)
        self.login_name.setPlaceholderText(u'用户名')

        login_passwordLabel = QtGui.QLabel(u'密码')
        self.login_password = QtGui.QLineEdit(self)
        self.login_password.setEchoMode(QtGui.QLineEdit.Password)
        self.login_password.setPlaceholderText(u'密码')

        login_np_mainlayout.addWidget(login_nameLabel, 0, 0)
        login_np_mainlayout.addWidget(self.login_name, 0, 1)
        login_np_mainlayout.addWidget(login_passwordLabel, 1, 0)
        login_np_mainlayout.addWidget(self.login_password, 1, 1)
        login_np.setLayout(login_np_mainlayout)

        # 按钮布局
        login_lc = QtGui.QWidget()
        self.pbLogin = QtGui.QPushButton(u'登录', self)
        self.pbCancel = QtGui.QPushButton(u'取消', self)
        self.pbLogin.clicked.connect(self.login)
        self.pbCancel.clicked.connect(self.reject)

        self.login_lc__mainlayout = QtGui.QGridLayout()
        self.login_lc__mainlayout.addWidget(self.pbLogin, 0, 0)
        self.login_lc__mainlayout.addWidget(self.pbCancel, 0, 1)
        login_lc.setLayout(self.login_lc__mainlayout)

        mainlayout = QtGui.QVBoxLayout()
        mainlayout.addWidget(self.login_logo)
        mainlayout.addWidget(login_np)
        mainlayout.addWidget(login_lc)
        self.setLayout(mainlayout)
        set_skin(self, os.sep.join(['skin', 'qss', 'login.qss']))  # 设置主窗口样式
        self.resize(size[0], size[1])

    def login(self):
        if self.login_name.text() == 'admin' and self.login_password.text() == 'admin':
            self.accept()  # 关闭对话框并返回1
        else:
            QtGui.QMessageBox.critical(self, u'错误', u'用户名密码不匹配')

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


def login():
    """返回True或False"""
    dialog = LoginDialog()
    if dialog.exec_():
        return True
    else:
        return False
