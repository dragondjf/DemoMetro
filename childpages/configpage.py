#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import logging
import time
from PyQt4 import QtGui
from PyQt4 import QtCore
from effects import FaderWidget
from basepage import BasePage
from ping import ping
import udpcmd


logger = logging.getLogger(__name__)


code = {
        'baseinfo': 0x01,   # 产品固化信息
        'comminfo': 0x02,   # 通信控制信息
        'samplingctrlinfo': 0x04,  # 采样控制信息
        'channelctrlinfo': 0x06,  # 通道控制信息
        'devicefunctioninfo': 0x08  # 设备功能控制信息
    }

code_zh = {
        'baseinfo': u'产品固化信息',
        'comminfo': u'通信控制信息',
        'samplingctrlinfo': u'采样控制信息',
        'channelctrlinfo': u'通道控制信息',
        'devicefunctioninfo': u'设备功能控制信息'
}

code_flag = {
        'baseinfo': False,
        'comminfo': False,
        'samplingctrlinfo': False,
        'channelctrlinfo': False,
        'devicefunctioninfo': False
}

code_result = {
        'baseinfo': '',
        'comminfo': '',
        'samplingctrlinfo': '',
        'channelctrlinfo': '',
        'devicefunctioninfo': ''
}


commondinfo = ['baseinfo', 'comminfo', 'samplingctrlinfo', 'channelctrlinfo', 'devicefunctioninfo']


class ConfigPage(BasePage):
    def __init__(self, parent=None):
        super(ConfigPage, self).__init__(parent)
        self.parent = parent
        self.ver = 2
        self.initipGrounp()
        self.initTabWidget()

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.ipGroup)
        mainLayout.addWidget(self.tabs)
        mainLayout.addSpacing(12)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)
        self.mainLayout = mainLayout

    def initipGrounp(self):
        ipGroup = QtGui.QGroupBox(u"IP 查询")

        ipLabel = QtGui.QLabel(u'输入采集器的IP：')
        self.ipEdit = QtGui.QLineEdit('192.168.100.79')
        self.ipEdit.setInputMask('000.000.000.000')
        self.ipokbutton = QtGui.QPushButton('')

        udpportLabel = QtGui.QLabel(u'默认UDP端口：')
        self.udpportEdit = QtGui.QLineEdit('6004')

        self.v2Radio = QtGui.QRadioButton(u'V2.0')
        self.VqRadio = QtGui.QRadioButton(u'V-Q')

        ipcheckButton = QtGui.QPushButton(u'查询')
        ipcheckButton.clicked.connect(self.ipcheck)

        ipLayout = QtGui.QGridLayout()
        ipLayout.addWidget(ipLabel, 0, 0)
        ipLayout.addWidget(self.ipEdit, 0, 1)
        ipLayout.addWidget(self.ipokbutton, 0, 2)

        ipLayout.addWidget(udpportLabel, 1, 0)
        ipLayout.addWidget(self.udpportEdit, 1, 1)

        ipLayout.addWidget(self.v2Radio, 2, 0)
        ipLayout.addWidget(self.VqRadio, 2, 1)

        ipLayout.addWidget(ipcheckButton, 3, 2)

        ipGroup.setLayout(ipLayout)

        self.ipGroup = ipGroup

    def initTabWidget(self):
        self.tabs = QtGui.QTabWidget(self)
        self.tabs.setTabPosition(QtGui.QTabWidget.North)
        self.tabs.setMovable(True)
        self.tabs.hide()
        for key in commondinfo:
            self.tabs.addTab(getattr(sys.modules[__name__], key.capitalize() + 'Page')(self), code_zh[key])

        self.connect(self.tabs, QtCore.SIGNAL("currentChanged(int)"), self.fadeInWidget)  # 页面切换时淡入淡出效果

    def ipcheck(self):
        ip = unicode(self.ipEdit.text())
        ping_flag, ping_result = ping(ip)
        if ping_flag:
            self.ipokbutton.setText(u'连接正常')
            self.tabs.show()
        else:
            self.ipokbutton.setText(u'连接错误')
            self.tabs.hide()
        mainwindow = self.parent.parent()
        mainwindow.statusBar().showMessage(ping_result)


        if self.v2Radio.isChecked():
            self.ver = 2
        elif self.VqRadio.isChecked():
            self.ver = 3

    def fadeInWidget(self, index):
        '''
            页面切换时槽函数实现淡入淡出效果
        '''
        self.faderWidget = FaderWidget(self.tabs.widget(index))
        self.faderWidget.start()


