#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import json
import logging
import urllib2
import base64
import time
from PyQt4 import QtGui
from PyQt4 import QtCore

from basepage import BasePage
from utildialog import msg, urlinput, ipaddressinput
from config import windowsoptions
from guiutil import set_bg, set_skin
from app import StatusListenThreadServer
from login import login

monitoroption = windowsoptions['monitorpage']
adddcoptions = windowsoptions['adddcdialog']
msgoptions = windowsoptions['msgdialog']
urloptions = windowsoptions['urldialog']
webserviceloginoptions = windowsoptions['webseverlogin_window']
ipaddressoptions = windowsoptions['ipaddressdialog']

logger = logging.getLogger(__name__)


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

        self.loadPAmenu = QtGui.QMenu(u'加载防区(Load PA)')
        self.action_loadfromweb = self.loadPAmenu.addAction(u'加载ifpms1.2(Load from 1.2 WebService)')
        self.action_loadfromconfig = self.loadPAmenu.addAction(u'加载配置文件(Load from config file)')
        self.loadPAmenu.setStyleSheet(style_QMenu)

        self.action_pointnum = self.contextMenu.addAction(u'载入监控地图(Load image)')
        self.action_addPA = self.contextMenu.addAction(u'增加防区(Add PA)')
        self.action_loadPA = self.contextMenu.addMenu(self.loadPAmenu)
        self.action_clearPA = self.contextMenu.addAction(u'清除防区(Clear PA)')
        self.action_listenWebService = self.contextMenu.addAction(u'监听(Listen WebService)')

        self.action_pointnum.triggered.connect(self.set_monitormap)
        self.action_addPA.triggered.connect(self.addPAs)
        self.action_loadfromweb.triggered.connect(self.loadPAsfromWeb)
        self.action_loadfromconfig.triggered.connect(self.loadPAsfromconfig)
        self.action_clearPA.triggered.connect(self.clearPAs)
        self.action_listenWebService.triggered.connect(self.listenwebservice)

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

    def loadPAsfromWeb(self):
        self.clearPAs()
        user, password = login(webserviceloginoptions)
        if user == u'ov-orange' and password== u'ov-orange':
            url = urlinput(urloptions)
            f = None
            try:
                req = urllib2.Request(url)
                # logger.info("web get [%s]" % (url))
                auth = "Basic " + base64.urlsafe_b64encode("%s:%s" % (user, password))
                req.add_header("Authorization", auth)
                f = urllib2.urlopen(req)
                palist = json.loads(f.read())
                for pa in palist['protection_areas']:
                    if not pa.has_key('rid'):
                        pa.update({'rid': 0})
                    gno = '%d-%d-%d' % (pa['rid'], pa['did'], pa['pid'])
                    palabel = PALabel(pa['ip'], pa['pid'], pa['did'], pa['rid'], pa['name'], pa['cx'], pa['cy'], self)
                    palabel.status = pa['status']

                    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(pa['status_change_time']))).decode('UTF8')
                    palabel.status_change_time = t             
                    palabel.show()
                    self.palabels.update({gno: palabel})
            except Exception, e:
                logger.error(e)
            finally:
                if f:
                    f.close()

    def loadPAsfromconfig(self):
        try:
            import os
            with open(os.sep.join([os.getcwd(), 'options', 'painfos.json']), 'r') as f:
                self.painfos = json.load(f)
        except Exception, e:
            self.painfos = {}
        self.clearPAs()
        for gno, pa in self.painfos.items():
            palabel = PALabel(pa['ip'], pa['pid'], pa['did'], pa['rid'], pa['name'],pa['x'], pa['y'], self)
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
                    x = postions[i][0]
                    y = postions[i][1]
                    palabel = PALabel(ip, pid, did, rid, 'PA-%s' % gno, x, y, self)
                    palabel.show()
                    self.palabels.update({gno: palabel})
                    i = i + 1
            self.action_addPA.setEnabled(False)
            self.action_loadPA.setEnabled(False)
            self.action_clearPA.setEnabled(True)
        else:
            flag = msg(u'支持的数量上限为128,请输入正确的ip地址范围', msgoptions)
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

    def listenwebservice(self):
        ip, port = ipaddressinput(ipaddressoptions)
        if ip and port:
            self.statuserver = StatusListenThreadServer(ip, port)
            self.statuserver.statuschanged.connect(self.changestatus)
            self.statuserver.start()

    @QtCore.pyqtSlot(dict)
    def changestatus(self, painfo):
        rid = 0
        did = painfo['did']
        pid = painfo['pid']
        rid = painfo['rid']
        status = painfo['status']
        status_change_time = painfo['status_change_time']
        gno = '%d-%d-%d' % (rid, did, pid)
        self.palabels[gno].status = status
        self.palabels[gno].status_change_time = status_change_time
        self.palabels[gno].update()

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
            pos = position - hotSpot
            x = pos.x()
            y = pos.y()
            newLabel = PALabel(ip, pid, did, rid, name, x, y, self)
            # newLabel.move(position - hotSpot)
            newLabel.show()

            position += QtCore.QPoint(newLabel.width(), 0)

            newLabel.x = newLabel.pos().x()
            newLabel.y = newLabel.pos().y()
            newLabel.status = event.source().status
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
        x = (i + 1) * width / (col + 2)
        for j in range(row):
            y = (j + 1) * height / (row + 2)
            postions.append((x, y))
    return postions


