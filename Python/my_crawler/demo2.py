#!/usr/bin/python
# -*- coding:utf-8 -*-

#urllib2_proxy2.py

import urllib2
import urllib

def test():
	# 私密代理授权的账户
	user = "F3200278"
	# 私密代理授权的密码
	passwd = "Foxconn@2016"
	# 私密代理 IP
	proxyserver = "10.191.131.43:3128"
	# Download URL
	url="https://www.python.org/ftp/python/3.5.0/python-3.5.0-macosx10.6.pkg"
	# 保存的文件路径
	filename="download.txt"
	

	# 1. 构建一个密码管理对象，用来保存需要处理的用户名和密码
	passwdmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()

	# 2. 添加账户信息，第一个参数realm是与远程服务器相关的域信息，一般没人管它都是写None，后面三个参数分别是 代理服务器、用户名、密码
	passwdmgr.add_password(None, proxyserver, user, passwd)

	# 3. 构建一个代理基础用户名/密码验证的ProxyBasicAuthHandler处理器对象，参数是创建的密码管理对象
	#   注意，这里不再使用普通ProxyHandler类了
	proxyauth_handler = urllib2.ProxyBasicAuthHandler(passwdmgr)

	# 4. 通过 build_opener()方法使用这些代理Handler对象，创建自定义opener对象，参数包括构建的 proxy_handler 和 proxyauth_handler
	opener = urllib2.build_opener(proxyauth_handler)

	# 5. 构造Request 请求
	request = urllib2.Request("http://www.baidu.com/")

	# 6. 使用自定义opener发送请求
	response = opener.open(request)

	# 7. 打印响应内容
	# print response.read()
	
	# 8. 保存文件内容
	with open( filename, 'w') as f:
		f.write("")