class BaseinfoPage(QtGui.QWidget):

    key = 'baseinfo'

    baseinfo_zh = {
        'mac': u'MAC地址',
        'hwcode': u'硬件型号',
        'hw_version': u'硬件版本',
        'sw_version': u'软件版本',
        'proto_version': u'协议版本',
        'proto_mode': u'通信方式',
        'channel_num': u'通道数',
        'config_version': u'配置版本',
        'boot_version': u'Bootload版本',
        'ip_num': u'单设备IP数',
        'machine_id': u'设备号',
        'slot_id': u'槽位号'
    }

    baseinfo = [
            'mac',
            'hwcode',
            'hw_version',
            'sw_version',
            'proto_version',
            'proto_mode',
            'channel_num',
            'config_version',
            'boot_version',
            'ip_num',
            'machine_id',
            'slot_id'
        ]

    def __init__(self, parent=None):
        super(BaseinfoPage, self).__init__(parent)
        self.parent = parent
        self.ver = self.parent.ver
        self.initctrlbutton()
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.addWidget(self.ctrlwidget)
        self.mainLayout.addStretch(1)
        self.setLayout(self.mainLayout)

        self.connect(self.parent.tabs, QtCore.SIGNAL("currentChanged(int)"), self.tabchange)  # 页面切换时隐藏部分控件

    def initctrlbutton(self):

        self.checkButton = QtGui.QPushButton(u'查询')
        self.setButton = QtGui.QPushButton(u'设置')
        self.saveButton = QtGui.QPushButton(u'保存')

        self.ctrlwidget = QtGui.QWidget()

        ctrlLayout = QtGui.QGridLayout()
        for i in xrange(4):
            ctrlLayout.addWidget(QtGui.QLabel(), 0, i)
        ctrlLayout.addWidget(self.checkButton, 0, 5)
        ctrlLayout.addWidget(self.setButton, 0, 6)
        ctrlLayout.addWidget(self.saveButton, 0, 7)

        self.ctrlLayout = ctrlLayout

        self.checkButton.clicked.connect(self.checkinfo)
        self.setButton.clicked.connect(self.setinfo)
        self.saveButton.clicked.connect(self.saveinfo)
        self.setButton.setDisabled(True)
        self.saveButton.setDisabled(True)

        self.ctrlwidget.setLayout(self.ctrlLayout)

    def checkinfo(self):
        key = self.key
        mainwindow = self.parent.parent.parent()
        try:
            if hasattr(self, 'infowidget'):
                getattr(self, 'infowidget').deleteLater()

            ip = unicode(self.parent.ipEdit.text())
            port = int(unicode(self.parent.udpportEdit.text()))

            rsp = udpcmd.getinforsp(ip, port, code[key], ver=self.ver)
            code_result.update({key: rsp})

            self.infowidget = QtGui.QWidget()

            setattr(self, key + 'GridLoyout', QtGui.QGridLayout())

            for k in getattr(self, self.key):
                i = getattr(self, self.key).index(k)
                setattr(self, k + 'Label', QtGui.QLabel(unicode(self.baseinfo_zh[k])))
                setattr(self, k + 'LineEdit', QtGui.QLineEdit(unicode(rsp[k])))
                getattr(self, key + 'GridLoyout').addWidget(getattr(self, k + 'Label'), i, 0)
                getattr(self, key + 'GridLoyout').addWidget(getattr(self, k + 'LineEdit'), i, 1)
                getattr(self, k + 'LineEdit').setReadOnly(True)
            self.infowidget.setLayout(getattr(self, key + 'GridLoyout'))
            self.mainLayout.addWidget(self.infowidget)

            mainwindow.statusBar().showMessage(time.ctime() + u'产品固化信息查询成功')
        except Exception, e:
            logger.error(e)
            mainwindow.statusBar().showMessage(time.ctime() + u'产品固化信息查询失败')

    def setinfo(self):
        pass

    def saveinfo(self):
        pass

    def tabchange(self, i):
        if hasattr(self, 'infowidget'):
            getattr(self, 'infowidget').hide()


