#!/usr/bin/python
# -*- coding:UTF-8 -*-
#**********************************************	#
# This py script is Panic Tools Package 	#
#----------------------------------------------	#
# @Author: Cyril				#
# @Create: 2019-01-28				#
# @Tips: All cableName is such as '30F465'	#
#**********************************************	#

import os
import re
import sys
import time
import datetime
import json
import sqlite3
from jc import utils
from jc import csv_rw
from SqliteTools import SqliteHelper

#----------------------------路径(调试1)----------------------------------------
#DOCUMENT_PATH = os.environ['HOME']+"/Documents/AutoPanic/"
DOCUMENT_PATH = "/Users/gdlocal/Documents/AutoPanic/"
#------------------------------------------------------------------------------

#----------------------------路径(调试2)----------------------------------------
script_path = os.path.split(os.path.realpath(__file__))[0]+"/" # Current script real path.
#------------------------------------------------------------------------------

marvin_path = "/usr/local/bin/marvin"
astris_path = "/usr/local/bin/astris"
LOG_NAME = "panic_tool_package.log"
LOG_PATH = "/tmp/" + LOG_NAME   ## Log路径 - 和Swift中的log输出路径一致
APP_CONFIG = DOCUMENT_PATH + "/app_config.json"

# Document目录
DATA_DIR = DOCUMENT_PATH + "/Data"
Data_History = DOCUMENT_PATH + "/Data/History"
Data_Unsync = DOCUMENT_PATH + "/Data/Unsync"
Report_Summary = DOCUMENT_PATH + "/Report/Summary"
Report_NDay = DOCUMENT_PATH + "/Report/NDay"

#DEVICE_PATH = DOCUMENT_PATH + "/PanicLog/" + sn + "/panic_device.log"
#HOST_PATH = DOCUMENT_PATH + "/PanicLog/" + sn + "/panic_host.log"


# 获取location id以及机台模式
def getLocIDAndMode():
    """
    获取location id以及机台模式
    :return: [(cable_name, loc_id, mode)]
    """
    import re
    pattern_cable_name = "Serial Number: ([a-zA-Z0-9]+)"
    pattern_cable_locid = "Location ID: ([a-zA-Z0-9]+)"
    pattern_unitsn_recovery = "SRNM:\[([a-zA-Z0-9]+)\]"

    (res, info_arr)=readCMD(['/usr/sbin/system_profiler SPUSBDataType | egrep "DCSD USB UART:|Kanzi:|iPhone|Serial Number:*|Location ID:*|Apple Mobile Device*"'], True, LOG_PATH)
    result = []

    info_arr_count=len(info_arr)
    for i in range(info_arr_count):
#       print("[H] %s" %info_arr[i])
        a = (
            re.search("iPhone:", info_arr[i]),          # OS mode
            re.search("Apple Mobile Device \(Recovery Mode\):", info_arr[i]), # Recovery mode
            re.search("Apple Mobile Device \(DFU Mode\):", info_arr[i]))      # DFU mode

        if a[0] or a[1] or a[2]:
            if a[0]:
                mode = "iOS"
            elif a[1]:
                mode = "Recovery"
            elif [2]:
                mode = "DFU"
            else:
                pass

            try:
                cable_name = re.search(pattern_cable_name, info_arr[i - 2]).group().split(":")[1].strip()
                loc_id = re.search(pattern_cable_locid, info_arr[i + 2]).group().split(":")[1].strip()
                result.append((cable_name, loc_id, mode))
            except Exception as e:
                print(e)
            else:
                if a[2]:    # Recovery模式下读取SN
                    g = re.search(pattern_unitsn_recovery, info_arr[i + 1])
                    if g:
                        unit_sn = g.group()[6:-1]
                        print("Cable-%s : Unit_SN-%s" % (cable_name, unit_sn))
#print("getLocIDAndMode:%s" %str(result))
    return result

##  根据cableName获取LocationID
def getLocId(_cableName, path_sn):
    """
    :param _cableName: cableName, such as "cu.kanzi-30EE63"/"30EE63"
    :param path_sn: log_path or sn
    :return: location id(str)
    """
    import re
    cableName = str(_cableName)  # 去掉cablename的前缀
    if re.search("-",cableName):
        cableName = cableName.split("-")[1].strip()
    getLocIds = getLocIDAndMode()
    if len(getLocIds) < 1:
        return None
    for item in getLocIds:
        print(item)
        if item[0] == cableName:
            writeLogs("getLocId: %s" %str(item), path_sn)
            print("getLocId:%s" %str(item))
            return  item[1]
    return None


def setKisStatus(_cableName, status, path_sn):
	"""
	# 设置Kis状态
	:param _cableName: _cableName
	:param status: 只接受 0/2
	:param path_sn:
	:return:
	"""
	if str(status) != "0" and str(status) != "2" :
		writeLogs("setKisStatus failed because status not (0 or 2).", path_sn)
		exit(1)

	# 首先获取完整的ProbeName
	probeName = ""
	res, rev = readCMD(["astrisctl --host localhost list"], True, path_sn)
	try:
		if "-" in _cableName:
			_cableName = _cableName.split("-")[1].strip()
		probeName = [line for line in rev if re.search(_cableName, line)][0].strip()
	except:
		writeLogs("getAstrisProbeName failed. CableName-%s" % _cableName, path_sn)
		exit(1)
	else:
		if probeName.strip() == "":
			writeLogs("setKisStatus failed because probeName is Nil.", path_sn)
			exit(1)

	res, rev = readCMD(["astrisctl --force-kick --host localhost:%s kis %s" %(probeName, status)], True, path_sn)
	if res and rev:
		if "failed" not in "\n".join(rev):
			print("True")
			exit(0)
	writeLogs("setKisStatus failed. (res,rev) = (%s, %s)" %(res,rev), path_sn)
	exit(1)

