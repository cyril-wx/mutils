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

#----------------------------路径(调试2)----------------------------------------
script_path = os.path.split(os.path.realpath(__file__))[0]+"/" # Current script real path.
#------------------------------------------------------------------------------

LOG_PATH = "/tmp/panictools.log"
DOCUMENT_PATH = "/tmp/panictools"

def setKisStatus2():

	# probeName=`echo $probeName | awk -F '-' '{print $2}' | awk '$1=$1' `
	
	# `/usr/local/bin/astrisctl --force-kick --host localhost:KanziSWD-$1 kis $2 &>/dev/null ; echo $?`
	pass

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
                        #print("Cable-%s : Unit_SN-%s" % (cable_name, unit_sn))
    print("getLocIDAndMode:%s" %str(result))
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
            #writeLogs("getLocId: %s" %str(item), path_sn)
            print("getLocId:%s" %str(item))
            return  item[1]
    return None

def setKisStatus(_cableName, status, path_sn):
	"""
	# 设置Kis状态
	:param _cableName: _cableName
	:param status: 只接受 0/1/2. 0:关闭  1:强制开启  2:自动开启
	:param path_sn:
	:return:
	"""
	if str(status) not in ["0", "1", "2"] :
		#writeLogs("setKisStatus failed because status not (0/1/2).", path_sn)
		print("setKisStatus failed because status not (0/1/2).")

		exit(1)

	# 首先获取完整的ProbeName
	probeName = ""
	res, rev = readCMD(["astrisctl --host localhost list"], True, path_sn)
	try:
		if "-" in _cableName:
			_cableName = _cableName.split("-")[1].strip()
		probeName = [line for line in rev if re.search(_cableName, line)][0].strip()
	except:
		#writeLogs("getAstrisProbeName failed. CableName-%s" % _cableName, path_sn)
		print("getAstrisProbeName failed. CableName-%s" % _cableName, path_sn)
		exit(1)
	else:
		if probeName.strip() == "":
			#writeLogs("setKisStatus failed because probeName is Nil.", path_sn)
			print("setKisStatus failed because probeName is Nil.", path_sn)
			exit(1)

	res, rev = readCMD(["astrisctl --force-kick --host localhost:%s kis %s" %(probeName, status)], True, path_sn)
	if res and rev:
		if "failed" not in "\n".join(rev):
			print("True")
			exit(0)
	#writeLogs("setKisStatus failed. (res,rev) = (%s, %s)" %(res,rev), path_sn)
	print("setKisStatus failed. (res,rev) = (%s, %s)" %(res,rev), path_sn)
	exit(1)

##  根据cableName获取mode
def getConnState(_cableName, path_sn):
	"""
	:param _cableName: cableName, such as "cu.kanzi-30EE63"/"30EE63"
	:param path_sn: log_path or sn
	:return: device mode(str)  DFU/Recovery/iOS
	"""
	import re
	try:
		cableName = str(_cableName).split("-")[1].strip()
	except:
		cableName = str(_cableName)
	
	getLocIds = getLocIDAndMode()
	print ("DEBUG getLocIds={}".format(getLocIds))
	if len(getLocIds) > 0:
		for item in getLocIds:
			if item[0] == cableName:
				#writeLogs("getConnState: %s" %item[1], path_sn)
				print("getConnState: {}".format(item[2]), path_sn)
				return item[2]
	#writeLogs("getConnState failed.", path_sn)
	print("getConnState failed.", path_sn)
	print("state=")		## Unknonw mode
	return None


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
		#writeLogs("run_sysdiagnose_2 failed. can not get location id for cableName:%s" %cableName, sn)
		print("run_sysdiagnose_2 failed. can not get location id for cableName:%s" %cableName, sn)
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
					
					#writeLogs("run_sysdiagnose_2 sysdiagnose=%s" %(logpath), sn)
					print("run_sysdiagnose_2 sysdiagnose=%s" %(logpath), sn)
					print("sysdiagnose=%s" %(logpath))
					exit(0)

	#writeLogs("run_sysdiagnose_2 failed. sn=%s" %sn, sn)
	print("run_sysdiagnose_2 failed. sn=%s" %sn, sn)
	print("sysdiagnose=" )
	exit(1)

def run_iboot_cmd(cableName, sn, *args):
	conn_cmd = "nanokdp -d /dev/cu.kanzi-%s" %(cableName)	
	exp_cmd = """
	spawn nanokdp -d /dev/cu.kanzi-%s -L /tmp/panictools_uart.log
	expect {
		-re \"Use Ctrl\" { send \"\r\n\r\n\" } 
	}
	interact
	
	""" %(cableName)
	print ("exp_cmd={}".format(exp_cmd))
	res, rev = readCMD(['expect -c "{}".format(exp_cmd))'], False, sn)
	print ("rev = {}".format(rev))

	

