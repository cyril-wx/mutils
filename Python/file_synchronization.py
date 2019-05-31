#!/usr/bin/env python2
# -*- coding:UTF-8 -*-

### =====================================
def read_file(filename):
    global location
    location = 0
    with open(filename) as fd:
        while True:
            cur_location = fd.tell()#记录文件当前位置
            if cur_location == location: #如果两者相等，说明没有新增文件
                continue
            else:
                data = fd.seek(location).read()#读取增量内容
                location = cur_location#移动指针到当前位置
                print(data)
### =====================================

import time
import os
import cPickle as p
import tarfile
import hashlib
baseDir = '/Users/gdlocal1/Desktop/Cyril/TMP'
srcDir = 'src'
dstDir = 'dst'
fullName = "full_%s_%s.tar.gz" % (srcDir, time.strftime('%Y%m%d'))
incrName = "incr_%s_%s.tar.gz" % (srcDir, time.strftime('%Y%m%d'))
md5file = 'md5.data'

def md5sum(fname):
    m = hashlib.md5()
    with file(fname) as f:
        while True:
            data = f.read(4096)
            if len(data) == 0:
                break
            m.update(data)
    return m.hexdigest()

# 全量备份
def fullBackup():
    md5Dict = {}
    fileList = os.listdir(os.path.join(baseDir,srcDir))
    for eachFile in fileList:
        md5Dict[eachFile] = md5sum(os.path.join(baseDir,srcDir,eachFile))
    with file(os.path.join(baseDir,dstDir,md5file),'w') as f:
        p.dump(md5Dict,f)
    tar = tarfile.open(os.path.join(baseDir,dstDir,fullName),'w:gz')
    os.chdir(baseDir)
    tar.add(srcDir)
    tar.close()


def incrBackup():
    newmd5 = {}
    fileList = os.listdir(os.path.join(baseDir,srcDir))
    for eachFile in fileList:
        newmd5[eachFile] = md5sum(os.path.join(baseDir,srcDir,eachFile))
    with file(os.path.join(baseDir,dstDir,md5file)) as f:
        storedmd5 = p.load(f)
    tar = tarfile.open(os.path.join(baseDir,dstDir,incrName),'w:gz')
    os.chdir(baseDir)
    for eachKey in newmd5:
        if (eachKey not in storedmd5) or (newmd5[eachKey] != storedmd5[eachKey]):
            tar.add(os.path.join(srcDir,eachKey))
    tar.close()
    with file(os.path.join(baseDir,dstDir,md5file),'w') as f:
        p.dump(newmd5,f)

def main():
        if time.strftime('%a') == 'Mon':
            print ("Start full backup.")
            fullBackup()
        else:
            print ("Start increase backup.")
            incrBackup()
            
import os
import shutil
import sys
import logging

# 同步文件夹
class SynDirTool:
    def __init__(self, fromdir, todir):
        self.fromdir = fromdir
        self.todir = todir

    def synDir(self):
        return self.__copyDir(self.fromdir, self.todir)

    def __copyDir(self, fromdir, todir):
        # 防止该目录不存在，创建目录
        self.__mkdir(todir)
        count = 0
        for filename in os.listdir(fromdir):
            if filename.startswith('.'):
                continue
            fromfile = fromdir + os.sep + filename
            tofile = todir + os.sep + filename
            if os.path.isdir(fromfile):
                count += self.__copyDir(fromfile, tofile)
            else:
                count += self.__copyFile(fromfile, tofile)
        return count

    def __copyFile(self, fromfile, tofile):
        if not os.path.exists(tofile):
            shutil.copy2(fromfile, tofile)
            logging.info("新增%s ==> %s" % (fromfile, tofile))
            return 1
        fromstat = os.stat(fromfile)
        tostat = os.stat(tofile)
        if fromstat.st_ctime > tostat.st_ctime:
            shutil.copy2(fromfile, tofile)
            logging.info("更新%s ==> %s" % (fromfile, tofile))
            return 1
        return 0

    def __mkdir(self, path):
        # 去除首位空格
        path = path.strip()
        # 去除尾部 \ 符号 或者 /
        path = path.rstrip(os.sep)

        # 判断路径是否存在
        isExists = os.path.exists(path)

        # 判断结果
        if not isExists:
            # 如果不存在则创建目录
            logging.info(path + ' 目录创建成功')
            # 创建目录操作函数
            os.makedirs(path)

# 同步文件夹——测试
def test_SynDirTool():
    count = 0
    
    basedir = "/Users/gdlocal1/Desktop/Cyril/TMP"
    sync_file = "panic_report.csv"
    #src_list = ["src_1", "src_2", "src_3", "src_4", "src_5"]
    src_list = ["src_1", "src_2", "src_3", "src_4", "src_5"]
    current_src = src_list[1]

    for i in src_list:
        if not i == current_src:
            source = basedir+"/"+current_src+"/"
            target = basedir+"/"+i+"/"
            logging.basicConfig(filename='SynDirTool.log', level=logging.INFO)
            tool = SynDirTool(source, target)
            count += tool.synDir()
    #srcdir = sys.argv[1]
    #descdir = sys.argv[2]
    
            

if __name__ == '__main__':
    main()
    #test_SynDirTool()