##  根据cableName获取mode
def getConnState(_cableName, path_sn):
	"""
	:param _cableName: cableName, such as "cu.kanzi-30EE63"/"30EE63"
	:param path_sn: log_path or sn
	:return: device mode(str)  DFU/Recovery/iOS
	"""
	import re
	cableName = str(_cableName)  # 去掉cablename的前缀
	if re.search("-",cableName):
		cableName = cableName.split("-")[1].strip()
		getLocIds = getLocIDAndMode()
		if len(getLocIds) < 1:
			writeLogs("getConnState failed.", path_sn)
			print("state=")	## Unknonw mode
		for item in getLocIds:
			if item[0] == cableName:
				print("state=%s" %item[1])
				writeLogs("getConnState: state-%s" %item[1], path_sn)
	writeLogs("getConnState failed.", path_sn)
	print("state=")		## Unknonw mode


def getMarvinProbeID(cableName, path_sn):
	"""
	# Get Marvin Probe ID for expect auto run.
	# @param cableName(str):
	# @param path_sn(str): path or sn for log storage.
	# @return probeID(int):  //If get null, return -1
	"""
	# 处理未格式化的 cablename 字符串
	cableName_0 = cableName
	if re.search("-", cableName_0):
		cableName_0 = cableName_0.split("-")[1]
	res, rev = readCMD(["%s/runMarvin.exp"%(script_path)], True, path_sn)
	
	for item in rev:
		if re.search(cableName_0, item):
			probeID=re.search("[0-9]{1}", item).group()
			writeLogs("getMarvinProbeID probeID=%s" %probeID, path_sn)
			return probeID
	writeLogs("getMarvinProbeID failed. cableName=%s" %cableName, path_sn)
	return "999"

def getAstrisProbeID(cableName, path_sn):
	"""
	# Get Astris Probe ID for expect auto run.
	# @param cableName(str):
	# @param path_sn(str): path or sn for log storage.
	# @return probeID(int):  //If get null, return -1
	"""
	# 处理未格式化的 cablename 字符串
	cableName_0 = cableName
	if re.search("-", cableName_0):
		cableName_0 = cableName_0.split("-")[1]
	res, rev = readCMD([script_path+"/runAstrisID.exp"], True, path_sn)
	for item in rev:
		if re.search(cableName_0, item):
			probeID = re.search( "[0-9]{1}", item).group() 
			writeLogs("getAstrisProbeID: sn=%s probeID=%s" %(path_sn,probeID), path_sn)
			return probeID     ## probeID
	writeLogs("getAstrisProbeID failed. cableName=%s" %cableName, path_sn )
	return "999"


def run_marvin(*args):
	'''################################################################
	# @Descript: Running marvin script
	# @param: cableName(String): cable线的名字，如"30EED5"/"KanziSWD-30EED5"，运行marvin后查看
	# @param: args(list): 所有的unit信息，一共8个
	#               Such as: args = ["D42_EVT_BUILD","D42_EVT_FF","YukonNanshan16A999","Burnin","Black","3CAA","C39XXX_001"]
	# @return: exit 1, marvin crashed.
	# @return: (res, rev, panic_type, panic_log) :
	#               res(str):CMD RETURN CODE; rev(str):CMD RETURN INFO;
	#               panic_type(str); panic_log(str):log path
	################################################################ '''

	if (not args) or len(args)!=9:
		writeLogs("ERROR: run_marvin params incorrect.")
		exit(2) 
	
	# Get panic type
	result=True
	panic_type="Unknown"
	panic_log=""
	panic_log_host = DOCUMENT_PATH + "/PanicLog/"+args[-1]+"/"    ##以SN命名Log文件夹
	
	cableName = args[0]
	tmpfile = args[1]
	sn = args[8]

	_args = list(args[2:])

	# Judge device connection status
	if getLocId(cableName, sn):
		panic_type = "Error: Device current in DFU/Recovery/iOS mode."
		writeTMPF(tmpfile,"type=%s" %panic_type)
		writeTMPF(tmpfile,"res=False")
		writeTMPF(tmpfile, "done")
		exit(12)
	
	# Run marvin factory
	probe_id = getMarvinProbeID(cableName, sn)
	if probe_id == "999":
		panic_type = "ERROR: No astris probes connected"
		writeTMPF(tmpfile,"type=%s" %panic_type)
		writeTMPF(tmpfile,"res=False")
		writeTMPF(tmpfile, "done")
		exit(11)

	_args.insert(0, probe_id)        ## Put key "probe_id" to args
	_args.insert(0, script_path+"/auto_marvin.exp")      ## Put the cmd script path to args

	import time
	time.sleep(1)
	res, rev = readCMD(_args, False, sn)
	
	for item in rev:
		if re.search("Passive Coredump : Failed!", item):
			result=False
		elif re.search('Explore Failure', item):
			# Some bug in it 🚩
			if re.search('marvin crashed', "\n".join(rev)):
				panic_type = "marvin crashed"
				result=False
				writeLogs("marvin crashed.", sn)
#				writeTMPF(tmpfile, "panic_type=%s" %panic_type)
#				writeTMPF(tmpfile, "done")
#				exit(3)
                
		elif re.search('-Report-', item):
			panic_type=rev[rev.index(item)+2].strip()  ## strip() 默认是去字串首尾空格
#		elif re.search('-System Triage-', item):
#			panic_type=rev[rev.index(item)+2].strip()  ## strip() 默认是去字串首尾空格
                
		elif "factory-debug.zip" in item:
			panic_log=item
			readCMD(["/bin/mkdir","-p",panic_log_host], False, sn)
			(res, rev2) = readCMD(["/bin/mv", panic_log, panic_log_host], False, sn)
			
			try:
				radar_txt = panic_log.replace("factory-debug.zip", "radar.txt")
				readCMD(["/bin/mv", radar_txt, panic_log_host], False, sn)
			except:
				writeLogs("Move radar.txt file failed.", sn)
                        
			if res==True:
				writeLogs("Corefile has been moved to localhost.", sn)
				panic_log = panic_log_host+"/factory-debug.zip"
	
	# replace “//” as “/”
	try:
		pattern = re.compile(r"(/{2,}?)")
		panic_log = re.sub(pattern, "/", panic_log)
	except Exception as e:
		writeLogs("panic_log get failed: e", sn)
	
	#return (res, rev, panic_type, panic_log)
	writeTMPF(tmpfile,"res=%s" %result)
	writeTMPF(tmpfile,"type=%s" %panic_type)
	writeTMPF(tmpfile,"log=%s" %panic_log)
	writeTMPF(tmpfile,"done")
	writeLogs("run_marvin finish. sn=%s res=%s type=%s log=%s" %(sn, result, panic_type, panic_log), sn)


