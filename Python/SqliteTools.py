# -*- coding:utf-8 -*-
import sqlite3
import os
import re
#import weakref
import jc
from jc import csv_rw
from jc import utils

class SqliteHelper(object):

    db = None
    db_Name = None
    conn = None

    def __init__(self, database):
        self.mlog = utils.my_logger("SqliteHelper")
        if not os.path.exists(database):
            self.mlog.exception("Database: %s not exists." % database)
            #return
        self.db = database
        self.db_Name = os.path.split(database)[1].split(".")[0]
        self.conn = sqlite3.connect(database=self.db)
        self.c = self.conn.cursor()
        self.mlog.info("Database: %s connecting." % self.db)

    def __del__(self):
        if self.c:
            self.mlog.info("Cursor closed.")
            self.c.close()
        if self.conn:
            self.mlog.info("Database [%s] closed." % self.db)
            self.conn.close()

    def createTable_Panic(self, tableName):
        """
        # (Panic报告建表专用)创建PANIC_REPORT数据表
        # `SrNm`, `Radar` 作为联合主键
        :return:
        """
        self.c.execute('''CREATE TABLE %s
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
        ''' %tableName)
        self.mlog.info ("Table created successfully")
        self.conn.commit()


    def select(self, table="PANIC_REPORT", args=[], conditions=""):
        """
        # 查询模式
        # 支持 "*" 查询
        # 支持 条件 查询
        :param table:
        :param args: 支持 "*" 查询，Ex: args=["*"]
        :param conditions: conditions 为标准sql查询条件字串, 不带"WHERE" 关键字, Ex: `OSD Version`>'400'
        :return: cursor: iter
        """
        if not args:
            self.mlog.exception("args is none")
            return

        select_items = ""
        for i in args:
            if i.strip() != "":
                select_items = "%s`%s`, " %(select_items, i.strip())
        select_items = select_items.strip()[:-1]    # 去掉结尾的逗号
        if select_items.__contains__("*"):
            select_items = "*"

        if conditions != "":   # 带条件查询
            sql = "SELECT %s from %s WHERE %s ;" % (select_items, table, conditions)
        else:           # 不带条件查询
            sql = "SELECT %s from %s ;" %(select_items,table)
        self.mlog.info ("sql: %s" %sql )
        cursor = self.c.execute(sql)

        return cursor



    def insert(self, valueDict={}, table="PANIC_REPORT"):
        # kwargs 支持两种模式。
        # 1。 单记录插入  {"NO":"1", "Location":"FXGL", "Validation":"Offline"...}
        # 2。 多记录插入  { "1": {"NO":"1", "Location":"FXGL", "Validation":"Offline"...}}
        #               { "2": {"NO": "1", "Location": "FXGL", "Validation": "Offline"...}}
        #  多记录插入key值必须是int 或能 int() 转换成功
        # 主键：PRIMARY KEY (`SrNm`, `Radar`)
        if not valueDict:
            self.mlog.error("插入值（valueDict）不能为空")
            return
        self.mlog.info ("Opened database successfully")

        # 多记录插入模式
        try:
            if valueDict[1] != "":
                for record_x in valueDict.values():
                    item_keys = [ key for key in record_x ]
                    insert_item_keys = ""
                    insert_item_values = ""
                    for key in item_keys:
                        insert_item_keys = "%s`%s`, " %(insert_item_keys, key)
                        insert_item_values = "%s'%s', " %(insert_item_values, record_x[key])
                    insert_item_values = insert_item_values.strip()[:-1]
                    insert_item_keys = insert_item_keys.strip()[:-1]
                    sql = "INSERT INTO %s (%s) VALUES (%s) ;" %(table, insert_item_keys, insert_item_values)
                    self.mlog.info("sql: %s" %sql)
                    self.c.execute(sql)

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
            sql = "INSERT INTO %s (%s) VALUES (%s) ;" % (table, insert_item_keys, insert_item_values)
            self.mlog.info("sql: %s" % sql)

        finally:
            self.conn.commit()
            self.mlog.info("Total number of rows insert :%s" %self.conn.total_changes)

    def update(self, valueDict={}, indexKey={}, table="PANIC_REPORT"):
        """
        # 仅支持单记录更新  {"NO":1, "Location":"FXGL", "Validation":"Offline"...}
        # 支持条件约束（索引）。条件仅限 AND，不支持 OR NOT IN等。
        # 主键：PRIMARY KEY (`SrNm`, `Radar`)
        :param valueDict: 更新值 字典 （支持多记录）
        :param indexKey: 插入索引键
        :param table:
        :return:
        """
        if not valueDict or not indexKey:
            self.mlog.error("插入值（valueDict）和 索引键（indexKey） 均不能为空")
            return
        self.mlog.info ("Opened database successfully")

        try:
            # 多记录模式
            if valueDict[1] != "":
                for record_x in valueDict.keys():  ## row records
                    item_keys = valueDict[record_x]  ## column keys
                    one_val = []
                    one_cond = []
                    for x in indexKey[record_x].keys():
                        one_cond.append("`%s`='%s'" % (x, indexKey[record_x][x]))

                    for key in item_keys.keys():
                        one_val.append("`%s`='%s'" % (key, item_keys[key]))

                    sql = "UPDATE %s SET %s WHERE %s;" % (table, ", ".join(one_val), " AND ".join(one_cond))
                    self.mlog.info("sql: %s" % sql)
                    self.c.execute(sql)
        except KeyError:
            one_cond = []
            for x in indexKey.keys():
                one_cond.append("`%s`='%s'" % (x, indexKey[x]))
            one_val = []
            for key in valueDict.keys():
                one_val.append("`%s`='%s'" % (key, valueDict[key]))
            sql = "UPDATE %s SET %s WHERE %s;" % (table, ", ".join(one_val), " AND ".join(one_cond))
            self.mlog.info("sql: %s" % sql)
            self.c.execute(sql)

        finally:
            self.conn.commit()
            self.mlog.info("Total number of rows insert :", self.conn.total_changes)


    def readCSVs(self, path):
        """
        # 读取CSV
        # 支持目录下csv批量读取，但是强烈建议所有csv格式一致。
        :param path: 目录或文件
        :return: dict{}
        """
        if not os.path.exists(path):
            self.mlog.error("Path is not found: %s" %path)
            return

        csvs = []
        rows_dict = {}
        id = 0

        if os.path.isdir(path):     # 输入路径是目录
            for file in os.listdir(path):  # 不仅仅是文件，当前目录下的文件夹也会被认为遍历到
                #self.mlog.info (file)
                if re.search(r"(.*).csv", file):
                    csvs.append(path + "/" + file)
        else:                       # 输入路径是文件
            csvs.append(path)

        for csv in csvs:
            data = csv_rw.readCSVFile(csv)
            title = data[0]
            content = data[1:]
            tag = 0
            for c in content:
                row_dict = {}
                for ti in range(0, len(title) - 1):
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
        if (not os.path.exists(data_file)) or os.path.isdir(data_file) or (not re.search(r"(.*).csv", data_file)):
            self.mlog.error("createTable: data_file must be a csv file.")
            return False

        # 导入CSV文件进入PANIC_REPORT表
        info = sql_helper.readCSVs(data_file)
        column_name = info[1].keys()      # table column_name

        self.mlog.info("Opened database successfully")

        create_str = ""
        for item in column_name:
            create_str = create_str + " `%s` TEXT NULL, "%item

        create_str = "`CID` INTEGER PRIMARY KEY AUTOINCREMENT, " + create_str
        create_str = create_str.strip()[:-1]
        #self.mlog.info (create_str)
        self.c.execute("CREATE TABLE %s ( %s ); " %(tableName, create_str))
        self.conn.commit()
        self.mlog.info("Table [%s] created successfully." %tableName)
        return True


    def dropTable(self, tableName):
        sql = "DROP TABLE %s ;" %(tableName)
        self.c.execute(sql)
        self.conn.commit()
        self.mlog.info("Table [%s] dropped successfully. "%tableName)


