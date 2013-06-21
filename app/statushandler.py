#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
from PyQt4 import QtCore
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import json
import urllib
import time


class StatusListenThreadServer(threading.Thread, QtCore.QObject):

    statuschanged = QtCore.pyqtSignal(dict)

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        QtCore.QObject.__init__(self)
        threading.Thread.__init__(self)
        self.setDaemon(True)

    def run(self):
        status_server = StatusHttpServer((self.ip, self.port), StatusRequestHandler, self)
        status_server.serve_forever()

    def changestatus(self, painfo):
        self.statuschanged.emit(painfo)


class StatusHttpServer(ThreadingMixIn, HTTPServer):
    '''
    '''
    def __init__(self, server_address, RequestHandlerClass, listenserver):

        self.listenserver = listenserver
        HTTPServer.__init__(self, server_address, RequestHandlerClass)


class StatusRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        datas = self.rfile.read(int(self.headers['content-length']))
        datas = urllib.unquote(datas).decode("utf-8", 'ignore')  # 指定编码方式
        notification = json.loads(datas[len('notification='):])
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(notification[u'status_change_time']))).decode('UTF8')
        painfo = {
                    'pid': notification[u'pid'],
                    'did': notification[u'did'],
                    'rid': 0,
                    'status': notification[u'status'],
                    'status_change_time': t
                }
        self.server.listenserver.changestatus(painfo)
