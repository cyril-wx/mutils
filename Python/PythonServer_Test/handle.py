# -*- coding:UTF-8 -*-
# handle.py

import hashlib
import web
import reply
import receive
import os
#import commands
import subprocess

basepath=os.path.abspath(os.path.dirname(__file__))  # 当前文件所在绝对路径

class Handle(object):
	def GET(self):
		try:
			data = web.input()
			if len(data) == 0:
				return "Welcome to chinared.xyz."
			print("[handle.py] -> data = ",data)
			print("type(data) = ", type(data))
			'''
			code_base = data.code_base
			code_lang = data.code_lang
			code_param = data.code_param
			MsgId = data.MsgId
			'''
			code_base = data.code
			code_lang = 'python'
			code_param = None
			MsgId= '1001'
			print("[handle.py] -> code_base = ", code_base , " code_lang = ", code_lang, " code_param = ", code_param, "  MsgId = ", MsgId)
			global basepath
			script_path=basepath + "/test.sh"
			
		#	script = "echo \'", code_base, "\' > ", script_path, " ; echo \'helloworld\' | sudo -S chmod 777 ", script_path, " ; script_path;" 
#			script = "{}{}{} {} {} {} {} {}".format("echo '", code_base, "' >", script_path, ";", "echo 'helloworld' | sudo -S chmod 777 ", ";", script_path)
#			print (''.join(script))

			with open(script_path, 'w') as f:
				f.write(''.join(code_base))
			script = " {} {} {} {}".format( "echo 'Cyril2018' | sudo -S chmod 777 ", script_path, ";", script_path)
			info=subprocess.check_output(''.join(code_base), shell=True, stderr=subprocess.STDOUT)
			result="""
<html>
<head></head>
<body>
<p>%s</p>
</body>
</html>""" %(info)
			
			with open('/Users/gdlocal1/Desktop/Cyril/Coding/Web/codetest/loadtext.htm', 'w') as f:
                                f.write(result)
		#	return info
		except Exception as e:
			print(e)
			return e

	def POST(self):
		try:
			webData = web.data()
			print("Handle Post webdata is ", webData)
			recMsg = receive.parse_xml(webData)
			if isinstance(recMsg, receive.Msg):
				data.code_base = data.code_base
				data.code_lang = data.code_lang
				data.code_param = data.code_param
				data.MsgId = data.MsgId
				
				if recMsg.code_lang == "python":
					content = recMsg.Content
					content = content.decode("utf-8")
					replyMsg = reply.TextMsg(content)
					return replyMsg.send()
			else:
				print("Test 1...")
		except Exception as e:
			return e
'''
	def get_status_output(*args, **kwargs):
		p = subprocess.Popen(*args, **kwargs)
		stdout, stderr = p.communicate()
		return p.returncode, stdout, stderr
'''

if __name__ == "__main__":
	print("Test handle.py")
