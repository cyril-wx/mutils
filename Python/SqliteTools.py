# !/usr/bin/env python
# -*- coding:UTF-8 -*-
"""
#**********************************************	#
# SqliteTools.py | Sqlite 连接工具       	 	#
#----------------------------------------------	#
# @Author: Cyril				                #
# @GitLab: https://gitlab.com/cyril_j           #
# @Create: 2019-06-26				            #
# @Modify: 2019-08-24                           #
# @Tips:                                        #
#**********************************************	#
"""

import sqlite3
import os
import re
import logging
from jc import csv_rw
from jc import utils


class SqliteHelper(object):
	db = None
	db_Name = None
	conn = None
	mlog = None

	def __init__(self, database):

		try:
			database_pdir = os.path.split(database)[0]
			self.mlog = MyLogger("SqliteHelper", database_pdir).mlog
		except:
			print ("Database_file-[%s] is not exists." %database)
			exit(1)

		self.mlog.info("###### 连接数据库 ######")
		if not os.path.exists(database):
			self.mlog.exception("Database-[%s] not exists." % database)
		# return
		self.db = database
		self.db_Name = os.path.split(database)[1].split(".")[0]
		self.conn = sqlite3.connect(database=self.db)
		self.mlog.info("Opened database-[%s] successfully." % self.db_Name)
		self.mlog.info("Database path=%s" %self.db)

	def __del__(self):
		if self.conn:
			self.mlog.info("Closing Database-[%s]." % self.db_Name)
			self.conn.close()

	def createTable_Panic(self, tableName):
		"""
		# (Panic报告建表专用)创建PANIC_REPORT数据表
		# `SrNm`, `Radar` 作为联合主键
		:return:
		"""
		self.mlog.info("###### 创建数据库表 ######")
		sql = '''CREATE TABLE %s
               (
               `NO` TEXT NULL,
               `Location`           TEXT     NULL,
               `Validation`           TEXT     NULL,
               `Station`           TEXT     NULL,
               `Config`           TEXT     NULL,
               `UNIT#`           TEXT     NULL,
               `SrNm`           TEXT     NOT NULL,
               `Bundle`           TEXT     NULL,
               `OSD Version`           TEXT     NULL,
               `Panic info`           TEXT     NULL,
               `Umbrella Radar`           TEXT     NULL,
               `Radar`           TEXT    NOT NULL,
               `Status/Action`           TEXT     NULL,
               `Comment/Solution`           TEXT     NULL,
               `Date`           TEXT     NULL,
               PRIMARY KEY (`SrNm`, `Radar`) );
        ''' % tableName

		try:
			self.mlog.info("Creating Table-[%s]" % tableName)
			self.conn.execute(sql)
			self.conn.commit()
			self.mlog.info("Table-[%s] created successfully" % tableName)
		except sqlite3.OperationalError:
			self.mlog.exception("Table-[%s] already exists in database. Create failed." % tableName)


	def select(self, tableName="PANIC_REPORT", args=[], conditions=""):
		"""
		# 查询模式
		# 支持 "*" 查询
		# 支持 条件 查询
		:param tableName:
		:param args: 支持 "*" 查询，Ex: args=["*"]
		:param conditions: conditions 为标准sql查询条件字串, 不带"WHERE" 关键字, Ex: `OSD Version`>'400'
		:return: cursor: iter
		"""
		self.mlog.info("###### 查询数据库 ######")
		if not args:
			self.mlog.exception("args is none")
			return

		select_items = ""
		for i in args:
			if i.strip() != "":
				select_items = "%s`%s`, " % (select_items, i.strip())
		select_items = select_items.strip()[:-1]  # 去掉结尾的逗号
		if select_items.__contains__("*"):
			select_items = "*"

		if conditions != "":  # 带条件查询
			sql = "SELECT %s from %s WHERE %s ;" % (select_items, tableName, conditions)
		else:  # 不带条件查询
			sql = "SELECT %s from %s ;" % (select_items, tableName)

		data = None
		cur = self.conn.cursor()
		try:
			self.mlog.info("Select data from Table-[%s]\n" % (tableName))
			cursor = cur.execute(sql)
			self.conn.commit()
			self.mlog.info("Select data from Table-[%s] successful" % (tableName))
			data = cur.fetchall()
		except sqlite3.SQLITE_SELECT as e:
			self.mlog.exception("Select data from Table-[%s] failed\n%s" % (tableName, sql))
		finally:
			if cur:
				cur.close()

		return data

	def insert(self, valueDict={}, tableName="PANIC_REPORT"):
		# kwargs 支持两种模式。
		# 1。 单记录插入  {"NO":"1", "Location":"FXGL", "Validation":"Offline"...}
		# 2。 多记录插入  { "1": {"NO":"1", "Location":"FXGL", "Validation":"Offline"...}}
		#               { "2": {"NO": "1", "Location": "FXGL", "Validation": "Offline"...}}
		#  多记录插入key值必须是int 或能 int() 转换成功
		# 主键：PRIMARY KEY (`SrNm`, `Radar`)
		self.mlog.info("###### 插入数据库 ######")

		if not valueDict:
			self.mlog.error("插入值（valueDict）不能为空")
			return

		# 多记录插入模式
		try:

			if valueDict[1] != "":
				for record_x in valueDict.values():
					item_keys = [key for key in record_x]
					insert_item_keys = ""
					insert_item_values = ""
					for key in item_keys:
						insert_item_keys = "%s`%s`, " % (insert_item_keys, key)
						insert_item_values = "%s'%s', " % (insert_item_values, record_x[key])
					insert_item_values = insert_item_values.strip()[:-1]
					insert_item_keys = insert_item_keys.strip()[:-1]
					sql = "INSERT INTO %s (%s) VALUES (%s) ;" % (tableName, insert_item_keys, insert_item_values)

					## 这里需要无需处理异常，出现查询失败异常需上抛至调用点使用 try-excption 处理
					self.mlog.info("Insert data into Table-[%s]\n%s" % (tableName, sql))
					self.conn.execute(sql)
					self.mlog.info("Insert data into Table-[%s] successfully" % tableName)

				self.conn.commit()

		# 单记录插入模式
		except KeyError:
			item_keys = valueDict.keys()

			insert_item_keys = ""
			insert_item_values = ""
			for key in item_keys:
				insert_item_keys = "%s`%s`, " % (insert_item_keys, key)
				insert_item_values = "%s'%s', " % (insert_item_values, valueDict[key])
			insert_item_values = insert_item_values.strip()[:-1]
			insert_item_keys = insert_item_keys.strip()[:-1]
			sql = "INSERT INTO %s (%s) VALUES (%s) ;" % (tableName, insert_item_keys, insert_item_values)

			## 这里需要无需处理异常，出现查询失败异常需上抛至调用点使用 try-excption 处理
			self.mlog.info("Insert data into Table-[%s]\n%s" % (tableName, sql))
			self.conn.execute(sql)
			self.conn.commit()
			self.mlog.info("Insert data into Table-[%s] successfully" % tableName)

		finally:
			self.mlog.info("Total number of rows insert :%s" % self.conn.total_changes)

	def update(self, valueDict={}, indexKey=[], table="PANIC_REPORT"):
		"""
		# 支持条件约束（索引）。条件仅限 AND，不支持 OR NOT IN等。
		# 主键：PRIMARY KEY (`SrNm`, `Radar`)
		:param valueDict: 更新值 字典 （支持多记录）
		:param indexKey: 更新索引键(即主键)
		:param table:
		:return:
		"""
		self.mlog.info("###### 更新数据库表 ######")
		if not valueDict or not indexKey:
			self.mlog.error("插入值（data）和 索引键（indexKey） 均不能为空")
			return

		# 多记录插入模式
		cur = self.conn.cursor()
		try:
			if valueDict[1] != "":
				for record_x in valueDict.values():
					item_keys = [key for key in record_x]

					one_val = []
					one_cond = []
					for key in item_keys:
						one_val.append("`%s`='%s'" % (key, record_x[key]))

					one_cond.append("`%s`='%s'" % (indexKey[0], record_x[indexKey[0]]))
					one_cond.append("`%s`='%s'" % (indexKey[1], record_x[indexKey[1]]))
					sql = "UPDATE %s SET %s WHERE %s;" % (table, ", ".join(one_val), " AND ".join(one_cond))

					try:
						self.mlog.info("Start update: \n%s"%sql)
						cur.execute(sql)
						self.mlog.info ("Update successful")
					except sqlite3.SQLITE_UPDATE as e:
						self.mlog.exception("%s. \nsql:%s" % (e, sql))
						continue
				self.conn.commit()

		except KeyError:
			one_cond = []
			for x in indexKey.keys():
				one_cond.append("`%s`='%s'" % (x, indexKey[x]))
			one_val = []
			for key in valueDict.keys():
				one_val.append("`%s`='%s'" % (key, valueDict[key]))
			sql = "UPDATE %s SET %s WHERE %s;" % (table, ", ".join(one_val), " AND ".join(one_cond))

			self.mlog.info("Start update: \n%s"%sql)
			cur.execute(sql)
			cur.commit()
			self.mlog.info("Update successful")

		finally:
			self.mlog.info("Total number of rows update: %s", self.conn.total_changes)
			if cur:
				cur.close()


	def readCSVs(self, path):
		"""
		# 读取CSV
		# 支持目录下csv批量读取，但是强烈建议所有csv格式一致。
		:param path: 目录或文件
		:return: dict{}
		"""
		self.mlog.info("###### 读取外部数据CSV文件 ######")
		if not os.path.exists(path):
			self.mlog.error("Path is not found: %s" % path)
			return

		csvs = []
		rows_dict = {}
		id = 0

		if os.path.isdir(path):  # 输入路径是目录
			for file in os.listdir(path):  # 不仅仅是文件，当前目录下的文件夹也会被认为遍历到
				# self.mlog.info (file)
				if re.search(r"(.*).csv", file):
					csvs.append(path + "/" + file)
		else:  # 输入路径是文件
			csvs.append(path)

		for csv in csvs:
			data = csv_rw.readCSVFile(csv)
			title = data[0]
			content = data[1:]
			tag = 0
			for c in content:
				row_dict = {}
				for ti in range(0, len(title)):
					row_dict.update({title[ti]: content[tag][ti]})

				rows_dict.update({id + 1: row_dict})
				id += 1
				tag += 1
		# print (rows_dict)
		return rows_dict

	def createTable(self, data_file, tableName):
		"""
		 # 根据CSV文件自动创建数据表, 并插入数据。
		 # `CID` 为自增主键列
		:param data_file: 必须为CSV文件
		:param tableName: 表名
		:return: True/False
		"""
		self.mlog.info("###### 创建数据库表 ######")
		if (not os.path.exists(data_file)) or os.path.isdir(data_file) or (not re.search(r"(.*).csv", data_file)):
			self.mlog.error("createTable: data_file must be a csv file.")
			return False

		# 导入CSV文件进入PANIC_REPORT表
		info = self.readCSVs(data_file)
		column_name = info[1].keys()  # table column_name

		create_str = ""
		for item in column_name:
			create_str = create_str + " `%s` TEXT NULL, " % item

		create_str = "`CID` INTEGER PRIMARY KEY AUTOINCREMENT, " + create_str
		create_str = create_str.strip()[:-1]

		self.mlog.info("Creating table-[%s]")
		self.conn.execute("CREATE TABLE %s ( %s ); " % (tableName, create_str))
		self.conn.commit()
		self.mlog.info("Create table-[%s] successfully." % tableName)
		return True

	def dropTable(self, tableName):
		self.mlog.info("###### 删除数据库表 ######")
		sql = "DROP TABLE %s ;" % (tableName)

		self.mlog.info("Dropping table-[%s]")
		self.conn.execute(sql)
		self.conn.commit()
		self.mlog.info("Drop table-[%s] successfully. " % tableName)