class PALabel(QtGui.QLabel):

    status_name = ['Disabled', 'Disconn', 'Connect', 'MinorWarning' , 'Warning', 'Fiberbroken', 'Blast', 'Unnormal']
    ALARM_DELAY_SECS = 5  # 告警状态延迟秒数
    ALARM_REPREAT_INTERVAL_SECS = 2  # 告警持续期间播放声音重复间隔

    STATUS_DISABLE = 0
    STATUS_DISCONN = 1
    STATUS_CONNECT = 2
    STATUS_ALARM_MINOR = 3
    STATUS_ALARM_CRITICAL = 4
    STATUS_ALARM_FIBER_BREAK = 5
    STATUS_ALARM_BLAST = 6
    STATUS_LID_OPEN = 7
    STATUS_LID_CLOSE = 8

    statuscolor = {
        'Disabled': '#ABABAB',
        'Disconn': '#ABABAB',
        'Connect' : 'green',
        'Blast': 'red',
        'Warning': 'red',
        'MinorWarning': 'yellow',
        'Fiberbroken': 'yellow',
        'Unnormal': '#ABABAB'
    }
    status_name_zh = {
        'Disabled': u'禁用',
        'Disconn': u'断开',
        'Connect' : u'运行',
        'Blast': u'爆破',
        'Warning': u'告警',
        'MinorWarning': u'预警',
        'Fiberbroken': u'断纤',
        'Unnormal': u'故障'
    }
    def __init__(self, ip, pid, did, rid, name, x, y, parent):
        super(PALabel, self).__init__(parent)
        self.ip = ip
        self.rid = rid
        self.did = did
        self.pid = pid
        self.gno = '%d-%d-%d' % (rid, did, pid)
        self.name = u"PA-%s" % self.gno
        self.desc = self.name
        self.enable = True
        self.audio_enable = False
        self.x = x
        self.y = y
        self.status = 1
        self.status_change_time = u'1970-08-08: 08:08:08'
        self.latest_change_time = u'1970-08-08: 08:08:08'
        self.alg = {}
        self.setText(self.name)
        set_bg(self)
        self.setAutoFillBackground(True)
        self.setFrameShape(QtGui.QFrame.Panel)
        self.setFrameShadow(QtGui.QFrame.Raised)
        self.setObjectName('palabel')
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.resize(30, 30)

        self.createContextMenu()
        self.setMouseTracking(True)
        self.move(self.x, self.y)

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
        self.action_changestatus = self.contextMenu.addAction(u'改变状态(Change Status)')

        self.action_disable.triggered.connect(self.set_disable)
        self.action_checkwave.triggered.connect(self.checkwave)
        self.action_checkproperty.triggered.connect(self.checkproperty)
        # self.action_changestatus.triggered.connect(self.changestatus)

        # self.timer = QtCore.QTimer(self)
        # self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.changestatus)
        # self.timer.start(200)

    def set_disable(self):
        if unicode(self.action_disable.text()) == u'禁用(Disabled)':
            self.action_disable.setText(u'启用(enabled)')
            self.status = 0
        else:
            self.action_disable.setText(u'禁用(Disabled)')
            self.status = 2
        self.update()

    def checkwave(self):
        pass

    def checkproperty(self):
        self.propertymessage = u'<table> \
                            <tr align="left"><td>防区ip: </td><td>%s</td></tr> \
                            <tr align="left"><td>防区名字:</td><td>%s</td></tr> \
                            <tr align="left"><td>防区状态:</td><td> %s</td></tr> \
                            <tr align="left"><td>防区告警时间:</td><td> %s</td></tr> \
                            <tr align="left"><td>防区上一次状态改变的时间:</td><td> %s</td></tr> \
                            <tr align="left"><td>防区的区域编号:</td><td> %d</td></tr> \
                            <tr align="left"><td>防区的采集器编号:</td><td> %d</td></tr> \
                            <tr align="left"><td>防区的通道编号:</td><td> %d</td></tr> \
                            <tr align="left"><td>防区描述信息:</td><td> %s</td></tr> \
                            <tr align="left"><td>防区位置:</td><td>( %d, %d)</td></tr></table>' % (
                            self.ip,
                            self.name, 
                            self.status_name_zh[self.status_name[self.status]],
                            self.status_change_time,
                            self.latest_change_time,
                            self.rid,
                            self.did,
                            self.pid,
                            self.desc,
                            self.x,
                            self.y
                            )
        msg(self.propertymessage, msgoptions)

    def showContextMenu(self):
        '''
        右键点击时调用的函数
        '''
        # 菜单显示前，将它移动到鼠标点击的位置
        coursePoint = QtGui.QCursor.pos()  # 获取当前光标的位置
        self.contextMenu.move(coursePoint)
        self.contextMenu.show()

    # def changestatus(self):
    #     import random
    #     self.status = random.randrange(0, 7)
    #     self.update()

    def paintEvent(self, event):
        set_bg(self, QtGui.QColor(self.statuscolor[self.status_name[self.status]]))
        self.setText(self.name)

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
            self.tipmessage = u'<table> \
                            <tr align="left"><td>防区ip: </td><td>%s</td></tr> \
                            <tr align="left"><td>防区名字:</td><td>%s</td></tr> \
                            <tr align="left"><td>防区状态:</td><td> %s</td></tr> \
                            <tr align="left"><td>防区告警时间:</td><td> %s</td></tr></table>' % (
                            self.ip,
                            self.name,
                            self.status_name_zh[self.status_name[self.status]],
                            self.status_change_time
                            )
            self.setToolTip(self.tipmessage)


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
