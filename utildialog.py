#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from PyQt4 import QtGui
from PyQt4 import QtCore
import json
from guiutil import set_skin
from config import windowsoptions


exitoptions = windowsoptions['exitdialog']
msgoptions = windowsoptions['msgdialog']


class MessageDialog(QtGui.QDialog):
    def __init__(self, text, options, parent=None):
        QtGui.QDialog.__init__(self, parent)

        msg_title = options['msg_title']
        windowicon = options['windowicon']
        minsize = options['minsize']
        size = options['size']
        logo_title = options['logo_title']
        logo_img_url = options['logo_img_url']

        self.setWindowTitle(msg_title)
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

        # message内容提示
        self.msglabel = QtGui.QLabel(text)
        # self.msglabel.setAlignment(QtCore.Qt.AlignCenter)
        # 退出按钮布局
        self.login_lc = QtGui.QWidget()
        self.pbEnter = QtGui.QPushButton(u'确定', self)
        self.pbEnter.clicked.connect(self.enter)
        self.login_lc__mainlayout = QtGui.QGridLayout()
        self.login_lc__mainlayout.addWidget(self.pbEnter, 0, 0)
        # self.login_lc__mainlayout.addWidget(self.pbCancel, 0, 1)
        self.login_lc.setLayout(self.login_lc__mainlayout)

        mainlayout = QtGui.QVBoxLayout()
        mainlayout.addWidget(self.login_logo)
        mainlayout.addWidget(self.msglabel)
        mainlayout.addWidget(self.login_lc)
        self.setLayout(mainlayout)
        set_skin(self, os.sep.join(['skin', 'qss', 'login.qss']))  # 设置主窗口样式
        self.resize(size[0], size[1])
        self.msgflag = {}

    def enter(self):
        self.accept()  # 关闭对话框并返回1

    def resizeEvent(self, event):
        if hasattr(self, 'login_bg'):
            setbg(self.login_logo, self.login_bg)
        else:
            return


class UrlDialog(QtGui.QDialog):
    def __init__(self, options, parent=None):
        QtGui.QDialog.__init__(self, parent)

        url_title = options['url_title']
        windowicon = options['windowicon']
        minsize = options['minsize']
        size = options['size']
        logo_title = options['logo_title']
        logo_img_url = options['logo_img_url']

        self.setWindowTitle(url_title)
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

        # url内容输入
        self.urlwidget = QtGui.QWidget()
        url_mainlayout = QtGui.QGridLayout()
        self.urlLabel = QtGui.QLabel(u'输入需要访问的url:')
        self.urlLineEdit = QtGui.QLineEdit(u'http://192.168.10.135:8000/webs/protection_areas/list')
        url_mainlayout.addWidget(self.urlLabel, 0, 0)
        url_mainlayout.addWidget(self.urlLineEdit, 1, 0)
        self.urlwidget.setLayout(url_mainlayout)

        # 退出按钮布局
        self.login_lc = QtGui.QWidget()
        self.pbEnter = QtGui.QPushButton(u'确定', self)
        self.pbEnter.clicked.connect(self.enter)
        self.login_lc__mainlayout = QtGui.QGridLayout()
        self.login_lc__mainlayout.addWidget(self.pbEnter, 0, 0)
        # self.login_lc__mainlayout.addWidget(self.pbCancel, 0, 1)
        self.login_lc.setLayout(self.login_lc__mainlayout)

        mainlayout = QtGui.QVBoxLayout()
        mainlayout.addWidget(self.login_logo)
        mainlayout.addWidget(self.urlwidget)
        mainlayout.addWidget(self.login_lc)
        self.setLayout(mainlayout)
        set_skin(self, os.sep.join(['skin', 'qss', 'login.qss']))  # 设置主窗口样式
        self.resize(size[0], size[1])
        self.msgflag = {}

    def enter(self):
        self.accept()  # 关闭对话框并返回1

    def resizeEvent(self, event):
        if hasattr(self, 'login_bg'):
            setbg(self.login_logo, self.login_bg)
        else:
            return


