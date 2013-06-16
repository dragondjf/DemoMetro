# -*- coding: utf-8 -*-
#
# Copyright © 2013 dragondjf
# Pierre Raybaut
# Licensed under the terms of the CECILL License

import os
import stat
import shutil

from distutils.core import setup
import py2exe
import sys

def delete_file_folder(src):
    '''delete files and folders'''
    if os.path.isfile(src):
        try:
            os.remove(src)
        except:
            pass
    elif os.path.isdir(src):
        for item in os.listdir(src):
            itemsrc=os.path.join(src,item)
            delete_file_folder(itemsrc) 
        try:
            os.rmdir(src)
        except:
            pass

#this allows to run it with a simple double click.
for key in ['build', 'dist']:
  path = os.getcwd() + os.sep + key
  delete_file_folder(path)

sys.argv.append('py2exe')

py2exe_options = {
        "includes": ["sip"],
        "dll_excludes": ["MSVCP90.dll",],
        "compressed": 1,
        "optimize": 2,
        "ascii": 0,
        "bundle_files": 1,
        }

setup(
      name = 'Config Tool',
      version = '1.0',
      windows=[{
          "script": "ConfigTool.py",
          "icon_resources": [(1, os.sep.join(['skin', 'images', 'config8.ico']))]
        }],
      author = 'djf',
      author_email = 'dragondjf@gmail.com',
      maintainer = 'djf',
      zipfile = None,
      options = {'py2exe': py2exe_options}
      )

'''
    拷贝响应的图片皮肤和与项目有关的资源文件到打包目录
'''
for item in ['skin', 'log', 'file']:
    shutil.copytree(os.getcwd() + os.sep + item, os.getcwd() + os.sep + os.sep.join(['dist', item]))

for key in ['build']:
  path = os.getcwd() + os.sep + key
  delete_file_folder(path)

os.remove(os.getcwd() + os.sep + 'dist' + os.sep + 'w9xpopen.exe')
os.remove(os.getcwd() + os.sep + 'dist' + os.sep + 'log' + os.sep + 'config.log')