class ComminfoPage(QtGui.QWidget):

    key = 'comminfo'

    comminfo_zh = {
        'ip_mode': u'IP设置模式',
        'ipaddr': u'IP地址',
        'netmask': u'Netmask',
        'gateway': u'Gateway',
        'mgmt_ipaddr': u'IFPMS IP地址',
        'mgmt_port': u'IFPMS端口号',
        'syslog_ipaddr': u'syslog服务器 IP地址',
        'syslog_port': u'syslog服务器 端口号',
        'syslog_priority': u'Syslog日志优先级',
        'log_priority': u'本地日志优先级'
    }

    comminfo = [
        'ip_mode',
        'ipaddr',
        'netmask',
        'gateway',
        'mgmt_ipaddr',
        'mgmt_port',
        'syslog_ipaddr',
        'syslog_port',
        'syslog_priority',
        'log_priority'
    ]

    def __init__(self, parent=None):
        super(ComminfoPage, self).__init__(parent)
        self.parent = parent
        self.ver = self.parent.ver
        self.initctrlbutton()
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.addWidget(self.ctrlwidget)
        self.mainLayout.addStretch(1)
        self.setLayout(self.mainLayout)

        self.connect(self.parent.tabs, QtCore.SIGNAL("currentChanged(int)"), self.tabchange)  # 页面切换时淡入淡出效果

    def initctrlbutton(self):

        self.checkButton = QtGui.QPushButton(u'查询')
        self.setButton = QtGui.QPushButton(u'设置')
        self.saveButton = QtGui.QPushButton(u'保存')
        self.setButton.setToolTip(u'修改采集器ip方法：将ip设置模式修改为1（静态ip模式），然后修改ip地址, 点击设置按钮即可，最后点击保存重启')
        self.ctrlwidget = QtGui.QWidget()

        ctrlLayout = QtGui.QGridLayout()
        for i in xrange(4):
            ctrlLayout.addWidget(QtGui.QLabel(), 0, i)
        ctrlLayout.addWidget(self.checkButton, 0, 5)
        ctrlLayout.addWidget(self.setButton, 0, 6)
        ctrlLayout.addWidget(self.saveButton, 0, 7)

        self.ctrlLayout = ctrlLayout

        self.checkButton.clicked.connect(self.checkinfo)
        self.setButton.clicked.connect(self.setinfo)
        self.saveButton.clicked.connect(self.saveinfo)

        self.ctrlwidget.setLayout(self.ctrlLayout)

    def checkinfo(self):
        key = self.key
        mainwindow = self.parent.parent.parent()
        try:
            if hasattr(self, 'infowidget'):
                getattr(self, 'infowidget').deleteLater()

            ip = unicode(self.parent.ipEdit.text())
            port = int(unicode(self.parent.udpportEdit.text()))

            rsp = udpcmd.getinforsp(ip, port, code[key], ver=self.ver)
            code_result.update({key: rsp})

            self.infowidget = QtGui.QWidget()
            setattr(self, key + 'GridLoyout', QtGui.QGridLayout())

            for k in getattr(self, self.key):
                i = getattr(self, self.key).index(k)
                setattr(self, k + 'Label', QtGui.QLabel(unicode(self.comminfo_zh[k])))
                setattr(self, k + 'LineEdit', QtGui.QLineEdit(unicode(rsp[k])))
                getattr(self, key + 'GridLoyout').addWidget(getattr(self, k + 'Label'), i, 0)
                getattr(self, key + 'GridLoyout').addWidget(getattr(self, k + 'LineEdit'), i, 1)

            self.infowidget.setLayout(getattr(self, key + 'GridLoyout'))
            self.mainLayout.addWidget(self.infowidget)
            mainwindow.statusBar().showMessage(time.ctime() + u'通讯控制信息查询成功')
        except Exception, e:
            logger.error(e)
            mainwindow.statusBar().showMessage(time.ctime() + u'通讯控制信息查询失败')

    def setinfo(self):
        ip = unicode(self.parent.ipEdit.text())
        port = int(unicode(self.parent.udpportEdit.text()))
        mainwindow = self.parent.parent.parent()
        comminfobody = {}
        for k in self.comminfo:
            comminfobody.update({k: str(getattr(self, k + 'LineEdit').text())})
        flag = udpcmd.setinforsp(ip, port, code[self.key] + 1, ver=self.ver, body_dict=comminfobody)

        if flag:
            mainwindow.statusBar().showMessage(time.ctime() + u'通讯控制信息設置成功')
        else:
            mainwindow.statusBar().showMessage(time.ctime() + u'通讯控制信息設置失敗')

    def saveinfo(self):
        ip = unicode(self.parent.ipEdit.text())
        port = int(unicode(self.parent.udpportEdit.text()))
        udpcmd.save_reboot(ip, port, ver=self.ver)

    def tabchange(self, i):
        if hasattr(self, 'infowidget'):
            getattr(self, 'infowidget').hide()


