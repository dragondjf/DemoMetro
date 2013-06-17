#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from PyQt4 import QtCore
from basepage import BasePage
import os


class ExitPage(BasePage):
    def __init__(self, parent=None):
        super(ExitPage, self).__init__(parent)
        self.parent = parent
        # print self.parent.parent()
        self.configGroup = QtGui.QGroupBox(u"退出设置")

        self.exitLayout = QtGui.QGridLayout()
        # self.exitLayout.addWidget(self.ipLabel, 0, 0)
        self.configGroup.setLayout(self.exitLayout)

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.addWidget(self.configGroup)
        self.mainLayout.addStretch(1)
        self.setLayout(self.mainLayout)
