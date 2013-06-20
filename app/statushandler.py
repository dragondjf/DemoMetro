#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
from PyQt4 import QtCore
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import json
import urllib
import time

class StatusListenThreadHandler(threading.Thread, QtCore.QObject):

    statuschanged = QtCore.pyqtSignal(dict)

    def __init__(self):
        QtCore.QObject.__init__(self)
        threading.Thread.__init__(self)
        self.setDaemon(True)

    def run(self):
        status_server = StatusHttpServer(('192.168.10.135', 8000), StatusRequestHandler, self)
        status_server.serve_forever()



    def changestatus(self, painfo):
        self.statuschanged.emit(painfo)

class StatusHttpServer(ThreadingMixIn, HTTPServer):
    '''
    '''
    def __init__(self, server_address, RequestHandlerClass, listenhandler):

        self.listenhandler = listenhandler
        HTTPServer.__init__(self, server_address, RequestHandlerClass)


class StatusRequestHandler(BaseHTTPRequestHandler):


    def do_GET(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        datas = self.rfile.read(int(self.headers['content-length']))
        datas = urllib.unquote(datas).decode("utf-8", 'ignore')#指定编码方式
        notification = json.loads(datas[len('notification='):])
        painfo = {
                    'pid': notification[u'pid'],
                    'did': notification[u'did'],
                    'rid': 0,
                    'status': notification[u'status'],
                    'change_time': time.localtime(notification[u'status_change_time'])
                }
        self.server.listenhandler.changestatus(painfo)


def web_get(url, user, passwd):

    f = None

    try:
        req = urllib2.Request(url)
        logger.info("web get [%s]" % (url))
        auth = "Basic " + base64.urlsafe_b64encode("%s:%s" % (user, passwd))
        req.add_header("Authorization", auth)
        f = urllib2.urlopen(req)
        logger.info("web get ok.")
    except Exception, e:
        logger.info("web get failed.")
    finally:
        if f:
            f.close()