## 基于scout命令， 已弃用🚩
def run_jebdump(cableName, tmpfile, sn):
	"""
	# @Description: get jebdump by cable name.
	# @param args(list): args[0]=<cableName> args[1]=<tmp_file_path>
	#			'args' can be NULL.
	# @return jebdump_path(str) / None
	"""
	probe_id = getAstrisProbeID(cableName, sn)
	if probe_id == "999":
		writeTMPF(tmpfile,"res=False")
		writeTMPF(tmpfile, "done")
		exit(11)
	_args = []
	_args.insert(0, probe_id)        ## Put key "probe_id" to args
	_args.insert(0, script_path+"/auto_jebdump.exp")      ## Put the cmd script path to args
	res, rev = readCMD(_args, False, sn)
	for item in rev:
		info = re.search("/(.*).zip", item)
		if info:
			logpath = info.group()
			
			# replace “//” as “/”
			pattern = re.compile(r"(/{2,}?)")
			logpath = re.sub(pattern, "/", logpath)
			
			writeLogs("run_jebdump jebdump=%s" %logpath, sn)
			writeTMPF(tmpfile, "jebdump=%s" %logpath)
			writeTMPF(tmpfile, "done")
			exit(0)

	writeLogs("Cable:%s jebdump log failed."%(cableName), sn)
	writeTMPF(tmpfile, "jebdump=")
	writeTMPF(tmpfile, "done")
	exit(1)

def run_jebdump_2(cableName, tmpfile, sn):
	"""
	# @Description: get jebdump by cable name.
	# 		- Only for NonScout
	# @param args(list): args[0]=<cableName> args[1]=<tmp_file_path>
	#			'args' can be NULL.
	# @return jebdump_path(str) / None
	"""
	
	panic_log_host = DOCUMENT_PATH + "/PanicLog/"+sn+"/"    ##以SN命名Log文件夹
	probe_id = getAstrisProbeID(cableName,sn)
	if probe_id == "999":
		writeTMPF(tmpfile,"res=False")
		writeTMPF(tmpfile, "done")
		exit(11)
	_args = []
	_args.insert(0, probe_id)        ## Put key "probe_id" to args
	_args.insert(0, script_path+"/auto_jebdump_2.exp")      ## Put the cmd script path to args
	res, rev = readCMD(_args, False, sn)
	for item in rev:
		info = re.search("/(.*).zip", item)
		if info:
			#return info.group()
			res, rev = readCMD(["mv %s %s" %(info.group(), panic_log_host)], sn)
			if res:
				log = panic_log_host + re.search("jebdump(.*).zip", item).group()
				
				# replace “//” as “/”
				pattern = re.compile(r"(/{2,}?)")
				log = re.sub(pattern, "/", log)
				
				writeLogs("run_jebdump_2 jebdump=%s" %log, sn)
				writeTMPF(tmpfile, "jebdump=%s" %log)
				writeTMPF(tmpfile, "done")
				exit(0)

	writeLogs("Collect jebdump log failed.", sn)
	writeTMPF(tmpfile, "jebdump=")
	writeTMPF(tmpfile, "done")
	exit(1)


def run_reboot(cableName, sn):
	writeLogs("Start Cable:%s reboot log collecting."%(cableName), sn)
	#	reboot_log_host="/tmp/reboot_%s.log" %sn    ##以SN命名Log文件夹
	panic_log_host = DOCUMENT_PATH + "/PanicLog/"+sn+"/"    ##以SN命名Log文件夹
	readCMD(["mkdir -p %s" %panic_log_host], True, sn)

	reboot_name = panic_log_host+"/reboot_log.txt"
	res, reboot_log_str = readCMD(["%s/auto_reboot.exp %s >> %s" %(script_path, cableName, reboot_name)], True, sn)
	
	# replace “//” as “/”
	pattern = re.compile(r"(/{2,}?)")
	reboot_name = re.sub(pattern, "/", reboot_name)
	
	writeLogs("reboot_log=%s" %reboot_name, sn)
	print("reboot=%s" %reboot_name)

## 基于scout命令， 已弃用🚩
def run_sysdiagnose(cableName, sn):
	"""
	# @Description: get sysdiagnose by cable name.
	#			- Based on Scout CMD
	# @param cableName(str):
	# @param args(list): args[0]=<probe_id> args[1]=<rep._script_path> args[3...]=<rep._script_args>
	#			'args' can be NULL.
	# @return sysdiagnose_path(str) / None
	"""
	panic_log_host = DOCUMENT_PATH + "/PanicLog/"+sn+"/"    ##以SN命名Log文件夹
	_args = []
	_args.insert(0, script_path+"/auto_sysdiagnose.exp")      ## Put the cmd script path to args
	res, rev = readCMD(_args, False, sn)
	for item in rev:
		info = re.search("/(.*).tar.gz", item)
		if info:
			logpath = info.group()
			
			# replace “//” as “/”
			pattern = re.compile(r"(/{2,}?)")
			logpath = re.sub(pattern, "/", logpath)
			
			writeLogs("run_sysdiagnose sysdiagnose=%s" %logpath, sn)
			print("sysdiagnose=%s" %logpath)
			exit(0)
	writeLogs("Cable:%s sysdiagnose log failed."%(cableName), sn)
	print("sysdiagnose=")
	exit(1)

