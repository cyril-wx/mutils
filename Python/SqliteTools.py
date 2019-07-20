# -*- coding:utf-8 -*-
import sqlite3
import os
import re
#import weakref
import jc
from jc import csv_rw

class SqliteHelper(object):

    db = None
    conn = None

    def __init__(self, database):
        if not os.path.exists(database):
            print("Database: %s not exists." % database)
            #return
        self.db = database
        self.conn = sqlite3.connect(database=self.db)
        print("Database: %s connecting." % self.db)

    def __del__(self):
        if self.conn:
            print("Database: %s closed." %self.db)
            self.conn.close()


    def createTable_Panic(self):
        """
        # 创建PANIC_REPORT数据表
        # `SrNm`, `Radar` 作为联合主键
        :return:
        """
        if not self.conn:
            self.conn = sqlite3.connect(database=self.db)
        c = self.conn.cursor()
        print("Opened database successfully")

        c.execute('''CREATE TABLE PANIC_REPORT
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
        ''')
        print ("Table created successfully")
        self.conn.commit()
        self.conn.close()




    def select(self, table="PANIC_REPORT", args=[], conditions=""):
        """
        # 查询模式
        # 支持 "*" 查询
        # 支持 条件 查询
        :param table:
        :param args: 支持 "*" 查询，Ex: args=["*"]
        :param conditions: conditions 为标准sql查询条件字串, 不带"WHERE" 关键字, Ex: `OSD Version`>'400'
        :return:
        """
        if not args:
            return
        self.conn = sqlite3.connect(database=self.db)
        c = self.conn.cursor()
        print ("Opened database successfully")

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
        print ("sql: %s" %sql )
        cursor = c.execute(sql)

        for row in cursor:
            yield row
        self.conn.close()
        return row


    def insert(self, valueDict={}, table="PANIC_REPORT"):
        # kwargs 支持两种模式。
        # 1。 单记录插入  {"NO":"1", "Location":"FXGL", "Validation":"Offline"...}
        # 2。 多记录插入  { "1": {"NO":"1", "Location":"FXGL", "Validation":"Offline"...}}
        #               { "2": {"NO": "1", "Location": "FXGL", "Validation": "Offline"...}}
        #  多记录插入key值必须是int 或能 int() 转换成功
        # 主键：PRIMARY KEY (`SrNm`, `Radar`)
        if not valueDict:
            print("插入值（valueDict）不能为空")
            return
        self.conn = sqlite3.connect(database=self.db)
        c = self.conn.cursor()
        print ("Opened database successfully")

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
                    print("sql: %s" %sql)
                    c.execute(sql)

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
            print("sql: %s" % sql)
            c.execute(sql)

        finally:
            self.conn.commit()
            print("Total number of rows insert :", self.conn.total_changes)
            self.conn.close()

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
            print("插入值（valueDict）和 索引键（indexKey） 均不能为空")
            return
        self.conn = sqlite3.connect(database=self.db)
        c = self.conn.cursor()
        print ("Opened database successfully")

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
                    print("sql: %s" % sql)
                    c.execute(sql)
        except KeyError:
            one_cond = []
            for x in indexKey.keys():
                one_cond.append("`%s`='%s'" % (x, indexKey[x]))
            one_val = []
            for key in valueDict.keys():
                one_val.append("`%s`='%s'" % (key, valueDict[key]))
            sql = "UPDATE %s SET %s WHERE %s;" % (table, ", ".join(one_val), " AND ".join(one_cond))
            print("sql: %s" % sql)
            c.execute(sql)

        finally:
            self.conn.commit()
            print("Total number of rows insert :", self.conn.total_changes)
            self.conn.close()

    def readCSVs(self, dir):
        if not os.path.isdir(dir):
            print("Input path is not dir. exit.")
            return

        csvs = []
        rows_dict = {}

        id = 0
        for file in os.listdir(dir):  # 不仅仅是文件，当前目录下的文件夹也会被认为遍历到
            print (file)
            if re.search(r"(.*).csv", file):
                csvs.append(dir + "/" + file)
                data = csv_rw.readCSVFile(dir + "/" + file)
                title = data[0]
                content = data[1:]
                tag = 0
                for c in content:
                    row_dict = {}
                    for ti in range(0, len(title)-1):
                        row_dict.update({ title[ti]: content[tag][ti]} )

                    rows_dict.update({id+1:row_dict})
                    id += 1
                    tag += 1
        # print (rows_dict)
        return rows_dict

    def createTable(self, data_dict):
        """
        # 创建PANIC_REPORT数据表
        # `SrNm`, `Radar` 作为联合主键
        :return:
        """

        # 导入CSV文件进入PANIC_REPORT表
        # info = sql_helper.readCSVs("/Users/gdlocal1/Desktop/Cyril/TMP/Macan_DVT_Panic_Tracking_Report_0719_patrick")



        if not self.conn:
            self.conn = sqlite3.connect(database=self.db)
        c = self.conn.cursor()
        print("Opened database successfully")

        c.execute('''CREATE TABLE PANIC_REPORT
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
        ''')
        print("Table created successfully")
        self.conn.commit()
        self.conn.close()


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
    valueDict = {"UNIT#":"9001","SrNm":"C390001", "Umbrella Radar":"123"}
    indexKey = {"SrNm":"C390001", "Radar":"123"}
    ## 单记录update测试
    #d = sql_helper.update(valueDict=valueDict, indexKey=indexKey, table="PANIC_REPORT")
    ## 多记录update测试
    valueDict = {1:{"UNIT#": "9001", "SrNm": "C390001", "Umbrella Radar": "123"}}
    indexKey = {1:{"SrNm": "C390001", "Radar": "123"}}
    d = sql_helper.update(valueDict=valueDict, indexKey=indexKey, table="PANIC_REPORT")

"""
    count = 0
    try:
        while True:
            print (next(c))
            count += 1
    except:
        print("Finish")
        pass

    print("count = %s" %count)
"""