class SamplingctrlinfoPage(QtGui.QWidget):

    key = 'samplingctrlinfo'

    samplingctrlinfo_zh = {
        'freq': u'每通道采样频率',
        'fft_size': u'处理粒度'
    }

    samplingctrlinfo = ['freq', 'fft_size']

    def __init__(self, parent=None):
        super(SamplingctrlinfoPage, self).__init__(parent)
        self.parent = parent
        self.ver = self.parent.ver
        self.initctrlbutton()
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.addWidget(self.ctrlwidget)
        self.mainLayout.addStretch(1)
        self.setLayout(self.mainLayout)
        self.connect(self.parent.tabs, QtCore.SIGNAL("currentChanged(int)"), self.tabchange)  # 页面切换时淡入淡出效果

    def initctrlbutton(self):

        self.checkButton = QtGui.QPushButton(u'查询')
        self.setButton = QtGui.QPushButton(u'设置')
        self.saveButton = QtGui.QPushButton(u'保存')

        self.ctrlwidget = QtGui.QWidget()

        ctrlLayout = QtGui.QGridLayout()
        for i in xrange(4):
            ctrlLayout.addWidget(QtGui.QLabel(), 0, i)
        ctrlLayout.addWidget(self.checkButton, 0, 5)
        ctrlLayout.addWidget(self.setButton, 0, 6)
        ctrlLayout.addWidget(self.saveButton, 0, 7)

        self.ctrlLayout = ctrlLayout

        self.checkButton.clicked.connect(self.checkinfo)
        self.setButton.clicked.connect(self.setinfo)
        self.saveButton.clicked.connect(self.saveinfo)

        self.setButton.setDisabled(True)
        self.saveButton.setDisabled(True)

        self.ctrlwidget.setLayout(self.ctrlLayout)

    def checkinfo(self):
        key = self.key
        mainwindow = self.parent.parent.parent()
        try:
            if hasattr(self, 'infowidget'):
                getattr(self, 'infowidget').deleteLater()

            ip = unicode(self.parent.ipEdit.text())
            port = int(unicode(self.parent.udpportEdit.text()))

            rsp = udpcmd.getinforsp(ip, port, code[key], ver=self.ver)
            code_result.update({key: rsp})

            self.infowidget = QtGui.QWidget()

            setattr(self, key + 'GridLoyout', QtGui.QGridLayout())

            for k in getattr(self, self.key):
                i = getattr(self, self.key).index(k)

                setattr(self, k + 'Label', QtGui.QLabel(unicode(getattr(self, self.key + '_zh')[k])))
                setattr(self, k + 'LineEdit', QtGui.QLineEdit(unicode(rsp[k])))
                getattr(self, key + 'GridLoyout').addWidget(getattr(self, k + 'Label'), i, 0)
                getattr(self, key + 'GridLoyout').addWidget(getattr(self, k + 'LineEdit'), i, 1)
                getattr(self, k + 'LineEdit').setReadOnly(True)
            self.infowidget.setLayout(getattr(self, key + 'GridLoyout'))
            self.mainLayout.addWidget(self.infowidget)

            mainwindow.statusBar().showMessage(time.ctime() + u'采样控制信息查询成功')
        except Exception, e:
            logger.error(e)
            mainwindow.statusBar().showMessage(time.ctime() + u'采样控制信息查询失败')

    def setinfo(self):
        pass

    def saveinfo(self):
        pass

    def tabchange(self, i):
        if hasattr(self, 'infowidget'):
            getattr(self, 'infowidget').hide()