def run_sysdiagnose_2(cableName, sn):
	"""
	# @Description: get sysdiagnose by cable name.
	# 			- Based on traditional CMD
	# @param cableName
	# @param SN
	# @return sysdiagnose=%s
	"""
	location_id = getLocId(cableName,sn)
	if not location_id:
		writeLogs("run_sysdiagnose_2 failed. can not get location id for cableName:%s" %cableName, sn)
		print("sysdiagnose=")
		exit(11)

	panic_log_host = DOCUMENT_PATH + "/PanicLog/"+sn+"/"    ##以SN命名Log文件夹
	sysdiagnose_log = ""
	rev = run_OS_CMDs(cableName, sn, "sysdiagnose")
	if rev:
		for info in rev:
			if re.match("Output available at", info):
				sysdiagnose_log = re.search("/(.*).tar.gz", info).group()
				sysdiagnose_name = re.search("sysdiagnose_(.*).tar.gz", sysdiagnose_log).group()
				
				cmd = "/usr/local/bin/copyUnrestricted -u %s -s %s -t %s" %(location_id, sysdiagnose_log,panic_log_host)
				res, rev = readCMD([cmd], True, sn)
				if res:
					logpath = panic_log_host+sysdiagnose_name
					
					# replace “//” as “/”
					pattern = re.compile(r"(/{2,}?)")
					logpath = re.sub(pattern, "/", logpath)
					
					writeLogs("run_sysdiagnose_2 sysdiagnose=%s" %(logpath), sn)
					print("sysdiagnose=%s" %(logpath))
					exit(0)

	writeLogs("run_sysdiagnose_2 failed. sn=%s" %sn, sn)
	print("sysdiagnose=" )
	exit(1)

## 基于scout命令， 已弃用🚩
# Need to zip log files (Coding ongoing)
def run_burnin(cableName, sn):
	"""
	# @Description: get burnin by cable name. 
	# @param cableName(str):
	# @return burnin_path(str) / None
	# Tips: burnin_path is a folder path.
	"""
	panic_log_host = DOCUMENT_PATH + "/PanicLog/"+sn+"/"    ##以SN命名Log文件夹
    
	_args=[]
	_args.insert(0, script_path+"/auto_burnin.exp")      ## Put the cmd script path to args
	res, rev = readCMD(_args, False, sn)
	for item in rev:
		info = re.search("/(.*)LogCollector", item)
		if info:
			res, rev = readCMD(["mv %s %s" %(info.group(), panic_log_host)], True, sn)
			if res:
				zip_log_file = "%s/burnin_logs.zip" %panic_log_host
				res, rev = readCMD(["zip -r %s %s" %(zip_log_file, info.group())], True, sn)
				if res:
					# replace “//” as “/”
					pattern = re.compile(r"(/{2,}?)")
					zip_log_file = re.sub(pattern, "/", zip_log_file)
					
					writeLogs("run_burnin burnin=%s" %zip_log_file, sn)
					print("burnin=%s" %zip_log_file)
					exit(0)
		if "File exists:" in item:	## Burnin file has exists
			_log =  re.search("/(.*)[0-9]{12}", info).group() + "/LogCollector"
			
			# replace “//” as “/”
			pattern = re.compile(r"(/{2,}?)")
			_log = re.sub(pattern, "/", _log)
			
			writeLogs("run_burnin burnin=%s" %_log, sn)
			print("burnin=%s" %_log)
			exit(0)
	writeLogs("Cable:%s burnin log failed."%(cableName), sn)
	print("burnin=")
	exit(1)

## No need scout
def run_burnin_2(cableName, sn):
	"""
	# @Description: get burnin by cable name. 
	# @param cableName(str):
	# @return burnin_path(str) / None
	# Tips: burnin_path is a folder path.
	"""
	panic_log_host = DOCUMENT_PATH + "/PanicLog/"+sn+"/"    ##以SN命名Log文件夹
	location_id = getLocId(cableName, sn)

	if not location_id:
		writeLogs("run_burnin_2 failed. can not get location id for cableName:%s" %cableName, sn)
		print("burnin=")
		exit(11)

	# 转储log到指定路径
	cmd = "/usr/local/bin/copyUnrestricted -u %s -s /private/var/logs -t %s" %(location_id, panic_log_host)
	#writeLogs("DEBUG: auto_burnin: %s " %cmd, sn)
	res, rev = readCMD([cmd], True, sn)
	if res:
		cmd = "zip -r  %s/burnin_log.zip %s" %(panic_log_host, panic_log_host+"/logs")
		res, rev = readCMD([cmd], True, sn)
		if res:
			# 删除原logs文件夹
			cmd = "rm -rf %s" %(panic_log_host+"/logs")
			readCMD([cmd], True, sn)
			logpath = panic_log_host+"/burnin_log.zip"
			
			# replace “//” as “/”
			pattern = re.compile(r"(/{2,}?)")
			logpath = re.sub(pattern, "/", logpath)
			
			writeLogs("run_burnin burnin=%s" %logpath, sn)
			print("burnin=%s" %logpath)
			exit(0)
	writeLogs("Cable:%s burnin log failed."%(cableName), sn)
	print("burnin=")
	exit(1)

def run_crstackshot(cableName, sn):
	"""
	# 收集crstackshot log
	:param cableName:
	:param sn:
	:return:
	"""
	log = ""
	log_name = ""
	location_id = getLocId(cableName, sn)
	if not location_id:
		writeLogs("run_crstackshot failed. Can not get location id for cableName:%s" % cableName, sn)
		print("crstackshot=")
		exit(11)

	cmd = "ls /private/var/root/ | grep 'stacks+test*' | sort -r | head -n 1"
	panic_log_host = DOCUMENT_PATH + "/PanicLog/" + sn + "/"  ##以SN命名Log文件夹
	rev = run_OS_CMDs(cableName, sn, cmd)
	if rev:
		for item in rev:
			if re.search("stacks(.*).ips", item):
				log_name = re.search("stacks(.*).ips", item).group()
	if log_name and log_name != "":
		writeLogs("copy crstackshot log from device to host_path-%s" % (panic_log_host), sn)
		cmd = "/usr/local/bin/copyUnrestricted -u %s -s /private/var/root/%s -t %s" % (location_id, log_name, panic_log_host)
		res, rev = readCMD([cmd], True, sn)
		if res:
			log = panic_log_host + log_name
		else:
			writeLogs("copy crstackshot log from device failed.", sn)

	try:
		pattern = re.compile(r"(/{2,}?)")
		log = re.sub(pattern, "/", log)
	except Exception as e:
		writeLogs("crstackshot_log get failed: %s" %e, sn)
	writeLogs("run_crstackshot crstackshot=%s" %(log), sn)
	print("crstackshot=%s" % (log))