# 测试模块功能
def test():
	sql_helper = SqliteHelper("panic_report.db")

	# 创建数据库及PANIC_REPORT表
	# sql_helper.createTable_Panic()

	# 导入CSV文件进入PANIC_REPORT表
	# info = sql_helper.readCSVs("/Users/gdlocal1/Desktop/Cyril/TMP/Macan_DVT_Panic_Tracking_Report_0719_patrick")

	# 测试insert
	# test_info = { "1": {"Location":"FXGL", "Validation":"Offline"}}
	# print (type(test_info))
	# sql_helper.insert(info, table="PANIC_REPORT")
	# test_info = {"UNIT#":"9001","SrNm":"C390001", "Umbrella Radar":"123", "Radar":"123", "OSD Version":"0032"}
	# sql_helper.insert(test_info, table="PANIC_REPORT")

	# 测试select
	#   a = sql_helper.select(table="PANIC_REPORT", args=["UNIT#","SrNm", "Umbrella Radar", "Radar", "OSD Version"])
	#   b = sql_helper.select(table="PANIC_REPORT", args=["*"])
	#    c = sql_helper.select(table="PANIC_REPORT", args=["*"], conditions="`OSD Version`>'400'")

	# 测试update
	#    valueDict = {"UNIT#":"9001","SrNm":"C390001", "Umbrella Radar":"123"}
	#   indexKey = {"SrNm":"C390001", "Radar":"123"}
	## 单记录update测试
	# d = sql_helper.update(valueDict=valueDict, indexKey=indexKey, table="PANIC_REPORT")
	## 多记录update测试
	#    valueDict = {1:{"UNIT#": "9001", "SrNm": "C390001", "Umbrella Radar": "123"}}
	#    indexKey = {1:{"SrNm": "C390001", "Radar": "123"}}
	#    d = sql_helper.update(valueDict=valueDict, indexKey=indexKey, table="PANIC_REPORT")

	#   # 测试插入表
	#    data = sql_helper.readCSVs(csv_f)
	#    sql_helper.insert(data, table="TEST")
	#    b = sql_helper.select(table="TEST", args=["*"])
	#    print("TEST SELECT")
	#    for i in b:
	#        print(i)
	#    sql_helper.dropTable("TEST")


	#sql_helper.mlog.info("###### 创建表 PANIC_REPORT ######")
	tableName = "D43_DVT_PANIC_REPORT"
	sql_helper.createTable_Panic(tableName)



	#sql_helper.mlog.info("###### 导入数据 ######")
	csv_f = "/Users/gdlocal1/Desktop/Panic/0724/Macan_DVT_Panic_Tracking_Report_0724"
	data = sql_helper.readCSVs(csv_f)
	try:
		sql_helper.insert(data, tableName)
	except sqlite3.IntegrityError:   # 如果使用insert失败，说明数据需要更新
		sql_helper.update(data, indexKey=["SrNm", "Radar"], table=tableName)


	#sql_helper.mlog.info("###### 查询所有数据 ######")
	select_data = sql_helper.select(tableName, args=["*"])
	print(select_data)

	exit(0)

	#sql_helper.mlog.info("###### 查询所有母雷达 ######")
	print([i[0] for i in sql_helper.select(table=tableName, args=["Umbrella Radar"]) if i[0] != "" and i[0] != "/"])

	#sql_helper.mlog.info("###### 导出数据 ######")
	export_path = "/tmp/test.csv"
	export_data = select_data
	try:
		os.remove(export_path)
	except:
		pass
	csv_rw.writeCSVFile(export_path, export_data)


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
	# 测试SqliteTools模块
	test()


