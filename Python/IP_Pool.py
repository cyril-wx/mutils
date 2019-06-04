#!/usr/bin/env python
# -*- coding:UTF-8 -*-

import os
import sys

class IP_Pool:
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
                    return item[1]
        return None

    def setIPStats(self, IP, Stats):
        """
        #
        :param IP:
        :param Stats:
        :return:
        """
        import copy
        data = self.resolveData()
        if data:
            for item in data:
                if item[0] == IP :
                    print("Found IP: %s" %IP)
                    item[1] = Stats
                    self.rewriteConfig(data)
                    self.syncConfigOn2Stations("172.21.204.238", "/tmp/test.txt")
        else:
            print("No data in config file.")
        pass

    def rewriteConfig(self, data):
        """
        # 将修改后的数据写入配置文件
        :param data:
        :return:
        """
        with open(self.conf_path, "w") as f:

            if isinstance(data, str):   ## 源数据类型为 str
                f.write(data)
            elif isinstance(data, list): ## 源数据类型为 [["", ""], ]
                for line in data:
                    try:
                        f.write(" ".join(line)+"\n")
                    except:             ## 写入失败 将源数据类型强制转换为为 str 并写入
                        print("Writing data as list type failed and forcing writing as str.")
                        f.write(str(line)+"\n")
            else:                       ## 将源数据类型强制转换为为 str 并写入
                print("Unkown data type and writing as str.")
                f.write(str(data)+"\n")

    def syncConfigOn2Stations(self, remoteIP, syncFileOrDir, localhost="127.0.0.1"):
        import re, os
        if not re.match("\d+.\d+.\d+.\d+", remoteIP):
            print("'IP' is invalid type.")
            exit(1)

        (dir, filename) = os.path.split(syncFileOrDir)
        sync_cmd = """
expect << EOF
set timeout 10
spawn /usr/bin/rsync -av %s/%s gdlocal@%s:%s
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

        (res, rev) = readCMD(sync_cmd, True)
        #(res, rev) = readCMD(["/usr/bin/rsync", "-av", "/Users/gdlocal1/test.txt", "gdlocal@%s:/Users/gdlocal/test.txt" %s2], False)
        print("syncConfigOn2Stations", (res, rev))



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
    if p.wait() == 0:
        res = True

    return (res, rev)  ## res(Bool): The cmd is running successful?
                        ## rev(String): The cmd result string.

if __name__ == "__main__":

    config_path = "/Users/gdlocal1/test.txt"
    test = IP_Pool(config_path)

    print(test.resolveData())

    test.setIPStats("192.168.191.2", "Online")

    print(test.resolveData())