def run_ips(cableName, sn):
	"""
	# 收集ips log (KPCheck Panic)
	:param cableName:
	:param sn:
	:return:
	"""
	log = ""
	log_name = ""
	location_id = getLocId(cableName, sn)
	if not location_id:
		writeLogs("run_ips failed. Can not get location id for cableName:%s" % cableName, sn)
		print("ips=")
		exit(11)

	cmd = "ls /var/mobile/Library/Logs/CrashReporter/ | grep 'panic-*' | sort -r | head -n 1"
	panic_log_host = DOCUMENT_PATH + "/PanicLog/" + sn + "/"  ##以SN命名Log文件夹
	rev = run_OS_CMDs(cableName, sn, cmd)
	if rev:
		for item in rev:
			if re.search("panic-full(.*).ips", item):
				log_name = re.search("stacks(.*).ips", item).group()
	if log_name and log_name != "":
		writeLogs("copy ips log from device to host_path-%s" % (panic_log_host), sn)
		cmd = "/usr/local/bin/copyUnrestricted -u %s -s /var/mobile/Library/Logs/CrashReporter/%s -t %s" % (location_id, log_name, panic_log_host)
		res, rev = readCMD([cmd], True, sn)
		if res:
			log = panic_log_host + log_name
		else:
			writeLogs("copy ips log from device failed.", sn)

	try:
		pattern = re.compile(r"(/{2,}?)")
		log = re.sub(pattern, "/", log)
	except Exception as e:
		writeLogs("ips_log get failed: %s" %e, sn)
	writeLogs("run_ips ips_log=%s" %(log), sn)
	print("ips=%s" % (log))

##  现在还不能用，待修改 🚩
def run_remote():
	"""
	# @Description: Runing  OS CMDs on OS mode.
	# @param cableName(str)
	# @param args(list):	which CMDs run on OS mode
	# @return resultStr(str) / None
	"""
	#probe_id = getMarvinProbeID(cableName)
	#args.insert(0, probe_id)        ## Put key "probe_id" to args
	#args.insert(0, script_path+"/auto_remote.exp")      ## Put the cmd script path to args
	#res, rev = readCMD(args, False)
	#return res, rev
	res, rev = readCMD(["scout remote &"], False)
	return res


""" Backup
# ## 1. Get eixsts tcprelay_ports list
#     	res, tcp_port_list = readCMD(["lsof -i tcp | grep tcprelay | awk -F ':' '{print $2}' | awk -F ' ' '{print $1}' | awk -F/ '!a[$1,$2]++'"], True)
## 3. Get Current tcprelay proc_id
#      	telnet_port = tcp_port + 23
#      	res, rev = readCMD( ["lsof -i tcp:%s | awk -F ' ' '{print $2}' | sed '/PID/d' | awk -F/ '!a[$1,$2]++'" %(telnet_port)], True)
"""

##  测试OK
def run_OS_CMDs(*args):
	"""
	# @Description:
	#	- Runing  OS CMDs on OS mode. 
	# 	- Based on Tcprelay + Telnet
	# @Tips: 只支持单命令发送执行, 使用类似于“ /PanicToolPackage.py run_OS_CMDs 30EE63 TEST_SN "df -h" ”
	# @args[0] : cableName(str)
	# @args[1...] : OS CMDs
	# @Returns: rev (list)
	"""

	if (not args) or len(args)<3:
		writeLogs("ERROR: run_OS_CMDs params incorrect.")
		exit(10)

	cableName = args[0]
	sn = args[1]
	cLogsList = args[2:]
	print("cLogsList=%s" %str(cLogsList))
	rev = "" 	## OS command return value strings.
	sysdiagnose_log = ""
	loc_id = getLocId(cableName,sn)
	if not loc_id:		## 没有获取到Location id则直接退出
		print("rev=")
		writeLogs("run_OS_CMDs failed. can not get location id for sn:%s" %sn, sn)
		exit(1)
	
	tcp_port = 10000	## init tcp_port value to 10000
	tcp_proc_id = "" 	## tcprelay process id (str)
	
	## 1. Get eixsts tcprelay_ports list
	res, tcp_port_list = readCMD(["lsof -i tcp | grep tcprelay | awk -F ':' '{print $2}' | awk -F ' ' '{print $1}' | awk -F/ '!a[$1,$2]++'"], True, sn)
	if tcp_port_list and len(tcp_port_list)>0:
		## Produce a legal tcp_port for a new tcprelay connection.
		while (str(tcp_port+23) in tcp_port_list):
			tcp_port = tcp_port + 1

	TelnetExpPath = "%s/auto_telnet.exp" %script_path
	## 2. Start tcprelay monitor.
	tcp_cmd = "%s/runTcprelay.exp %s %d %s " %(script_path, loc_id, tcp_port, TelnetExpPath)
	for item in cLogsList:
		writeLogs("Running tcp_cmd:%s"%(tcp_cmd + item), sn)
		#res , rev = readCMD(["%s '%s'" %(tcp_cmd,item)], True, sn)
		res , rev = readCMD([script_path+"runTcprelay.exp", loc_id, str(tcp_port), TelnetExpPath, item], False, sn)
		if res and rev:
			#writeLogs("run_OS_CMDs rev=%s" %rev , sn)
			print "\n".join(rev)
			return rev
	writeLogs("run_OS_CMDs failed. sn:%s" %sn, sn)

# handle_OSCMD_Rev。配合run_OS_CMDs() 使用
def handle_OSCMD_Rev(rev_list):
	start_index = 0
	end_index = 0
	handle_rev_list = []
	tag = False
	Prompt = "iPhone:~ root#"
	if not rev_list and len(rev_list) < 3:
		return None
	for item in rev_list:
		if not tag and re.search("%s(.*)"%Prompt, item):
			tag = True
			continue
		if tag and re.search("%s exit"%Prompt, item):
			break
		if tag:
			handle_rev_list.append(item)
	writeLogs("handle_OSCMD_Rev handle_rev_list=%s" %handle_rev_list, sn)
	return handle_rev_list	
				