## No need scout
def run_burnin_2(cableName, sn):
	"""
	# @Description: get burnin by cable name. 
	# @param cableName(str):
	# @return burnin_path(str) / None
	# Tips: burnin_path is a folder path.
	"""
	panic_log_host = DOCUMENT_PATH + "/PanicLog/"+sn+"/"    ##以SN命名Log文件夹
	os.makedirs(panic_log_host)
	location_id = getLocId(cableName, sn)

	if not location_id:
		#writeLogs("run_burnin_2 failed. can not get location id for cableName:%s" %cableName, sn)
		print("run_burnin_2 failed. can not get location id for cableName:%s" %cableName, sn)
		exit(11)

	# 转储log到指定路径
	cmd = "/usr/local/bin/copyUnrestricted -u %s -s /private/var/logs/Astro -t %s" %(location_id, panic_log_host)
	# /private/var/logs/Astro
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
			
			#writeLogs("run_burnin burnin=%s" %logpath, sn)
			print("run_burnin burnin=%s" %logpath, sn)
			print("burnin=%s" %logpath)
			exit(0)
	#writeLogs("Cable:%s burnin log failed."%(cableName), sn)
	print("Cable:%s burnin log failed."%(cableName), sn)
	print("burnin=")
	exit(1)

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
		#writeLogs("ERROR: run_OS_CMDs params incorrect.")
		print("ERROR: run_OS_CMDs params incorrect.")
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
		#writeLogs("run_OS_CMDs failed. can not get location id for sn:%s" %sn, sn)
		print("run_OS_CMDs failed. can not get location id for sn:%s" %sn, sn)
		exit(1)
	
	tcp_port = 10000	## init tcp_port value to 10000
	tcp_proc_id = "" 	## tcprelay process id (str)
	
	## 1. Get eixsts tcprelay_ports list
	res, tcp_port_list = readCMD(["lsof -i tcp | grep tcprelay | awk -F ':' '{print $2}' | awk -F ' ' '{print $1}' | awk -F/ '!a[$1,$2]++'"], True, sn)
	if tcp_port_list and len(tcp_port_list)>0:
		## Produce a legal tcp_port for a new tcprelay connection.
		#while (str(tcp_port+23) in tcp_port_list):
		while (str(tcp_port+23) in tcp_port_list):
			tcp_port = tcp_port + 1

	TelnetExpPath = "%s/auto_telnet.exp" %script_path
	## 2. Start tcprelay monitor.
	tcp_cmd = "%s/runTcprelay.exp %s %d %s " %(script_path, loc_id, tcp_port, TelnetExpPath)
	for item in cLogsList:
		#writeLogs("Running tcp_cmd:%s"%(tcp_cmd + item), sn)
		print("Running tcp_cmd:%s"%(tcp_cmd + item), sn)

		#res , rev = readCMD(["%s '%s'" %(tcp_cmd,item)], True, sn)
		res , rev = readCMD([script_path+"runTcprelay.exp", loc_id, str(tcp_port), TelnetExpPath, item], False, sn)
		if res and rev:
			#writeLogs("run_OS_CMDs rev=%s" %rev , sn)
			print "\n".join(rev)
			return rev
	#writeLogs("run_OS_CMDs failed. sn:%s" %sn, sn)
	print("run_OS_CMDs failed. sn:%s" %sn, sn)

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
	#writeLogs("handle_OSCMD_Rev handle_rev_list=%s" %handle_rev_list, sn)
	print("handle_OSCMD_Rev handle_rev_list=%s" %handle_rev_list, sn)
	return handle_rev_list	


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
		#writeLogs("Warning: Already exec reset, but maybe the cable:%s is not connecting to unit." %cableName, sn)
		print("Warning: Already exec reset, but maybe the cable:%s is not connecting to unit." %cableName, sn)
		readCMD([script_path+"/auto_reset.exp", "0"], False, sn)
	else:
		#writeLogs("The cable '%s' will be reset later." %cableName, sn)
		print("The cable '%s' will be reset later." %cableName, sn)
		readCMD([script_path+"/auto_reset.exp", probe_id], False, sn)

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
#	writeLogs("readCMD args=%s" %args, logpath)
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
			#writeLogs_EXP(buff, logpath)
	if p.wait() == 0:
		res = True

	return (res, rev)         ## res(Bool): The cmd is running successful?
							## rev(list): The cmd result list.

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

main()
