# -*- coding: utf-8 -*-
# filename: receive.py
# create by Cyril on 18/10/23 11:00

# read !date +\%Y-\%m-\%d\ \%H\:\%M #shell date

import xml.etree.ElementTree as ET

def parse_xml(web_data):
	if len(web_data) == 0:
		return None
	xmlData = ET.fromstring(web_data)
	msg_type = xmlData.find('code_lang').text
	if msg_type == "python":
		return PythonMsg(xmlData)
	else:
		print("[receive.py] Unknown data type")

class Msg(object):
	def __init__(self, xmlData):
		self.code_base = xmlData.find('code_base').text
		self.code_lang = xmlData.find('data.code_lang').text
		self.code_param = xmlData.find('data.code_param').text
		self.MsgId = xmlData.find('MsgId').text
#		print("[receive.py] -> code_base = %s, code_lang = %s, code_param = %s, MsgId = %s" %(self.code_base, self.code_lang, self.code_param, self.MsgId))


class PythonMsg(Msg):
	def __init__(self, xmlData):
		Msg.__init__(self, xmlData)
	#	self.code_base = xmlData.find('code_base').text.encode('utf-8')
		print("[receive.py] -> code_base = %s, code_lang = %s, code_param = %s, MsgId = %s" %(data.code_base, data.code_lang, data.code_param, data.MsgId))

if __name__ == "__main__":
	pass