def fileRadar(Attachment, sn, forceUpload="false", Umbrella="None"):
	"""
	# @Description: createRadar and upload corefile to Radar, export data to panic report.
	# @param Attachment(str): Corefile log file
	# @param Umbrella(str): umbrella rader, allow ""
	# @param sn: Unit SN string
	# @return radar: radar_id string, res: true/false
	"""
	rep_fileradar = script_path+"/auto_fileradar.exp"
	rep_fileradar_noumbrella = script_path+"/auto_fileradar_noumbrella.exp"
	
	radar = ""
	Report = DOCUMENT_PATH + "/PanicLog/" + getReportName()
	
	if Umbrella == "None" or Umbrella.strip() == "":
		## Report 已被注释掉，report导出不再由scout生成
		scout_cmd = script_path+"/auto_fileradar_noumbrella.exp %s %s" %(Attachment, Report)
	else:
		## Report 已被注释掉，report导出不再由scout生成
		scout_cmd = script_path+"/auto_fileradar.exp %s %s" %(Attachment, Report, Umbrella)
	
	## 强制上传
	if forceUpload == "true":
		scout_cmd += " --force"

	try:
		res, rev = readCMD([scout_cmd], True, sn)

		if res:
			pattern = "generating panic report (.*).csv ... done"
			pattern_2 = "filing panic radar ... (<rdar://problem/\d+>)"
			for item in rev:
				check_done = re.search(pattern, item) # 检测到file radar是否执行成功
				check_radar = re.search(pattern_2, item) # 检测雷达号
				if check_done:	# 检测到file radar是否执行成功, 如果成功则可退出
					writeLogs("Filing radar successful. Unit-%s radar number: %s" %(sn,radar), sn)
					print("res=true")
					print("radar=%s" %radar)
					exit(0)
				if check_radar: # 检测雷达号
					radar = check_radar.group()[-9:-1]
					writeLogs("Get radar number: %s" %radar, sn)

	except Exception as e:
		writeLogs("Filing radar failed with an exception. Unit-%s radar_number-%s" %(sn,radar), sn)
		print("radar=%s" %radar)
		print("res=false")
		exit(255)
	else:
		writeLogs("Filing radar failed. Unit-%s radar_number-%s" %(sn,radar), sn)
		print("res=false")
		print("radar=%s" %radar)
		exit(1)

def uploadAttachment(Attachment, Radar, sn):
	'''
	##########################################
	# @Description: Upload panic logs file attachment to radar
	# ---------------------------------------
	# @param Attachment: logs file path
	# @param Radar: radar id
	# @param Report: panic report file path
	# @param sn: Unit serial_number
	# @return result: True/False
	##########################################
	'''
	result = False
	exp_upload_att = script_path + "/auto_upload_attachment.exp"
	try:
		res, rev = readCMD([exp_upload_att, Attachment, Radar], False, sn)
	except Exception as e:
		writeLogs("uploadAttachment() Error: %s" %e, sn)
		print("result=%s" %result) ## False
		exit(255)
	else:
		if res:
			pattern = "attaching (.*) ... done"
			for item in rev:
				if re.match(pattern, item):
					result = True
					print("result=%s" %result)
					exit(0)
		print("result=%s" %result) ## False
		exit(1)


def getReportName():
	"""
	# @Description: get Panic-Report csv file name by timestamp
	"""
	base_path = DOCUMENT_PATH + "/PanicLog/"
	from datetime import datetime
	now = datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")
	
	report_name = "panic_report_" + now + ".csv"
	return report_name


# 导出/更新Panic报告
def export_panic_report(sn, corefile, radar="/", umbrellaRadar="/", OSDVer="/", action="/"):
	report_path = DOCUMENT_PATH + "/Data/Unsync/"
	if not os.path.exists(report_path):
		# 创建文件夹
		os.makedirs(report_path)
	res, rev = readCMD([script_path + "/PanicReport.py %s %s %s %s %s %s" %( corefile, report_path + getReportName(), radar, umbrellaRadar, OSDVer, action)], True, sn)
	print ("res=%s" %str(res))


def astris_reset(cableName, sn):
	'''
	##########################################
	#@Descript astris_reset is for a Unit/MLB reset opt.
	#@param cableName(str)
	#@return None
	##########################################
	'''
	# Get Probe number
	probe_id=getAstrisProbeID(cableName,sn)
	if probe_id == "999":
		writeLogs("Warning: Already exec reset, but maybe the cable:%s is not connecting to unit." %cableName, sn)
		readCMD([script_path+"/auto_reset.exp", "0"], False, sn)
	else:
		writeLogs("The cable '%s' will be reset later." %cableName, sn)
		readCMD([script_path+"/auto_reset.exp", probe_id], False, sn)


mlog = None
# scp传输工具
def scp_PanicReport(target_IP, source, target, target_user="gdlocal", target_pwd="gdlocal", type="PUT"):
	"""
	:param target_IP: 传输目标工站IP
	:param source: local （csv）dirpath, local文件夹路径
	:param target: target dirpath，remote文件夹路径
	:param type: PUT/GET
	:return: True/False
	"""
	if type == "PUT":
		mlog.info("执行PUT")
		cmd = r"""
		/usr/bin/expect -c "
		set timeout 10;
		spawn """ "/usr/bin/scp -r %s/. %s@%s:/%s" %(source, target_user, target_IP, target) + r"""
		expect {
		        -re \"Invalid|fail\" { exit 1 }
		        -re \"Are you sure you want to continue connecting\" { send \"yes\r\" ; exp_continue }
		        -re \"Password:\" { send \""""+ target_pwd +r"""\r\"; exp_continue }
		        timeout { exit 255 }
		        eof { exit 256 }
		}"
				"""
	else:
		mlog.info("执行GET")
		cmd = r"""
		/usr/bin/expect -c "
		set timeout 10;
		spawn """ + "/usr/bin/scp -r %s@%s:/%s/. %s " %(target_user, target_IP, target, source) + r"""
		expect {
		        -re \"Invalid|fail\" { exit 1 }
		        -re \"Are you sure you want to continue connecting\" { send \"yes\r\" ; exp_continue }
		        -re \"Password:\" { send \""""+ target_pwd + r"""\r\"; exp_continue }
		        timeout { exit 255 }
		        eof { exit 256 }
		}"
		"""

	res = os.system(cmd)
	mlog.info("Expect script command:\n%s \nreturn_status:%s" %(cmd, res))
	if res == 0:
		if type == "PUT":
			# 如果成功将数据发送到master，则移动source文件到history。
			history_dir = DOCUMENT_PATH + "/Data/History"
			cmd1 = "/bin/cp -r %s/. %s" % (source, history_dir)
			cmd2 = "/bin/rm -rf %s/* " % (source)
			res1 = os.system(cmd1)
			writeLogs_EXP("Expect script command:\n%s \nreturn_status:%s" % (cmd1, res1))
			res2 = os.system(cmd2)
			mlog.info("Expect script command:\n%s \nreturn_status:%s" % (cmd2, res2))
		else:
			# 如果成功获取到主节点数据，无须做处理
			mlog.info("Flush Summary Data successfully.")
			pass
		return True
	else:
		mlog.exception("Transport local panic report data to master failed.")
		return False


