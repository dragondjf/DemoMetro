#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import json
from PyQt4 import QtGui
from PyQt4 import QtCore

from basepage import BasePage
from utildialog import msg
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
        self.palabels = {}
        # if self.paLabels:
        #     self.loadPA()
        # else:
        #     self.clearPA()

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
        self.action_loadPA = self.contextMenu.addAction(u'加载防区(Load PA)')
        self.action_clearPA = self.contextMenu.addAction(u'清除防区(Clear PA)')

        self.action_pointnum.triggered.connect(self.set_monitormap)
        self.action_addPA.triggered.connect(self.addPAs)
        self.action_loadPA.triggered.connect(self.loadPAs)
        self.action_clearPA.triggered.connect(self.clearPAs)

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

    def addPAs(self):
        self.clearPAs()
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
        self.createpalabels(self.ips, dc_panum)

    def loadPAs(self):
        try:
            import os
            with open(os.sep.join([os.getcwd(), 'options', 'painfos.json']), 'r') as f:
                self.painfos = json.load(f)
        except Exception, e:
            self.painfos = {}
        self.clearPAs()
        for gno, pa in self.painfos.items():
            palabel = PALabel(pa['ip'], pa['pid'], pa['did'], pa['rid'], pa['name'], self)
            palabel.move(pa['x'], pa['y'])
            palabel.show()
            self.palabels.update({gno: palabel})
        self.action_addPA.setEnabled(False)
        self.action_loadPA.setEnabled(False)
        self.action_clearPA.setEnabled(True)

    def createpalabels(self, ips, dc_panum):
        width = self.width()
        height = self.height()
        postions = poscalulator(width, height, 8, 16)
        if len(ips) * dc_panum <= windowsoptions['maxpanum']:
            i = 0
            rid = 0
            for ip in ips:
                did = ips.index(ip) + 1
                for pid in range(int(dc_panum)):
                    pid = pid + 1
                    gno = '%d-%d-%d' % (rid, did, pid)
                    palabel = PALabel(ip, pid, did, rid, 'PA-%s' % gno, self)
                    palabel.move(postions[i][0], postions[i][1])
                    palabel.x = postions[i][0]
                    palabel.y = postions[i][1]
                    palabel.show()
                    self.palabels.update({gno: palabel})
                    i = i + 1
            self.action_addPA.setEnabled(False)
            self.action_loadPA.setEnabled(False)
            self.action_clearPA.setEnabled(True)
        else:
            flag = msg(u'支持的数量上限为128,请输入正确的ip地址范围')
            if flag:
                self.addPAs()

    def clearPAs(self):
        if self.palabels:
            for gno, palabel in self.palabels.items():
                palabel.deleteLater()
        self.ips = []
        self.palabels = {}
        self.action_addPA.setEnabled(True)
        self.action_loadPA.setEnabled(True)
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
            pid = event.source().pid
            did = event.source().did
            rid = event.source().rid
            name = event.source().name
            gno = '%d-%d-%d' % (rid, did, pid)

            newLabel = PALabel(ip, pid, did, rid, name, self)
            newLabel.move(position - hotSpot)
            newLabel.show()

            position += QtCore.QPoint(newLabel.width(), 0)

            newLabel.x = newLabel.pos().x()
            newLabel.y = newLabel.pos().y()
            self.palabels.update({gno: newLabel})

            if event.source() in self.children():
                event.setDropAction(QtCore.Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()


def poscalulator(width, height, row, col):
    postions = []
    for i in range(col):
        x = (i + 1) * width / (col + 1)
        for j in range(row):
            y = (j + 1) * height / (row + 1)
            postions.append((x, y))
    return postions


class PALabel(QtGui.QLabel):
    def __init__(self, ip, pid, did, rid, name, parent):
        super(PALabel, self).__init__(parent)
        self.ip = ip
        self.rid = rid
        self.did = did
        self.pid = pid
        self.gno = '%d-%d-%d' % (rid, did, pid)
        self.name = u"PA-%s" % self.gno
        self.desc = u""
        self.enable = True
        self.audio_enable = False
        self.x = 0
        self.y = 0
        self.status = 1
        self.latest_change_time = 0
        self.alg = {}
        self.setText(self.name)
        set_bg(self)
        self.setAutoFillBackground(True)
        self.setFrameShape(QtGui.QFrame.Panel)
        self.setFrameShadow(QtGui.QFrame.Raised)
        self.setObjectName('palabel')
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.resize(self.width(), 40)

        self.createContextMenu()
        self.setMouseTracking(True)

    def createContextMenu(self):
        '''
        创建右键菜单
        '''
        # 必须将ContextMenuPolicy设置为Qt.CustomContextMenu
        # 否则无法使用customContextMenuRequested信号
        # self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.showContextMenu)

        # 创建QMenu
        self.contextMenu = QtGui.QMenu()
        style_QMenu1 = "QMenu {background-color: #ABABAB; border: 1px solid black;}"
        style_QMenu2 = "QMenu::item {background-color: transparent;}"
        style_QMenu3 = "QMenu::item:selected { /* when user selects item using mouse or keyboard */background-color: #654321;}"
        style_QMenu = QtCore.QString(style_QMenu1 + style_QMenu2 + style_QMenu3)
        self.contextMenu.setStyleSheet(style_QMenu)

        self.action_disable = self.contextMenu.addAction(u'禁用(Disabled)')
        self.action_checkwave = self.contextMenu.addAction(u'查看波形(Check Wave)')
        self.action_checkproperty = self.contextMenu.addAction(u'属性(Property)')

        self.action_disable.triggered.connect(self.set_disable)
        self.action_checkwave.triggered.connect(self.checkwave)
        self.action_checkproperty.triggered.connect(self.checkproperty)

    def set_disable(self):
        if unicode(self.action_disable.text()) == u'禁用(Disabled)':
            self.action_disable.setText(u'启用(enabled)')
            set_bg(self, QtGui.QColor('#ABABAB'))
        else:
            self.action_disable.setText(u'禁用(Disabled)')
            set_bg(self, QtGui.QColor('green'))
        self.update()

    def checkwave(self):
        pass

    def checkproperty(self):
        pass

    def showContextMenu(self):
        '''
        右键点击时调用的函数
        '''
        # 菜单显示前，将它移动到鼠标点击的位置
        coursePoint = QtGui.QCursor.pos()  # 获取当前光标的位置
        self.contextMenu.move(coursePoint)
        self.contextMenu.show()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
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

        if event.button() == QtCore.Qt.RightButton:
            self.showContextMenu()

    def mouseMoveEvent(self, event):
        if event.pos() in self.rect():
            self.setToolTip(self.gno)

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
