#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
from PyQt4 import QtGui
from PyQt4 import QtCore
from basepage import BasePage
import update_client
# from ping import ping


class UpdatePage(BasePage):
    def __init__(self, parent=None):
        super(UpdatePage, self).__init__(parent)
        self.parent = parent
        self.initipGrounp()

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.ipGroup)

        mainLayout.addSpacing(12)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)
        self.mainLayout = mainLayout

    def resizeEvent(self, event):
        width = self.ipctrl.width()
        if hasattr(self, 'updatetablewidget'):
            self.updatetablewidget.setColumnWidth(0, width / 4)
            self.updatetablewidget.setColumnWidth(1, width / 2)
            self.updatetablewidget.setColumnWidth(2, width / 4)

    def initipGrounp(self):
        ipGroup = QtGui.QGroupBox(u"固件升级")

        # 单个ip和多个ip选择
        ipctrl = QtGui.QWidget()
        ipctrlLayout = QtGui.QHBoxLayout()
        singleipRadioButton = QtGui.QRadioButton(u'单个ip')
        multiipRadioButton = QtGui.QRadioButton(u'多个ip')
        ipctrlLayout.addWidget(singleipRadioButton)
        ipctrlLayout.addWidget(multiipRadioButton)
        ipctrl.setLayout(ipctrlLayout)
        self.ipctrl = ipctrl

        # 根据单个ip和多个ip显示不同的提示和输入方式
        ipinput = QtGui.QWidget()
        self.ipLabel = QtGui.QLabel(u'输入采集器的IP范围：')
        self.beginipEdit = QtGui.QLineEdit('192.168.100.79')
        self.beginipEdit.setInputMask('000.000.000.000')
        self.endipEdit = QtGui.QLineEdit('192.168.100.82')
        self.endipEdit.setInputMask('000.000.000.000')

        ipLayout = QtGui.QGridLayout()
        ipLayout.addWidget(self.ipLabel, 0, 0)
        ipLayout.addWidget(self.beginipEdit, 0, 1)
        ipLayout.addWidget(self.endipEdit, 0, 2)
        ipinput.setLayout(ipLayout)

        # bin和cfg文件选择
        fileselect = QtGui.QWidget()
        fileLayout = QtGui.QHBoxLayout()
        updatemode = QtGui.QPushButton(u'开启升级模式')
        filechoose = QtGui.QPushButton(u'选择固件文件')
        fileLayout.addWidget(updatemode)
        fileLayout.addWidget(filechoose)
        fileselect.setLayout(fileLayout)

        updatemode.clicked.connect(self.startupdatemode)
        filechoose.clicked.connect(self.filechoose)
        # filechoose.setDisabled(True)
        self.filechooseButton = filechoose

        # 固件升级组
        ipGroupLayout = QtGui.QVBoxLayout()
        ipGroupLayout.addWidget(ipctrl)
        ipGroupLayout.addWidget(ipinput)
        ipGroupLayout.addWidget(fileselect)
        ipGroup.setLayout(ipGroupLayout)

        self.ipctrl = ipctrl
        self.ipinput = ipinput
        self.fileselect = fileselect

        self.ipGroup = ipGroup

        # 创建ip单选与多选的槽响应
        singleipRadioButton.toggled.connect(self.singleip)
        multiipRadioButton.toggled.connect(self.multiip)
        singleipRadioButton.setChecked(True)

        self.singleipRadioButton = singleipRadioButton
        self.multiipRadioButton = multiipRadioButton

    def singleip(self):
        self.endipEdit.hide()
        self.ipLabel.setText(u'输入单个采集器的ip：')

    def multiip(self):
        self.endipEdit.show()
        self.ipLabel.setText(u'输入采集器的IP范围：')

    def startupdatemode(self):
        self.ips = []
        ip_ready = []
        if self.singleipRadioButton.isChecked():
            self.ips = [str(self.beginipEdit.text())]

        if self.multiipRadioButton.isChecked():
            startip = str(self.beginipEdit.text())
            endip = str(self.endipEdit.text())
            ipnum = startip.split('.')
            baseip = '.'.join(ipnum[0:3])
            for i in range(int(startip.split('.')[3]), int(endip.split('.')[3])):
                self.ips.append(baseip + '.' + str(i))
        for ip in self.ips:
            ip_ready.append(update_client.enter_update_mode(ip, update_client.udp_port))

        if all(ip_ready):
            # self.filechooseButton.setDisabled(False)
            self.parent.parent().statusBar().showMessage(u'开启升级模式 成功')
        else:
            # self.filechooseButton.setDisabled(True)
            self.parent.parent().statusBar().showMessage(u'开启升级模式 失败')

    def filechoose(self):
        self.file_handleobj = {}
        fileNames = QtGui.QFileDialog.getOpenFileNames(self, u"选择需要升级的固件文件", u'', "file(*.bin *cfg);;All Files (*)")
        updatefiles = [str(i) for i in fileNames]

        if hasattr(self, 'fileshowwidget'):
            getattr(self, 'fileshowwidget').deleteLater()

        self.fileshowwidget = QtGui.QWidget()
        fileLayout = QtGui.QGridLayout()
        for filename in updatefiles:
            i = updatefiles.index(filename)
            setattr(self, 'filecheckbox%d' % i, QtGui.QCheckBox(u'%s' % filename))
            setattr(self, 'filemd5state%d' % i, QtGui.QLabel(u''))
            self.file_handleobj.update({filename: [getattr(self, 'filecheckbox%d' % i), getattr(self, 'filemd5state%d' % i)]})
            fileLayout.addWidget(getattr(self, 'filecheckbox%d' % i), i, 0)
            fileLayout.addWidget(getattr(self, 'filemd5state%d' % i), i, 1)

        self.checkfilesatateButton = QtGui.QPushButton(u'检测文件MD5状态')
        self.deletefileButton = QtGui.QPushButton(u'删除MD5校验不正确和未选中的文件')
        self.updatefileButton = QtGui.QPushButton(u'升级选中文件')

        ctrindex = len(fileNames)

        fileLayout.addWidget(self.checkfilesatateButton, ctrindex, 0)
        fileLayout.addWidget(self.deletefileButton, ctrindex, 1)
        fileLayout.addWidget(self.updatefileButton, ctrindex, 2)

        self.fileshowwidget.setLayout(fileLayout)
        index = self.ipGroup.layout().indexOf(self.fileselect)

        self.ipGroup.layout().insertWidget(index + 1, self.fileshowwidget)

        self.checkfilesatateButton.clicked.connect(self.checkfilestate)
        self.deletefileButton.clicked.connect(self.deletefile)
        self.updatefileButton.clicked.connect(self.updatefile)

        self.deletefileButton.setDisabled(True)
        self.updatefileButton.setDisabled(True)

    def checkfilestate(self):
        for k, v in self.file_handleobj.items():
            flag = update_client.is_valid_fw(k)
            if flag:
                v[1].setText(u'MD5校验正确')
            else:
                v[1].setText(u'MD5校验错误')

        self.deletefileButton.setDisabled(False)

    def deletefile(self):
        '''
            删除MD5校验不正确和未选中的文件
        '''
        self.file_uncorrect = {}
        for k, v in self.file_handleobj.items():
            flag = v[0].isChecked()
            if not flag:
                self.file_uncorrect.update({k: v})
            else:
                if v[1].text() == u'MD5校验错误':
                    self.file_uncorrect.update({k: v})
        for k, v in self.file_uncorrect.items():
            v[0].deleteLater()
            v[1].deleteLater()
            self.file_handleobj.pop(k)
        if not self.file_handleobj:
            self.checkfilesatateButton.deleteLater()
            self.deletefileButton.deleteLater()
            self.updatefileButton.deleteLater()

        self.checkfilesatateButton.setDisabled(True)
        self.deletefileButton.setDisabled(True)
        self.updatefileButton.setDisabled(False)

        if hasattr(self, 'updateinfo'):
            getattr(self, 'updateinfo').deleteLater()

        self.updateinfo = QtGui.QWidget()
        updateinfoLaout = QtGui.QGridLayout()

        ipLabel = QtGui.QLabel(u'目的采集器ip:')
        self.ipshowLabel = QtGui.QLabel(u'')

        fileLabel = QtGui.QLabel(u'升级的文件:')
        self.fileshowLabel = QtGui.QLabel(u'')

        progreessLabel = QtGui.QLabel(u'升级进度:')
        self.updateprogress = QtGui.QProgressBar()

        lastLabel = QtGui.QLabel(u'最终状态:')
        self.updatestateLabel = QtGui.QLabel(u'')

        updateinfoLaout.addWidget(ipLabel, 0, 0)
        updateinfoLaout.addWidget(self.ipshowLabel, 0, 1)
        updateinfoLaout.addWidget(fileLabel, 1, 0)
        updateinfoLaout.addWidget(self.fileshowLabel, 1, 1)
        updateinfoLaout.addWidget(progreessLabel, 2, 0)
        updateinfoLaout.addWidget(self.updateprogress, 2, 1)
        updateinfoLaout.addWidget(lastLabel, 3, 0)
        updateinfoLaout.addWidget(self.updatestateLabel, 3, 1)

        self.updateinfo.setLayout(updateinfoLaout)

        index = self.ipGroup.layout().indexOf(self.fileshowwidget)
        self.ipGroup.layout().insertWidget(index + 1, self.updateinfo)

        if hasattr(self, 'updatehistoryWidget'):
            getattr(self, 'updatehistoryWidget').deleteLater()

        # 获取ip
        self.ips = []
        if self.singleipRadioButton.isChecked():
            self.ips = [str(self.beginipEdit.text())]

        if self.multiipRadioButton.isChecked():
            startip = str(self.beginipEdit.text())
            endip = str(self.endipEdit.text())
            ipnum = startip.split('.')
            baseip = '.'.join(ipnum[0:3])
            for i in range(int(startip.split('.')[3]), int(endip.split('.')[3])):
                self.ips.append(baseip + '.' + str(i))

        # 获取升级文件
        self.file_updated = [k for k, v in self.file_handleobj.items() if v[0].isChecked()]
        # bin_files = [f for f in self.file_updated if f.endswith('.bin')]
        # cfg_files = [f for f in self.file_updated if f.endswith('.cfg')]

        # 升级历史显示
        rows = len(self.file_updated) * len(self.ips)
        hheaders = [u'采集器ip', u'升级文件', u'升级状态']

        self.updatehistoryWidget = QtGui.QWidget()
        updatehistoryLaout = QtGui.QVBoxLayout()
        self.updatetablewidget = QtGui.QTableWidget(rows, 3, self.updatehistoryWidget)
        # 设置表头
        for key in hheaders:
            index = hheaders.index(key)
            self.updatetablewidget.setHorizontalHeaderItem(index, QtGui.QTableWidgetItem(key))
        # 设置表头的宽度
        width = self.ipctrl.width()       
        self.updatetablewidget.setColumnWidth(0, width/4)
        self.updatetablewidget.setColumnWidth(1, width/2)
        self.updatetablewidget.setColumnWidth(2, width/4)
        updatehistoryLaout.addWidget(self.updatetablewidget)
        self.updatehistoryWidget.setLayout(updatehistoryLaout)

        index = self.ipGroup.layout().indexOf(self.updateinfo)
        self.ipGroup.layout().insertWidget(index + 1, self.updatehistoryWidget)

    def updatefile(self):
        # 升级文件
        row = 0
        for ip in self.ips:
            self.ipshowLabel.setText(ip)
            for f in self.file_updated:
                self.fileshowLabel.setText(f)
                try:
                    self.uc = update_client.TftpUpdateClient(ip, f)
                    self.uc.MAX_TFTP_ATTEMPT = 1
                    self.uc.start()
                    while True:
                        self.progressbarupdate()
                        if self.uc.info['update_flag']:
                            self.updatestateLabel.setText(time.ctime() + u'\t\t升级成功')
                            self.updatetablewidget.setItem(row, 0, QtGui.QTableWidgetItem(ip))
                            self.updatetablewidget.setItem(row, 1, QtGui.QTableWidgetItem(f))
                            self.updatetablewidget.setItem(row, 2, QtGui.QTableWidgetItem(u'升级成功'))
                            break
                        if self.uc.tftptimeout:
                            break
                except Exception:
                    self.updateprogress.setValue(self.uc.info['progress'])
                    self.updatestateLabel.setText(time.ctime() + u'\t\t升级失败')
                    self.updatetablewidget.setItem(row, 0, QtGui.QTableWidgetItem(ip))
                    self.updatetablewidget.setItem(row, 1, QtGui.QTableWidgetItem(f))
                    self.updatetablewidget.setItem(row, 2, QtGui.QTableWidgetItem(u'升级失败'))
                row = row + 1

    def progressbarupdate(self):
        self.updateprogress.setValue(self.uc.info['progress'])
        self.updatestateLabel.setText(time.ctime() + u'\t\t正在升级中......')
