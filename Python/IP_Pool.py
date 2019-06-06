#!/usr/bin/env python
# -*- coding:UTF-8 -*-

import os
import sys

class IP_Pool:
    """
    # 在配置文件中，逐行填入所有IP即可激活IP_Pool
    """
    sys_ver = ""
    conf_path = ""
    def __init__(self, conf_path):
        self.sys_ver = sys.version
        if os.path.exists(conf_path):
            self.conf_path = conf_path
        else:
            exit(1)

    def resolveData(self):
        """
        # 获取所有的IP及状态
        :return: list(tuple(ip_tuple_list)) or None
        """
        ip_tuple_list = []
        with open(self.conf_path, "r") as f:
            line = f.readline()
            while line:
                ip_tuple_list.append(line.strip().rstrip("\n").split(" "))
                line = f.readline()
            return  ip_tuple_list
        return None

    def getIPStats(self, IP):
        """
        # 获取IP的状态值
        :param IP: IP string.
        :return: str(stats) or None
        """
        import re
        if not re.match("\d+.\d+.\d+.\d+", IP):
            print("'IP' is invalid type.")
            exit(1)
        data = self.resolveData()
        if data:
            for item in data:
                if IP == item[0]:
                    cmd = "ping 172.21.157.72 -c1"
                    (rev,res) = readCMD([cmd], True)
                    if rev == 0:
                        return item[1]
        return None

    def setIPStats(self, IP, Stats):
        """
        # Add/Update IPStats to local IP_Pool
        # 请勿直接调用此方法
        :param IP:
        :param Stats:
        :return: True/False
        """
        import copy
        data = self.resolveData()
        if data:
            for item in data:
                if item[0] == IP :
                    print("Found IP: %s" %IP)
                    item[1] = Stats
                    return self.rewriteConfig(data)
        else:
            print("No data in config file.")
        return False

    def syncIPStats(self, file=conf_path, sync_rule="NEW_ADD",*args):
        """
        # 同步指定文件到指定所有工站 (采用强制同步)
        :param file: 指定待同步的所有文件
        :param sync_rule: 同步规则：NEW_ADD/NEW_OVERRIDE: 不检测值更新/检测是否需要更新值
        :param args: IPs(list)
        :return: success IPs(list)
        """
        #for ip in args:
        #    if ip ==


        pass

    def rewriteConfig(self, data):
        """
        # 将修改后的数据写入配置文件
        :param data:
        :return: true/false
        """
        with open(self.conf_path, "w") as f:

            if isinstance(data, str):   ## 源数据类型为 str
                f.write(data)
            elif isinstance(data, list) or isinstance(data, set): ## 源数据类型为 [["", ""], ]
                for line in data:
                    try:
                        f.write(" ".join(line)+"\n")
                    except:             ## 写入失败 将源数据类型强制转换为为 str 并写入
                        print("Writing data as list type failed and forcing writing as str.")
                        f.write(str(line)+"\n")
            else:                       ## 将源数据类型强制转换为为 str 并写入
                print("Unkown data type and writing as str.")
                f.write(str(data)+"\n")
            return True

    def getLocalHostIP(self):
        """
        # 获取本机 IP
        :return: IP(str)
        """
        cmd = "/sbin/ifconfig -a|grep inet|grep -v 127.0.0.1|grep -v inet6|awk '{print $2}'|tr -d \"addr:\" | sed -n 1p"
        IP = None
        try:
            IP = readCMD([cmd], True)[1][0]
        except Exception as e:
            print(e)
        finally:
            return IP

    def syncConfigOn2Stations(self, remoteIP, syncFileOrDir=conf_path):
        """
        # rsync同步。只适用于同步更新固定key。
        :param remoteIP:
        :param syncFileOrDir: 要同步的文件或文件夹
        :return: True/False
        """
        import re, os
        if not re.match("\d+.\d+.\d+.\d+", remoteIP):
            print("'IP' is invalid type.")
            exit(1)

        (dir, filename) = os.path.split(syncFileOrDir)
        ## -u 不同步旧版本
        sync_cmd = """
expect << EOF
set timeout 10
spawn /usr/bin/rsync -avu %s/%s gdlocal@%s:%s
expect {
	-re "Password:" { send "gdlocal\r"; exp_continue }
	-re "total size is" { exit 0}
    timeout {
        send_user "Timeout...exit.\r" ;
        exit 1
    }
	eof {
		send_user "EOF finish.\r" ;
		exit 2
	}
}
EOF
        """ %(dir, filename, remoteIP, dir)

        res = 1
        count = 0
        while count < 3:
            (res, rev) = readCMD(sync_cmd, True)
            if not res:
                return False
            count+=1
        return True

    def mergeLists(self, *args):
        """
        # merge all list data.
        :param data_1:
        :param data_2:
        :return:
        """
        merged_list = set()
        for item in args:
            for i_list in item:
                try:
                    merged_list.add(i_list)
                except Exception as e:
                    print("item-%s added failed." %str(i_list))
                    print(e)
                    continue
        return merged_list

    def mergeUpdate2Data(self):
        pass

    def fileDataCompare(self, f_1, f_2):
        """
        # 文件内容对比(仅限文本文档)
        :param f_1:
        :param f_2:
        :return:  True/False
        """
        #import hashlib
        a = None
        b = None
        try:
            f_a = open(f_1, "r")
            f_b = open(f_2, "r")

            while True:
                a = f_a.readline()
                b = f_b.readline()
                if not a and not b:
                    break
#                elif a.strip() == "" or b.strip() == "":       # 这里的作用就是检测文末是否存在空行，但影响执行效率
#                    continue
                elif a != b:
                    return False

        except Exception as e:
            print("Can't open file_1-%s or file_2-%s" %(f_1, f_2))
            print(e)
            return False
        finally:
            if f_a:
                f_a.close()
            if f_b:
                f_b.close()
        return True


def readCMD(args=[], isShell=True):
    '''
    #Running the command and read String from stdout.
    #@param args(list): cmd script path & cmd params
    #@param isShell(Bool): The cmd is shell cmd or not.
    #@param timeout(int): set timeout(must > 0), default -1 means never timeout
    #@return (res, rev): res: result status code
    #                   rev: result string
    '''
    import subprocess
    from subprocess import Popen

    res = False
    rev = []
    p = subprocess.Popen(args, shell=isShell, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while True:
        if sys.version > "3":  ## python3 +
            buff = p.stdout.readline().decode(encoding="UTF-8").strip().replace("\r\n", "")
        else:                   ## python2 +
            buff = p.stdout.readline().strip().replace("\r\n", "")

        if p.poll() != None:
            if buff == '':
                break;
        if buff != '':
            buff.strip().replace("\n", "")
            rev.append(buff)
            # print(buff)
#    if p.wait() == 0:
#        res = True

    return (p.wait(), rev)  ## res(Bool): The cmd is running successful?
                        ## rev(String): The cmd result string.

if __name__ == "__main__":



    import time
    from IP_Pool import IP_Pool
    config_path = "/Users/gdlocal1/test.txt"
    test = IP_Pool(config_path)

    print(test.getLocalHostIP())


    l_a = [1,2,3,4,5,6,]
    l_b = [2,9,8,21,6,17]
    l_c = [7,3,0,4,43,69]
    res = test.mergeLists(l_a,l_b,l_c)
    print(type(res))

    test.rewriteConfig(res)

    exit(0)

    print(test.resolveData())
    print(test.setIPStats("192.168.191.2", "Online"))
    print(test.resolveData())

