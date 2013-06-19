#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from PyQt4 import QtGui
from PyQt4 import QtCore
import json

from config import windowsoptions
from login import login
from effects import *
from childpages import *
from guiutil import set_skin, set_bg
import utildialog


#主日志保存在log/ifpms.log
logging.root.setLevel(logging.INFO)
logging.root.propagate = 0
loghandler = RotatingFileHandler(os.path.join("log", "config.log"), maxBytes=10 * 1024 * 1024, backupCount=100)
loghandler.setFormatter(logging.Formatter('%(asctime)s %(levelname)8s [%(filename)16s:%(lineno)04s] %(message)s'))
loghandler.level = logging.INFO
logging.root.addHandler(loghandler)
logger = logging.root
logger.propagate = 0


class MetroWindow(QtGui.QWidget):

    def __init__(self, parent=None):
        super(MetroWindow, self).__init__(parent)

        self.page_tag = windowsoptions['mainwindow']['centralwindow']['page_tag']
        self.page_tag_zh = windowsoptions['mainwindow']['centralwindow']['page_tag_zh']
        self.initUI()

    def initUI(self):

        self.pagecount = len(self.page_tag_zh)
        self.createMetroButton()

        self.pages = QtGui.QStackedWidget()

        self.pages.addWidget(self.navigationPage)

        self.createChildPages()

        self.createConnections()
        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(self.pages)
        self.setLayout(mainLayout)

        self.faderWidget = None
        self.connect(self.pages, QtCore.SIGNAL("currentChanged(int)"), self.fadeInWidget)  # 页面切换时淡入淡出效果
        self.layout().setContentsMargins(0, 0, 0, 0)

    def createMetroButton(self):
        self.navigationPage = NavigationPage()
        buttonLayout = QtGui.QGridLayout()
        buttonLayout.setHorizontalSpacing(10)   # 设置和横向间隔像素
        buttonLayout.setVerticalSpacing(10)    # 设置纵向间隔像素
        for buttons in self.page_tag:
            for item in buttons:
                button = item + 'Button'
                setattr(self, button, QtGui.QPushButton(self.page_tag_zh[item]))
                getattr(self, button).setObjectName(button)
                buttonLayout.addWidget(getattr(self, button), self.page_tag.index(buttons), buttons.index(item))

        self.buttonLayout = buttonLayout

        self.navigationPage.setLayout(buttonLayout)

    def createChildPages(self):
        for buttons in self.page_tag:
            for item in buttons:
                page = item + 'Page'
                childpage = 'child' + page
                if hasattr(sys.modules[__name__], page):
                    setattr(self, page, getattr(sys.modules[__name__], page)(self))
                else:
                    setattr(self, page, getattr(sys.modules[__name__], 'BasePage')(self))

                setattr(self, childpage, ChildPage(self, getattr(self, page)))
                self.pages.addWidget(getattr(self, childpage))

    def createConnections(self):
        for buttons in self.page_tag:
            for item in buttons:
                button = item + 'Button'
                getattr(self, button).clicked.connect(self.childpageChange)

    def childpageChange(self):
        currentpage = getattr(self, unicode('child' + self.sender().objectName()[:-6]) + 'Page')
        if currentpage is self.navigationPage:
            currentpage.parent.parent().statusBar().hide()
        else:
            currentpage.parent.parent().statusBar().show()
        self.pages.setCurrentWidget(currentpage)

    @QtCore.pyqtSlot()
    def backnavigationPage(self):
        self.parent().statusBar().hide()
        self.pages.setCurrentWidget(self.navigationPage)

    @QtCore.pyqtSlot()
    def backPage(self):
        index = self.pages.currentIndex()
        if index == 1:
            self.parent().statusBar().hide()
            self.pages.setCurrentWidget(self.navigationPage)
        else:
            self.pages.setCurrentIndex(index - 1)

    @QtCore.pyqtSlot()
    def forwardnextPage(self):
        index = self.pages.currentIndex()
        if index < self.pagecount:
            self.pages.setCurrentIndex(index + 1)
        else:
            self.parent().statusBar().hide()
            self.pages.setCurrentWidget(self.navigationPage)

    def fadeInWidget(self, index):
        '''
            页面切换时槽函数实现淡入淡出效果
        '''
        self.faderWidget = FaderWidget(self.pages.widget(index))
        self.faderWidget.start()


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        title = windowsoptions['mainwindow']['title']
        postion = windowsoptions['mainwindow']['postion']
        minsize = windowsoptions['mainwindow']['minsize']
        size = windowsoptions['mainwindow']['size']
        windowicon = windowsoptions['mainwindow']['windowicon']
        fullscreenflag = windowsoptions['mainwindow']['fullscreenflag']
        statusbar_options = windowsoptions['mainwindow']['statusbar']

        self.setWindowIcon(QtGui.QIcon(windowicon))  # 设置程序图标
        width = QtGui.QDesktopWidget().availableGeometry().width() * 4 / 5
        height = QtGui.QDesktopWidget().availableGeometry().height() * 7 / 8
        self.setGeometry(postion[0], postion[1], width, height)  # 初始化窗口位置和大小
        self.center()  # 将窗口固定在屏幕中间
        self.setMinimumSize(minsize[0], minsize[1])
        self.setWindowTitle(title)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.fullscreenflag = fullscreenflag  # 初始化时非窗口最大话标志
        self.navigation_flag = True   # 导航标志，初始化时显示导航
        self.layout().setContentsMargins(0, 0, 0, 0)

        # self.setWindowFlags(QtCore.Qt.CustomizeWindowHint)  # 隐藏标题栏， 可以拖动边框改变大小
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # 隐藏标题栏， 无法改变大小
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowMinimizeButtonHint)  # 无边框， 带系统菜单， 可以最小化
        # self.setMouseTracking(True)

        self.centeralwindow = MetroWindow(self)
        self.setCentralWidget(self.centeralwindow)

        self.statusbar = QtGui.QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage(statusbar_options['initmessage'])
        self.statusbar.setMinimumHeight(statusbar_options['minimumHeight'])
        self.statusbar.setVisible(statusbar_options['visual'])

        self.setskin()
        if self.fullscreenflag:
            self.showFullScreen()
        else:
            self.showNormal()

    def setskin(self):
        set_skin(self.centeralwindow, os.sep.join(['skin', 'qss', 'MetroNavigationPage.qss']))  # 设置导航页面样式

        for buttons in windowsoptions['mainwindow']['centralwindow']['page_tag']:
            for item in buttons:
                childpage = getattr(self.centeralwindow, 'child' + item + 'Page')
                set_skin(childpage, os.sep.join(['skin', 'qss', 'MetroNavigationBar.qss']))   # 设置导航工具条的样式

        set_skin(self, os.sep.join(['skin', 'qss', 'MetroMainwindow.qss']))  # 设置主窗口样式

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    @QtCore.pyqtSlot()
    def windowMaxNormal(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def closeEvent(self, evt):
        exitflag = utildialog.exit()
        for item in exitflag:
            if item == 'minRadio' and exitflag[item]:
                self.showMinimized()
                evt.ignore()
            elif item == 'exitRadio' and exitflag[item]:
                evt.accept()
            elif item == 'exitsaveRadio' and exitflag[item]:
                evt.accept()
                options = windowsoptions
                options['mainwindow']['fullscreenflag'] = self.isFullScreen()
                painfos = {}
                for gno, palabel in getattr(self.centeralwindow, 'MonitorPage').palabels.items():
                    pa = {
                        'ip': palabel.ip,
                        'pid': palabel.pid,
                        'did': palabel.did,
                        'rid': palabel.rid,
                        'name': palabel.name,
                        'x': palabel.x,
                        'y': palabel.y,
                    }
                    painfos.update({gno: pa})
                with open(os.sep.join([os.getcwd(), 'options', 'windowsoptions.json']), 'wb') as f:
                    # f.write(json.dumps(options, indent=1))
                    json.dump(options, f, indent=1)
                with open(os.sep.join([os.getcwd(), 'options', 'painfos.json']), 'wb') as f:
                    # f.write(json.dumps(painfos, indent=1))
                    json.dump(painfos, f, indent=1)

    def keyPressEvent(self, evt):
        if evt.key() == QtCore.Qt.Key_Escape:
            self.close()
        elif evt.key() == QtCore.Qt.Key_F11:
            if not self.fullscreenflag:
                self.showFullScreen()
                self.fullscreenflag = True
            else:
                self.showNormal()
                self.fullscreenflag = False
        elif evt.key() == QtCore.Qt.Key_F10:
            currentpage = self.centralWidget().pages.currentWidget()
            if hasattr(currentpage, 'navigation'):
                if self.navigation_flag:
                    currentpage.navigation.setVisible(False)
                    self.navigation_flag = False
                else:
                    currentpage.navigation.setVisible(True)
                    self.navigation_flag = True
        elif evt.key() == QtCore.Qt.Key_Return:
            if isinstance(self.focusWidget(), QtGui.QPushButton):
                self.focusWidget().click()


def main():
    app = QtGui.QApplication(sys.argv)
    if login():
        splash = QtGui.QSplashScreen(QtGui.QPixmap(windowsoptions['splashimg']))
        splash.show()
        app.processEvents()
        main = MainWindow()
        main.show()
        splash.finish(main)
        sys.exit(app.exec_())

if __name__ == '__main__':
    main()
