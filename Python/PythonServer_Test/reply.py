# -*- coding:UTF-8 -*-
# filename: reply.py

# create by Cyril on 2018-10-23 11:10

# read !date +\%Y-\%m-\%d\ \%H\:\%M #shell date

import time

class Msg(object):
	def __init__(self):
		pass
	def send(self):
		return 'success.'


class PythonMsg(Msg):
	def __init__(self, code_base, code_lang, code_param):
		self.__dic = dict()
		self.__dict['code_base'] = code_base
		self.__dict['code_lang'] = code_lang
		self.__dict['code_param'] = code_param
		self.__dict['MsgId'] = MsgId
	
	def send(self):
		XmlForm = """
		<xml>
		<MsgId><![CDATA[{MsgId}]]></MsgId>
		<code_base><![CDATA[{code_base}]]></code_base>
		<code_lang><![CDATA[{code_lang}]]></code_lang>
		<code_param><![CDATA[{code_param}]]></code_param>
		</xml>
		"""
		return XmlForm.format(**self.__dict)
