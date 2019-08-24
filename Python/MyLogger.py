class MyLogger(object):
	"""
	# 自定义log输出器
	# 单例模式
	"""
	_instance = None
	_log_obj = None
	_log_path = None

	mlog = None
	def __new__(cls, *args, **kw):
		if cls._instance is None:
			cls._instance = object.__new__(cls, *args, **kw)
		cls._log_obj = args[0]
		cls._log_path = args[1]
		return cls._instance

	def __init__(self, log_obj, log_path="/tmp"):
		if self.mlog is None:
			self.mlog = self.my_logger()
		pass

	def my_logger(self):
		"""
		# 自定义log显示及输出
		:param log_obj: object name who exec logger
		:param log_path: log output filepath
		:return: logger obj
		"""
		logger = logging.getLogger(self._log_obj)
		# print(logger.handlers)
		logger.setLevel(logging.INFO)

		console_handle = logging.StreamHandler()
		file_handle = logging.FileHandler(filename=self._log_path + "/" +self._log_obj + ".log")
		formatter = logging.Formatter('%(asctime)s - %(name)s:%(funcName)s - %(levelname)s - %(message)s ')
		console_handle.setFormatter(formatter)
		file_handle.setFormatter(formatter)
		logger.addHandler(console_handle)
		logger.addHandler(file_handle)

		return logger


if __name__ == "__main__":

	while True:
		# MyLogger 是单例模式 实现，否则每次新创建自定义logging一次都会导致log输出重复度加1
		mlog = MyLogger("test", "/tmp").mlog
		mlog.info("helloworld")
		mlog.info("testing log")
		import time
		time.sleep(3)