class IPaddressDialog(QtGui.QDialog):
    def __init__(self, options, parent=None):
        QtGui.QDialog.__init__(self, parent)

        ipaddress_title = options['ipaddress_title']
        windowicon = options['windowicon']
        minsize = options['minsize']
        size = options['size']
        logo_title = options['logo_title']
        logo_img_url = options['logo_img_url']

        self.setWindowTitle(ipaddress_title)
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

        # url内容输入
        self.urlwidget = QtGui.QWidget()
        ip_mainlayout = QtGui.QGridLayout()
        self.ipLabel = QtGui.QLabel(u'输入主机ip:')
        self.ipLineEdit = QtGui.QLineEdit(u'')
        self.ipLineEdit.setInputMask('000.000.000.000')
        self.portLabel = QtGui.QLabel(u'输入主机port:')
        self.portLineEdit = QtGui.QLineEdit(u'8000')
        ip_mainlayout.addWidget(self.ipLabel, 0, 0)
        ip_mainlayout.addWidget(self.ipLineEdit, 0, 1)
        ip_mainlayout.addWidget(self.portLabel, 1, 0)
        ip_mainlayout.addWidget(self.portLineEdit, 1, 1)

        self.urlwidget.setLayout(ip_mainlayout)

        # 退出按钮布局
        self.login_lc = QtGui.QWidget()
        self.pbEnter = QtGui.QPushButton(u'确定', self)
        self.pbEnter.clicked.connect(self.enter)
        self.login_lc__mainlayout = QtGui.QGridLayout()
        self.login_lc__mainlayout.addWidget(self.pbEnter, 0, 0)
        # self.login_lc__mainlayout.addWidget(self.pbCancel, 0, 1)
        self.login_lc.setLayout(self.login_lc__mainlayout)

        mainlayout = QtGui.QVBoxLayout()
        mainlayout.addWidget(self.login_logo)
        mainlayout.addWidget(self.urlwidget)
        mainlayout.addWidget(self.login_lc)
        self.setLayout(mainlayout)
        set_skin(self, os.sep.join(['skin', 'qss', 'login.qss']))  # 设置主窗口样式
        self.resize(size[0], size[1])
        self.msgflag = {}

    def enter(self):
        self.accept()  # 关闭对话框并返回1

    def resizeEvent(self, event):
        if hasattr(self, 'login_bg'):
            setbg(self.login_logo, self.login_bg)
        else:
            return


class ExitDialog(QtGui.QDialog):
    def __init__(self, options, parent=None):
        QtGui.QDialog.__init__(self, parent)

        exit_title = options['exit_title']
        windowicon = options['windowicon']
        minsize = options['minsize']
        size = options['size']
        logo_title = options['logo_title']
        logo_img_url = options['logo_img_url']

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
        self.pbCancel.clicked.connect(self.close)

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
        for radio in ['minRadio', 'exitRadio', 'exitsaveRadio']:
            if getattr(self, radio) is self.exitradiogroup.checkedButton():
                self.exitflag.update({radio: True})
            else:
                self.exitflag.update({radio: False})
        self.accept()

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


def exit(options):
    """返回True或False"""
    dialog = ExitDialog(options)
    if dialog.exec_():
        return dialog.exitflag
    else:
        return dialog.exitflag


def msg(text, options):
    """返回True或False"""
    dialog = MessageDialog(text, options)
    dialog.msglabel.setAlignment(QtCore.Qt.AlignCenter)
    if dialog.exec_():
        return True
    else:
        return False


def urlinput(options):
    dialog = UrlDialog(options)
    if dialog.exec_():
        return unicode(dialog.urlLineEdit.text())


def ipaddressinput(options):
    dialog = IPaddressDialog(options)
    if dialog.exec_():
        return unicode(dialog.ipLineEdit.text()), int(dialog.portLineEdit.text())