if __name__ == "__main__":
    sql_helper = SqliteHelper("panic_report.db")

    # 创建数据库及PANIC_REPORT表
    #sql_helper.createTable_Panic()

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
    #d = sql_helper.update(valueDict=valueDict, indexKey=indexKey, table="PANIC_REPORT")
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

    sql_helper.mlog.info("###### 创建表 PANIC_REPORT ######")
    tableName = "D42_DVT_PANIC_REPORT"
    try:
        sql_helper.createTable_Panic(tableName)
    except sqlite3.OperationalError:
        sql_helper.mlog.error("Table [PANIC_REPORT] already exists in database. Create failed.")

    sql_helper.mlog.info("###### 导入数据 ######")
    csv_f = "/Users/gdlocal1/Desktop/Panic/0724/Macan_DVT_Panic_Tracking_Report_0724"
    data = sql_helper.readCSVs(csv_f)
    try:
        sql_helper.insert(data, tableName)
    except sqlite3.IntegrityError as e:
        sql_helper.mlog.error("Dump data into table [%s] failed: %s" % (tableName, e))

    sql_helper.mlog.info("###### 查询所有数据 ######")
    select_data = [ i for i in sql_helper.select(table=tableName, args=["*"]) ]
    print( select_data )
    sql_helper.mlog.info("###### 查询所有母雷达 ######")
    print( [ i[0] for i in sql_helper.select(table=tableName, args=["Umbrella Radar"]) if i[0] != "" and i[0] != "/"])

    sql_helper.mlog.info("###### 导出数据 ######")
    export_path = "/tmp/test.csv"
    export_data = select_data
    csv_rw.writeCSVFile(export_path, export_data)





