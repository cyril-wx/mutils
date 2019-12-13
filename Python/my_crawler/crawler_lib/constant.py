#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import sys

System_Print = '[System:Print]'

# ********获取文件路径的方法***********
# 获取项目工作目录绝对路径
# print(os.getcwd())
#表示项目工作目录的绝对路径 
# CURRENT_PROJ_DIR_PATH = os.path.abspath('.')  
#表示项目的真实工作目录的绝对路径  
# PROJ_DIR_PATH = os.path.abspath('./my_crawler')

# 获取当前constant.py工作目录实际路径
# 实际文件路径: /Users/gdadmin/Desktop/Cyril/Python/my_crawler/crawler_lib/constant.py
# 打印出来：/Users/gdadmin/Desktop/Cyril/Python/my_crawler/crawler_lib
# ********获取文件路径的方法***********

# 获取当前constant.py工作目录实际路径
CURRENT_FILE_DIR_PATH = sys.path[0]

#Save File PATH
FILE_SAVE_PATH = CURRENT_FILE_DIR_PATH + "/Download"
FILE_SAVE_NAME = FILE_SAVE_PATH + '/DOWNLOAD.txt'


#私密代理授权的账户及密码
USER = "F3200278"
PWD = "Foxconn@2016"

#私密代理IP
PROXY_SERVER = "10.191.131.43:3128"

#Download URL
#URL_1 = "http://www.baidu.com/"
#URL_1 = "http://10.172.5.131/images/misc/rt.gif"
#URL_1="http://10.172.5.131/images/statusicons/download.gif"
URL_1 = "http://10.172.5.131/cgi-bin/WebObjects/QCR.woa/10/wo/aLNxtEbVMAwidmjzkwHqZg/4.13.1.5.15.1.3.0.1/C39WG01RJVYD_20180510-225230.966494_D32_QT0_Porsche_QT0_C39WG01RJVYD_T1_D0_20180510T2248043.txt.txt.gz"







