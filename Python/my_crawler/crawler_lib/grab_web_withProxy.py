#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Author:Cyril
# Create:2018/04/23 17:19:00
# Alter:2018/04/23 17:20:00

import urllib2
import urllib
import constant
import os

# 系统输出信息
System_Print=constant.System_Print
# 私密代理授权的账户及密码
USER=constant.USER
PWD=constant.PWD
# 私密代理IP
PROXY_SERVER=constant.PROXY_SERVER
# Download URL
URL_1=constant.URL_1
# Save File PATH
FILE_SAVE_NAME=constant.FILE_SAVE_NAME
FILE_SAVE_PATH=constant.FILE_SAVE_PATH

# 在公司里加域的电脑上运行Crawler抓取web
def _GrabWebWithProxy():
	# 1>.构建一个密码管理对象，用于保存需要处理的用户名和密码
	passwdmgr=urllib2.HTTPPasswordMgrWithDefaultRealm()

	# 2>.添加账户信息，第一个参数realm是与远程服务器相关的域信息，默认None，后面三个参数分别是 代理服务器、用户名、密码
	passwdmgr.add_password(None, PROXY_SERVER, USER, PWD)

	# 3>.构建一个代理基础用户名／密码验证的ProxyBasicAuthHandler处理器对象，参数是创建的密码管理器对象
	#    注意此处不在使用普通ProxyHandler类了
	proxyauth_handler = urllib2.ProxyBasicAuthHandler(passwdmgr)

	# 4. 通过 build_opener()方法使用这些代理Handler对象，创建自定义opener对象，参数包括构建的 proxy_handler 和 proxyauth_handler
	opener = urllib2.build_opener(proxyauth_handler)

	# 5. 构造Request 请求
	request = urllib2.Request(URL_1)

	# 6. 使用自定义opener发送请求
	response = opener.open(request)

	# 7. 打印响应内容
	# print response.read()

	# 8. 保存文件内容
	# print "FILE_SAVE_PATH:",FILE_SAVE_PATH
	if not os.path.exists(FILE_SAVE_PATH):
		os.makedirs(FILE_SAVE_PATH)
    	with open(FILE_SAVE_NAME, 'w')as f:
		f.write(response.read())

if __name__ == '__main__':
	print System_Print,'运行 grab_web_WithProxy 测试'
else:
	print System_Print,'执行 grab_web_WithProxy 函数初始化'

