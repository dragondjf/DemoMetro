#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from PyQt4 import QtGui
from PyQt4 import QtCore
import json
from basepage import BasePage
from config import windowsoptions
from guiutil import set_bg, set_skin

monitoroption = windowsoptions['monitorpage']
adddcoptions = windowsoptions['adddcdialog']


class MonitorPage(BasePage):
    def __init__(self, parent=None):
        super(MonitorPage, self).__init__(parent)
        self.parent = parent
        self.setObjectName('MonitorPage')
        self.setAcceptDrops(True)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.createContextMenu()
        self.ips = []
        self.paLabels = windowsoptions['paLabels']
        self.pas = []
        if self.paLabels:
            self.loadPA()
        else:
            self.clearPA()

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
        self.action_addPA = self.contextMenu.addAction(u'增加防区(Add PA)')
        self.action_clearPA = self.contextMenu.addAction(u'清除防区(Clear PA)')

        self.action_pointnum.triggered.connect(self.set_monitormap)
        self.action_addPA.triggered.connect(self.addPA)
        self.action_clearPA.triggered.connect(self.clearPA)

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
            windowsoptions['monitorpage']['backgroundimg'] = unicode(self.filename)
        else:
            return

    def addPA(self):
        flag, beginip, endip, dc_panum = adddc()
        if flag:
            if beginip and endip == '':
                if beginip not in self.ips:
                    self.ips.append(beginip)
            elif beginip and endip:
                ipnum = beginip.split('.')
                baseip = '.'.join(ipnum[0:3])
                for i in range(int(beginip.split('.')[3]), int(endip.split('.')[3]) + 1):
                    ip = baseip + '.' + str(i)
                    if ip not in self.ips:
                        self.ips.append(ip)
        self.createPALabels(self.ips, dc_panum)

    def loadPA(self):
        for ip in self.paLabels:
            pas = self.paLabels[ip]
            for ch in pas:
                pos =  pas[ch]
                pa = DragLabel(str(pos), ip, ch, self)
                pa.move(pos[0], pos[1])
                pa.show()
                self.pas.append(pa)
        self.action_addPA.setEnabled(False)
        self.action_clearPA.setEnabled(True)

    def createPALabels(self, ips=[], dc_panum=2):
        self.clearPA()
        width = self.width()
        height = self.height()
        postions = poscalulator(width, height, 8, 16)
        i = 0
        for ip in ips:
            pa_dc = {}
            for ch in range(dc_panum):
                pa = DragLabel(str(postions[i]), ip, ch, self)
                pa.move(postions[i][0], postions[i][1])
                pa.show()
                pa_dc.update({ch: (pa.pos().x(), pa.pos().y())})
                i = i + 1
                self.pas.append(pa)
            self.paLabels.update({ip: pa_dc})
        windowsoptions['paLabels'] = self.paLabels
        self.action_addPA.setEnabled(False)
        self.action_clearPA.setEnabled(True)

    def clearPA(self):
        if self.pas:
            for item in self.pas:
                item.deleteLater()
        self.pas = []
        self.paLabels = {}
        self.action_addPA.setEnabled(True)
        self.action_clearPA.setEnabled(False)

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
            self.setbg(monitoroption['backgroundimg'])

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            if event.source() in self.children():
                event.setDropAction(QtCore.Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            mime = event.mimeData()
            pieces = mime.text()
            position = event.pos()
            hotSpot = QtCore.QPoint()

            hotSpotPos = mime.data('application/x-hotspot').split(' ')
            if len(hotSpotPos) == 2:
                hotSpot.setX(hotSpotPos[0].toInt()[0])
                hotSpot.setY(hotSpotPos[1].toInt()[0])

            ip = event.source().ip
            ch = event.source().ch

            newLabel = DragLabel(pieces, ip, ch, self)
            newLabel.move(position - hotSpot)
            newLabel.show()

            position += QtCore.QPoint(newLabel.width(), 0)

            self.paLabels[ip][ch] = (newLabel.pos().x(), newLabel.pos().y())
            self.pas.append(newLabel)

            if event.source() in self.children():
                event.setDropAction(QtCore.Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()


def poscalulator(width, height, row, col):
    postions = []
    for i in range(row):
        x = (i + 1) * width / col
        for j in range(col):
            y = (j + 1) * height / row
            postions.append((x, y))
    return postions


class DragLabel(QtGui.QLabel):
    def __init__(self, text, ip, ch, parent):
        super(DragLabel, self).__init__(text, parent)
        self.ip = ip
        self.ch = ch
        set_bg(self)
        self.setAutoFillBackground(True)
        self.setFrameShape(QtGui.QFrame.Panel)
        self.setFrameShadow(QtGui.QFrame.Raised)

    def mousePressEvent(self, event):
        hotSpot = event.pos()

        mimeData = QtCore.QMimeData()
        mimeData.setText(self.text())
        mimeData.setData('application/x-hotspot',
                '%d %d' % (hotSpot.x(), hotSpot.y()))

        pixmap = QtGui.QPixmap(self.size())
        self.render(pixmap)

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        drag.setHotSpot(hotSpot)

        dropAction = drag.exec_(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction, QtCore.Qt.CopyAction)

        if dropAction == QtCore.Qt.MoveAction:
            self.close()
            self.update()


class AddDcDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)

        adddc_title = adddcoptions['adddc_title']
        windowicon = adddcoptions['windowicon']
        minsize = adddcoptions['minsize']
        size = adddcoptions['size']
        logo_title = adddcoptions['logo_title']
        logo_img_url = adddcoptions['logo_img_url']

        self.setWindowTitle(adddc_title)
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
        self.ipwidget = QtGui.QWidget()
        self.ip_mainlayout = QtGui.QGridLayout()
        self.dcLabel = QtGui.QLabel(u'选择采集器类型：')
        self.dctypeCombo = QtGui.QComboBox()
        self.dctypeCombo.addItem(u'I采集器')
        self.dctypeCombo.addItem(u'Q采集器')
        self.dctypeCombo.addItem(u'I区域控制器')

        self.beginipLabel = QtGui.QLabel(u'ip起始地址：')
        self.endipLabel = QtGui.QLabel(u'ip终止地址：')
        self.beginipEdit = QtGui.QLineEdit('192.168.100.4')
        self.beginipEdit.setInputMask('000.000.000.000')
        self.endipEdit = QtGui.QLineEdit('192.168.100.7')
        self.endipEdit.setInputMask('000.000.000.000')

        self.ip_mainlayout.addWidget(self.dcLabel, 0, 0)
        self.ip_mainlayout.addWidget(self.dctypeCombo, 0, 1)
        self.ip_mainlayout.addWidget(self.beginipLabel, 2, 0)
        self.ip_mainlayout.addWidget(self.beginipEdit, 2, 1)
        self.ip_mainlayout.addWidget(self.endipLabel, 3, 0)
        self.ip_mainlayout.addWidget(self.endipEdit, 3, 1)
        self.endipLabel.hide()
        self.endipEdit.hide()

        self.ipwidget.setLayout(self.ip_mainlayout)
        self.dctypeCombo.currentIndexChanged.connect(self.iptypechange)

        # 退出按钮布局
        self.login_lc = QtGui.QWidget()
        self.pbEnter = QtGui.QPushButton(u'确定', self)
        self.pbCancel = QtGui.QPushButton(u'取消', self)
        self.pbEnter.clicked.connect(self.enter)
        self.pbCancel.clicked.connect(self.reject)

        self.login_lc__mainlayout = QtGui.QGridLayout()
        self.login_lc__mainlayout.addWidget(self.pbEnter, 0, 0)
        self.login_lc__mainlayout.addWidget(self.pbCancel, 0, 1)
        self.login_lc.setLayout(self.login_lc__mainlayout)

        mainlayout = QtGui.QVBoxLayout()
        mainlayout.addWidget(self.login_logo)
        mainlayout.addWidget(self.ipwidget)
        mainlayout.addWidget(self.login_lc)
        self.setLayout(mainlayout)
        set_skin(self, os.sep.join(['skin', 'qss', 'login.qss']))  # 设置主窗口样式
        self.resize(size[0], size[1])

        self.beginip = ''
        self.endip = ''
        self.dc_panum = ''

    def iptypechange(self):
        if self.dctypeCombo.currentText() == u'I采集器':
            self.endipLabel.hide()
            self.endipEdit.hide()
        elif self.dctypeCombo.currentText() == u'Q采集器':
            self.endipLabel.hide()
            self.endipEdit.hide()
        elif self.dctypeCombo.currentText() == u'I区域控制器':
            self.endipLabel.show()
            self.endipEdit.show()

    def enter(self):
        self.accept()  # 关闭对话框并返回1
        if self.dctypeCombo.currentText() == u'I采集器':
            self.beginip = str(self.beginipEdit.text())
            self.dc_panum = 2
        elif self.dctypeCombo.currentText() == u'Q采集器':
            self.beginip = str(self.beginipEdit.text())
            self.dc_panum = 4
        elif self.dctypeCombo.currentText() == u'I区域控制器':
            self.beginip = str(self.beginipEdit.text())
            self.endip = str(self.endipEdit.text())
            self.dc_panum = 2

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


def adddc():
    """返回True或False"""
    dialog = AddDcDialog()
    if dialog.exec_():
        return True, dialog.beginip, dialog.endip, dialog.dc_panum
    else:
        return False, dialog.beginip, dialog.endip, dialog.dc_panum
