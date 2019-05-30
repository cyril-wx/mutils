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

if __name__ == '__main__':
    #main()
    print ("Start increase backup.")
    incrBackup()