# 数据同步派发器（决定是走master流程还是slave流程）
def sync_Adapter():
	"""
	数据同步派发器（决定是走master流程还是slave流程）
	:return:
	"""
	import socket
	localhost = socket.gethostbyname(socket.gethostname())
	writeLogs("localhost=%s" %localhost)
	if not os.path.exists(APP_CONFIG):
		writeLogs("%s is not exsits, 「sync_PanicReport」 stopped." % APP_CONFIG)
		exit(1)

	data = None
	slave_IP = []       # 从节点IP列表
	master_IP = None    # 主节点IP
	dbFile = None       # 数据库文件
	tableName = None    # 数据表名
	try:
		with open(APP_CONFIG, "r") as f:
			data = json.load(f, encoding="utf-8")
			slave_IP = list(data["Cluster"]["slave_IP"])
			master_IP = str(data["Cluster"]["master_IP"])
			dbFile = str(data["Cluster"]["SQLiteDB"])
			tableName = str(data["Cluster"]["DBTableName"])

			writeLogs("创建 SqliteHelper...")
			sql_helper = SqliteHelper(dbFile)

			sql_helper.mlog.info("master_IP=%s" %master_IP)
			sql_helper.mlog.info("slave_IP=%s" % slave_IP)
			sql_helper.mlog.info("dbFile=%s" % dbFile)
			sql_helper.mlog.info("tableName=%s" % tableName)
			global mlog
			mlog = sql_helper.mlog

	except ValueError:
		writeLogs("%JSON 格式错误，请检查。%s"%APP_CONFIG)
		return

	fail_count = 0
	if localhost == master_IP:
		# 如果是主节点，插入数据到DB
		sql_helper.mlog.info("当前是主节点")
		sql_helper.mlog.info("###### 导入数据到Sqlite3 ######")
		if not os.path.exists(dbFile):
			sql_helper.createTable_Panic(tableName)
		##csv_f = "/Users/gdlocal1/Desktop/Panic/0724/Macan_DVT_Panic_Tracking_Report_0724"
		csv_filenames = os.listdir(Data_Unsync)
		for filename in csv_filenames:
			try:
				csv_filepath = Data_Unsync + "/" + filename
				data = sql_helper.readCSVs(csv_filepath)
				sql_helper.insert(data, tableName)
				if fail_count == 0:     ## 如果所有数据插入没有问题，则移动源数据文件至History
					os.system("/bin/mv '%s' '%s'" %(csv_filepath, Data_History))
			except sqlite3.IntegrityError:  # 如果使用insert失败，说明数据需要更新
				update_fail_count = sql_helper.update(data, indexKey=["SrNm",  "Radar"], table=tableName)
				sql_helper.mlog.warning("Count failure [%s] times when updating dataFile-[%s] " %(fail_count, filename))
				if update_fail_count and (fail_count + update_fail_count == 0):  ## 如果更新过程中没有问题，则移动源数据文件csv至History
					os.system("/bin/mv '%s' '%s'" %(csv_filepath, Data_History))
				else:
					sql_helper.mlog.warning("Not move dataFile-[%s] to History because there is error when updating" %filename)

			except sqlite3.OperationalError:
				fail_count += 1
				sql_helper.mlog.exception("Not found DBTable-%s. Will create a new." % (tableName))
				sql_helper.createTable_Panic(tableName=tableName)
			except Exception as e:  # 异常
				fail_count += 1
				sql_helper.mlog.exception("Skip an exception when import data: %s" %e)
				continue

		## 主节点还负责导出summary csv
		sql_helper.mlog.info("###### 导出全部数据 ######")
		export_path = DOCUMENT_PATH + "/Report/Summary/%s.csv" %tableName

		try:
			select_data = [i for i in sql_helper.select(tableName, args=["*"])]
			# 写入csv之前为数据添加title行
			select_data.insert( 0,
				[
					"NO", "Location", "Validation", "Station", \
				    "Config", "UNIT#", "SrNm", "Bundle", "OSD Version", \
				    "Panic info", "Umbrella Radar", "Radar", \
				    "Status/Action", "Comment/Solution", "Date"]
			)
			csv_rw.writeCSVFile(export_path, select_data)
			sql_helper.mlog.info("Export data finish. path: %s" % export_path)
		except Exception as e:
			sql_helper.mlog.exception("Export data failed. %s" %e)

	else:
		# 如果是从节点，发送数据到主节点(同目录)并获取主节点数据(/Summary)
		sql_helper.mlog.info("当前是从节点")
		if scp_PanicReport(master_IP, Data_Unsync, Data_Unsync, type="PUT"):
			sql_helper.mlog.info("Sending panic csv file to master:%s." %master_IP)
			scp_PanicReport(master_IP, Report_Summary, Report_Summary, type="GET")
			sql_helper.mlog.info("Downloading panic summmary file from master:%s." % master_IP)


def startSyncData(syncTime=15):
	"""
	# 开启同步任务（默認15s一次）
	:return: Never (Only when program exit and return False)
	"""
	import time

	(res, rev) = readCMD(["ps -ef | grep 'PanicToolPackage.py startSyncData' | grep -v 'grep' | awk -F ' ' '{print $2}'"], True)
	if len(rev) > 1:
		writeLogs("startSyncData already in starting.")
		exit(0)
	else:
		writeLogs("startSyncData...")

	while True:
		sync_Adapter()
	#time.sleep(600)
		time.sleep(syncTime)
	return False