class ChannelctrlinfoPage(QtGui.QWidget):

    key = 'channelctrlinfo'

    channelctrlinfo_zh = {
        'enable': u'启用状态',
        'mu_factor': u'数字放大倍数',
        'mode': u'处理模式',
        'pre_process_mode': u'预处理模式',
        'photoelectron_value': u'光电特性值',
        'win_size': u'有效窗口个数',
        'win': u'窗口'
    }

    channelctrlinfo = ['enable', 'mu_factor', 'mode', 'pre_process_mode', 'photoelectron_value', 'win_size', 'win']

    def __init__(self, parent=None):
        super(ChannelctrlinfoPage, self).__init__(parent)
        self.parent = parent
        self.ver = self.parent.ver
        self.initctrlbutton()
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.addWidget(self.ctrlwidget)
        self.mainLayout.addStretch(1)
        self.setLayout(self.mainLayout)
        self.connect(self.parent.tabs, QtCore.SIGNAL("currentChanged(int)"), self.tabchange)  # 页面切换时淡入淡出效果

    def initctrlbutton(self):

        self.channelLabel = QtGui.QLabel(u"通道号：")
        self.channelLabel.setAlignment(QtCore.Qt.AlignRight)
        self.channelCombo = QtGui.QComboBox()
        self.channelCombo.addItem('1')
        self.channelCombo.addItem('2')
        self.channelCombo.addItem('3')
        self.channelCombo.addItem('4')

        self.checkButton = QtGui.QPushButton(u'查询')
        self.setButton = QtGui.QPushButton(u'设置')
        self.saveButton = QtGui.QPushButton(u'保存')

        self.ctrlwidget = QtGui.QWidget()

        ctrlLayout = QtGui.QGridLayout()
        for i in xrange(2):
            ctrlLayout.addWidget(QtGui.QLabel(), 0, i)
        ctrlLayout.addWidget(self.channelLabel, 0, 3)
        ctrlLayout.addWidget(self.channelCombo, 0, 4)
        ctrlLayout.addWidget(self.checkButton, 0, 5)
        ctrlLayout.addWidget(self.setButton, 0, 6)
        ctrlLayout.addWidget(self.saveButton, 0, 7)

        self.ctrlLayout = ctrlLayout

        self.checkButton.clicked.connect(self.checkinfo)
        self.setButton.clicked.connect(self.setinfo)
        self.saveButton.clicked.connect(self.saveinfo)

        self.setButton.setDisabled(True)
        self.saveButton.setDisabled(True)

        self.ctrlwidget.setLayout(self.ctrlLayout)

    def checkinfo(self):
        key = self.key
        mainwindow = self.parent.parent.parent()
        try:
            if hasattr(self, 'infowidget'):
                getattr(self, 'infowidget').deleteLater()

            ip = unicode(self.parent.ipEdit.text())
            port = int(unicode(self.parent.udpportEdit.text()))
            channel = int(self.channelCombo.currentText())

            rsp = udpcmd.getinforsp(ip, port, code[key], channel=channel, ver=self.ver)
            code_result.update({key: rsp})

            self.infowidget = QtGui.QWidget()

            setattr(self, key + 'GridLoyout', QtGui.QGridLayout())

            for k in getattr(self, self.key):
                i = getattr(self, self.key).index(k)

                setattr(self, k + 'Label', QtGui.QLabel(unicode(getattr(self, self.key + '_zh')[k])))
                setattr(self, k + 'LineEdit', QtGui.QLineEdit(unicode(rsp[k])))
                getattr(self, key + 'GridLoyout').addWidget(getattr(self, k + 'Label'), i, 0)
                getattr(self, key + 'GridLoyout').addWidget(getattr(self, k + 'LineEdit'), i, 1)
                getattr(self, k + 'LineEdit').setReadOnly(True)
            self.infowidget.setLayout(getattr(self, key + 'GridLoyout'))
            self.mainLayout.addWidget(self.infowidget)

            mainwindow.statusBar().showMessage(time.ctime() + u'\t\t通道%d\t\t' % channel  + u'通道控制信息查询成功')
        except Exception, e:
            logger.error(e)
            mainwindow.statusBar().showMessage(time.ctime() + u'\t\t通道%d\t\t' % channel  + u'通道控制信息查询失败')

    def setinfo(self):
        pass

    def saveinfo(self):
        pass

    def tabchange(self, i):
        if hasattr(self, 'infowidget'):
            getattr(self, 'infowidget').hide()


class DevicefunctioninfoPage(QtGui.QWidget):

    key = 'devicefunction'

    def __init__(self, parent=None):
        super(DevicefunctioninfoPage, self).__init__(parent)
        self.parent = parent
        self.ver = self.parent.ver
