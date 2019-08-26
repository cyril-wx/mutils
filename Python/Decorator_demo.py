
# -*- coding:utf-8 -*-

# 类装饰器示例

import functools,os
def checkLogFileExists(user):
	"""
	# MyLogger类的装饰器，带参数传递
	# 检测Log文件是否存在，若不存在则自动创建
	:param func:
	:return:
	"""
	def decorator(func):
		@functools.wraps(func)
		def wrapper(*args, **kw):
			log_obj = args[0]
			log_path = args[1]
			logF = log_path + "/" + log_obj

			## 如果log文件不存在需创建，否则logging.FileHandler无法主动输出log文件
			if not os.path.exists(logF):
				with open(logF, "w") as f:
					f.write("")
					print("[User:%s]Log文件不存在，已自动创建：%s" % (user,logF))
			else:
				print("[User:%s]Log文件存在，skip自动创建：%s" % (user,logF))
			return func(*args, **kw)

		return wrapper
	return decorator

@checkLogFileExists("cyril")
class MyLogger(object):
    def __init__(self, log_obj, log_path="/tmp"):
        print("MyLogger called, Log_Fpath=%s" %log_path+"/"+log_obj)
    pass

mlog = MyLogger("test.1.log", "/tmp")