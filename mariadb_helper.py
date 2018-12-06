#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import pymysql

class MariadbHelper(object):
        '''
        Mariadb 数据库 连接助手
        '''
        db = None
        config = {
                'host':'127.0.0.1',
                'port':3306,    ## MySQL默认端口
                'user':'root',  ## mysql默认用户名
                'password':'zxc12345',
                'db':'EISP_PERS',       ## 数据库
                'charset':'utf8', }     ## 如果不设置字符集则会导致输出中文乱码
        # 初始化db连接
        def __init__(self, config={}):
                self.db = pymysql.connect(**self.config)
                print("Connecting mysql.")

        # 析构函数
        def __del__(self):
                '''
                del析构函数，并不是在del a对象的时候就会调用该析构函数
                只有当该对象的引用计数为0时才会调用析构函数，回收资源
                析构函数被python的垃圾回收器销毁的时候调用。当某一个对象没有被引用时，垃圾回收器自动回收资源，调用析构函数
                 '''
                self.db.close() # 销毁对象时同时关闭数据库连接
                print("Disconnecting mysql.")

        def sql_select(self, col_names=[], table_name='', select_conditions=[{'','','',},]):
                '''
                执行 指定 sql 查询任务：
                暂未实现条件查询
                '''
                a = ''
                if col_name:
                        for  col_name in col_names:
                                a = a + col_name + ","
                        a = a[0:-1]
                else:
                        a = "*"
                if not table_name:  # 如果table_name为空, 则直接中断返回
                        return -1
                sql_cmd = "select " + a + " from " + table_name
                #print("sql_select -> sql_cmd = ", sql_cmd)
                exec_sql_cmd(sql_cmd)

                return data

        def exec_sql_cmd(self, sql_cmd):
                cursor = self.db.cursor()  #创建游标使用的cursor方法
                if not sql_cmd:
                        return -2
                try:
                        cursor.execute(sql_cmd)
                        self.db.commit()  # 提交数据库执行更新
                #       data = cursor.fetchone() # 使用 fetchone() 方法获取单条数据.
                        data = cursor.fetchall() # 使用 fetchall() 方法获取所有数据.
                        return data
                except Exception as e:
                        print("exec_sql_cmd -> ", e)
                        self.db.rollback()  # 如果发生错误则回滚
                finally:
                        cursor.close()

if __name__ == '__main__':
    
        mh = MariadbHelper()
        data = mh.exec_sql_cmd("""
                select * from punch_info;
""")

        print("TestResult: ", data)
        pass
        