def readCMD(args=[], isShell=True, logpath=LOG_PATH):
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
	writeLogs("readCMD args=%s" %args, logpath)
	p = subprocess.Popen( args, shell=isShell, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

	while True:
		buff = p.stdout.readline().strip().replace("\r\n", "")
		if p.poll() != None:
			if buff == '':
				break;
		if buff != '':
			buff.strip().replace("\n", "")
			rev.append(buff)
			#print(buff)
			writeLogs_EXP(buff, logpath)
	if p.wait() == 0:
		res = True

	return (res, rev)         ## res(Bool): The cmd is running successful?
							## rev(list): The cmd result list.

## 带超时设置，已弃用
def readCMD_2(args=[], isShell=True, timeout=-1, logpath = LOG_PATH):
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
        if timeout < 0 and timeout != -1:
                writeLogs("Timeout setting value illegal", logpath)
                exit(255)
        import time,signal
        rev = []
        p = subprocess.Popen( args, shell=isShell, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        while True:
                if timeout<=0:
                        buff = p.stdout.readline().strip().replace("\r\n","")
                        if p.poll() != None:
                                if buff == '':
                                        break;
                        if buff != '':
                                buff.strip().replace("\n","")
                                rev.append(buff)
                                writeLogs_EXP(buff)
                else:
                        try:
                                signal.signal(signal.SIGALRM, handler)
                                signal.alarm(timeout)
                                buff = p.stdout.readline().strip().replace("\r\n","")
                                if p.poll() != None:
                                        if buff == '':
                                                break;
                                if buff != '':
#                                       buff.strip().replace("\n","")
                                        rev.append(buff)
                                        writeLogs_EXP(buff)

                                signal.alarm(0)
                        except AssertionError:
                                writeLogs_EXP("CMDError: '%s' timeout" %(args[0]))
                                #print("rev=",rev)
                                return (False, rev)

        if p.wait() == 0:  ## get cmd result value
                res = True
        else:
                res = False
        return (res, rev)         ## res(Bool): The cmd is running successful?
                                ## rev(String): The cmd result string.


# str写入log
# @param info: log text 
# @param logpath: default:LOG_PATH
#		also can be "sn" str
def writeLogs(info, logpath=LOG_PATH):
	"""
	# 所有print输出都应写入log文件，使用writeLogs方法
	# @param info(str):log
	# @return none
	"""
	#now = datetime.datetime.now()
	now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	
	path = logpath
	if re.search("/", logpath):   # logpath is FileURL
		pass
	else:
		sn = logpath
		path = DOCUMENT_PATH + "/PanicLog/" + sn + "/panic_host.log"
	parent_path = os.path.split(path)[0]
	if not os.path.exists(parent_path):
		try:
			os.makedirs(parent_path)  # 多层创建目录 等效于mkdir -p	
		except Exception as e:
			error_info = "Create log file-%s error: %s" %(path,e)
			print("PYT [%s] %s \n" %(now, error_info))
	
	with open(path, 'a+') as f:
		try:
			f.write("PYT [%s] %s \n" %(now, info))
		except Exception as e:
			error_info = "Write to log file-%s error: %s" %(path,e)
			print("PYT [%s] %s \n" %(now, error_info))


# str写入tmp log
def writeTMPF(file, info):
	"""
	# 所有print输出都应写入log文件，使用writeLogs方法
	# @param info(str):log
	# @return none
	"""
	#now = datetime.datetime.now()
	now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

	path = file
	if re.search("/", path):   # logpath is FileURL
		pass
	else:
		path =  "/tmp/" + path
	parent_path = os.path.split(path)[0]
	if not os.path.exists(parent_path):
		try:
			os.makedirs(parent_path)  # 多层创建目录 等效于mkdir -p	
		except Exception as e:
			error_info = "Create TMP file-%s Error: %s" %(path,e)
			print("PYT [%s] %s \n" %(now, error_info))

	with open(path, 'a+') as f:
		try:
			f.write("%s\n" %info)
			print("PYT writeTMPF file:%s" %path)
		except Exception as e:
			error_info = "Write to TMP file-%s Error: %s" %(path,e)
			print("PYT [%s] %s \n" %(now, error_info))

# str写入log
def writeLogs_EXP(info, logpath=LOG_PATH):
	"""
	# 所有print输出都应写入log文件，使用writeLogs方法
	# @param info(str):log
	# @return none
	"""
	#now = datetime.datetime.now()
	now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

	path = logpath
	if re.search("/", logpath):   # logpath is FileURL
		pass
	else:
		sn = logpath
		path = DOCUMENT_PATH + "/PanicLog/" + sn + "/panic_device.log"
	parent_path = os.path.split(path)[0]
	if not os.path.exists(parent_path):
		try:
			os.makedirs(parent_path)  # 多层创建目录 等效于mkdir -p	
		except Exception as e:
			error_info = "Create log file-%s error: %s" %(path,e)
			print("EXP:[%s] %s \n" %(now, error_info))

	with open(path, 'a+') as f:
		try:
			f.write("EXP:[%s] %s \n" %(now, info))
		except Exception as e:
			error_info = "Write to log file-%s error: %s" %(path,e)
			print("EXP:[%s] %s \n" %(now, error_info))

##'''获取文件的大小,结果保留两位小数，单位为MB'''
#def get_FileSize(filePath):
#	filePath = unicode(filePath,'utf8')
#fsize = os.path.getsize(filePath)
#	fsize = fsize/float(1024*1024)
#	return round(fsize,2)
def getFileSize(filePath, size=0):
	for root, dirs, files in os.walk(filePath):
		for f in files:
			size += os.path.getsize(os.path.join(root, f))
			print(size)
			return size



## Python的入口开始
def main():
	module = sys.modules[__name__]
	# getattr() 函数用于返回一个对象属性值。
	# sys.argv 是获取运行python文件的时候命令行参数,且以list形式存储参数 
	# sys.argv[0] 代表当前module的名字
	try:
		func = getattr(module, sys.argv[1])
	except Exception as e:
		print(e)
	else:
		args = None
		if len(sys.argv) > 1:
			args = sys.argv[2:]
			#print("DEBUG: args = %s" %args)
			func(*args)

#main()
startSyncData()
