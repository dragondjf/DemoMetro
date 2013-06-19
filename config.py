#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import json

try:
    with open('windowsoptions.json', 'r') as f:
        windowsoptions = json.load(f)
except Exception, e:
    windowsoptions = {
        'login_window': {
                'login_title': u'登陆',
                'windowicon': os.sep.join([os.getcwd(), 'skin', 'images', 'config8.png']),
                'minsize': (400, 300),
                'size': (400, 300),
                'logo_title': u'Metro Style Mangager System',
                'logo_img_url': os.sep.join([os.getcwd(), 'skin', 'images', 'config8.png'])
            },
        'mainwindow': {
                'title': u'DemoMetro',
                'postion': (300, 300),
                'minsize': (800, 600),
                'size': (800, 600),
                'windowicon': os.sep.join(['skin', 'images', 'config8.png']),
                'fullscreenflag': True,
                'centralwindow': {
                    'page_tag': [['Monitor', 'Alarm', 'User'], ['Waveform', 'System', 'Help'], ['About', 'Exit', 'Add']],
                    'page_tag_zh': {
                        'Monitor': u'监控管理(Monitor)',
                        'Alarm': u'告警管理(Alarm)',
                        'User': u'用户管理(User)',
                        'Waveform': u'波形管理(Waveform)',
                        'System': u'系统管理(System)',
                        'Help': u'帮助(Help)',
                        'About': u'关于(About)',
                        'Exit': u'退出(Exit)',
                        'Add': u''
                    }
                },
                'statusbar': {
                    'initmessage': u'Ready',
                    'minimumHeight': 30,
                    'visual': False
                }
            },
        'exitdialog': {
            'exit_title': u'登陆',
            'windowicon': os.sep.join([os.getcwd(), 'skin', 'images', 'config8.png']),
            'minsize': (400, 300),
            'size': (400, 300),
            'logo_title': u'Metro Style Mangager System',
            'logo_img_url': os.sep.join([os.getcwd(), 'skin', 'images', 'config8.png'])
        },
        'adddcdialog': {
            'adddc_title': u'增加采集器',
            'windowicon': os.sep.join([os.getcwd(), 'skin', 'images', 'config8.png']),
            'minsize': (400, 300),
            'size': (400, 300),
            'logo_title': u'Metro Style Mangager System',
            'logo_img_url': os.sep.join([os.getcwd(), 'skin', 'images', 'config8.png'])
        },
        'msgdialog': {
            'msg_title': u'增加采集器',
            'windowicon': os.sep.join([os.getcwd(), 'skin', 'images', 'config8.png']),
            'minsize': (400, 300),
            'size': (400, 300),
            'logo_title': u'Metro Style Mangager System',
            'logo_img_url': os.sep.join([os.getcwd(), 'skin', 'images', 'config8.png'])
        },
        'splashimg': os.sep.join([os.getcwd(), 'skin', 'images', 'splash.png']),
        'monitorpage': {
            'backgroundimg': os.sep.join([os.getcwd(), 'skin', 'images', 'bg.jpg'])
        },
        'maxpanum': 128
    }
