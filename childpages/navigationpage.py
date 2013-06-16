#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from PyQt4 import QtGui
from PyQt4 import QtCore
from basepage import BasePage

logger = logging.getLogger(__name__)


class NavigationPage(BasePage):
    def __init__(self, parent=None):
        super(NavigationPage, self).__init__(parent)
        self.parent = parent
