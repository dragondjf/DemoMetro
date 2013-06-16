#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from PyQt4 import QtCore
from basepage import BasePage


class AlarmPage(BasePage):
    def __init__(self, parent=None):
        super(AlarmPage, self).__init__(parent)
        self.parent = parent

        hheaders = [u'采集器', u'DC编号', u'PA编号', u'发生时间', u'是否确认', u'告警复核', u'确认备注', u'确认时间', u'操作员', u'全选']
        vheaders = [str(i) for i in range(10)]
        self.hheaders_width = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
        contents = []
        for i in range(len(vheaders)):
            alarm = []
            for j in range(len(hheaders)):
                alarm.append(str((i + 1) * (j + 1)))
            contents.append(alarm)

        self.table = CumstomTable(hheaders, vheaders, contents, self)

        mainlayout = QtGui.QVBoxLayout()
        mainlayout.addWidget(self.table)
        self.setLayout(mainlayout)

    def resizeEvent(self, event):
        width = self.parent.width()
        if hasattr(self, 'table'):
            for i in range(len(self.hheaders_width)):
                self.table.setColumnWidth(i, self.hheaders_width[i] * width)


class CumstomTable(QtGui.QTableWidget):
    def __init__(self, hheaders, vheaders, contents, parent=None):
        super(CumstomTable, self).__init__(len(vheaders), len(hheaders), parent)
        self.parent = parent
        self.hheaders = hheaders
        self.vheaders = vheaders
        self.contents = contents

        self.setupHeaders()
        self.setupContents()

    def setupHeaders(self):
        width = self.parent.parent.parent().width() * 2
        for key in self.hheaders:
            index = self.hheaders.index(key)
            self.setHorizontalHeaderItem(index, QtGui.QTableWidgetItem(key))

        for key in self.vheaders:
            index = self.vheaders.index(key)
            self.setVerticalHeaderItem(index, QtGui.QTableWidgetItem(key))

        titleFont = self.font()
        for x in range(self.columnCount()):
            headItem = self.horizontalHeaderItem(x)   # 获得水平方向表头的Item对象
            headItem.setFont(titleFont)                      # 设置字体
            headItem.setBackgroundColor(QtGui.QColor(0, 60, 10))      # 设置单元格背景颜色
            headItem.setTextColor(QtGui.QColor(200, 111, 30))         # 设置文字颜色

        for x in range(self.rowCount()):
            headItem = self.verticalHeaderItem(x)   # 获得水平方向表头的Item对象
            headItem.setFont(titleFont)   # 设置字体
            headItem.setBackgroundColor(QtGui.QColor(0, 60, 10))      # 设置单元格背景颜色
            headItem.setTextColor(QtGui.QColor(200, 111, 30))         # 设置文字颜色

    def setupContents(self):
        for alarm in self.contents:
            rowindex = self.contents.index(alarm)
            for con in alarm:
                colindex = alarm.index(con)
                self.setItem(colindex, rowindex, QtGui.QTableWidgetItem(con))
