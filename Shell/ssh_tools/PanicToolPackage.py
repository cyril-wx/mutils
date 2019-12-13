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

    (res, rev)=readCMD(['/usr/sbin/system_profiler SPUSBDataType | egrep "DCSD USB UART:|Kanzi:|iPhone|Serial Number:*|Location ID:*|Apple Mobile Device*"'], True)
    result = []

    info_arr = rev.split("\n")
    info_arr_count=len(info_arr)
    for i in range(info_arr_count):
#       print("[H] %s" %info_arr[i])
        a = (
            re.search("iPhone:", info_arr[i]),          # OS mode
            # re.search("Apple Mobile Device \(Recovery Mode\):", info_arr[i]), # Recovery mode
            re.search("Recovery Mode", info_arr[i]), # Recovery mode
            # re.search("Apple Mobile Device \(DFU Mode\):", info_arr[i]))      # DFU mode
            re.search("DFU Mode", info_arr[i]))      # DFU mode

        if a[0] or a[1] or a[2]:
            if a[0]:
                mode = "iOS"
            elif a[1]:
                mode = "Recovery"
            elif [2]:
                mode = "DFU"
            else:
                continue
            
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
    print("getLocIDAndMode:%s" %str(result))
    return result

##  根据cableName获取LocationID
def getLocId(_cableName):
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
        if item[0] == cableName:
            print("getLocId:%s" %str(item))
            return  item[1]
    return None

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
			print("getConnState failed.", path_sn)
			print("state=")	## Unknonw mode
		for item in getLocIds:
			if item[0] == cableName:
				print("state=%s" %item[1])
				print("getConnState: state-%s" %item[1], path_sn)
	print("getConnState failed.", path_sn)
	print("state=")		## Unknonw mode


def setKisStatus(_cableName, openOrClose=False):
        """
        # 设置Kis状态
        :param _cableName: _cableName
        :param status: 只接受 True/False  开/关
        :return:
        """

        # 首先获取完整的ProbeName
        probeName = ""
        res, rev = readCMD(["astrisctl --host localhost list"], True)
        try:
                if "-" in _cableName:
                        _cableName = _cableName.split("-")[1].strip()
                probeName = [line for line in rev if re.search(_cableName, line)][0].strip()

        except:
                print("getAstrisProbeName failed. CableName-%s" % _cableName)
                return False
        else:
                if probeName.strip() == "":
                        print("setKisStatus failed because probeName is Nil.")
                        return False

        if openOrClose:
                # 打开 kis
                res, rev = readCMD(["astrisctl --force-kick --host localhost:%s kis 2" %(probeName)], True)
        else:
                # 关闭 kis
                res, rev = readCMD(["astrisctl --force-kick --host localhost:%s kis 0" %(probeName)], True)
        rev_str = "\n".join(rev)
        if res and rev:
                if not re.search("fail|Fail", rev_str):
                        print("set kis={}".format(status))
                        return True
        print("setKisStatus failed. ") #(res,rev) = (%s, %s)" %(res,rev)
        return False


def getMarvinProbeID(cableName):
	"""
	# Get Probe ID in running marvin.
	# @param cableName(str):
	# @return probeID(int):  //If get null, return -1
	"""
	# 处理未格式化的 cablename 字符串
	cableName_0 = cableName
	if re.search("-", cableName_0):
		cableName_0 = cableName_0.split("-")[1]
	res, rev = readCMD(["%s/runMarvin.exp"%(script_path)], True)
	time.sleep(1)
	
	#print("[*] rev={}".format(rev))
	try:
		probeID=re.search("\d+\) KanziSWD-%s" %(cableName_0), rev).group().strip()[:-17]
		print("getMarvinProbeID probeID=%s" %probeID)
		return probeID
	except Exception as e:
		#print(e)			
		print("getMarvinProbeID failed. cableName: %s" %cableName)
		return None

def getAstrisProbeID(cableName):
	"""
	# Get Probe ID in running astris.
	# @param cableName(str):
	# @return probeID(int):  //If get null, return -1
	"""
	# 处理未格式化的 cablename 字符串
	cableName_0 = cableName
	if re.search("-", cableName_0):
		cableName_0 = cableName_0.split("-")[1]
	status, rev = readCMD([script_path+"/runAstrisID.exp"], True)
	time.sleep(1)
	#print("[*] rev={}".format(rev))
	try:
		probeID=re.search("\d+\) KanziSWD-%s" %(cableName_0), rev).group().strip()[:-17]
		print("getAstrisProbeID: probeID=%s" %(probeID))
		return probeID     ## probeID
	except Exception as e:
		if re.search("KanziSWD-%s" %(cableName_0), rev):
			print("getAstrisProbeID failed: set default probeID=0")
			return 0  # 这里即使fail也不代表获取ProbeID失败，因为是可能只有一根线连接被识别，默认返回ID=0
		else:
			print(e)
			print("getAstrisProbeID failed. cableName: %s" %cableName)
			return None


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
		print("ERROR: run_OS_CMDs params incorrect.")
		exit(10)

	cableName = args[0]
	sn = args[1]
	cLogsList = args[2:]
	print("cLogsList=%s" %str(cLogsList))
	rev = "" 	## OS command return value strings.
	sysdiagnose_log = ""
	loc_id = getLocId(cableName)
	if not loc_id:		## 没有获取到Location id则直接退出
		print("rev=")
		print("run_OS_CMDs failed. can not get location id for sn:%s" %sn, sn)
		exit(1)
	
	tcp_port = 10000	## init tcp_port value to 10000
	tcp_proc_id = "" 	## tcprelay process id (str)
	
	## 1. Get eixsts tcprelay_ports list
	res, tcp_port_list = readCMD(["lsof -i tcp | grep tcprelay | awk -F ':' '{print $2}' | awk -F ' ' '{print $1}' | awk -F/ '!a[$1,$2]++'"], True)
	if tcp_port_list and len(tcp_port_list)>0:
		## Produce a legal tcp_port for a new tcprelay connection.
		while (str(tcp_port+23) in tcp_port_list):
			tcp_port = tcp_port + 1

	TelnetExpPath = "%s/auto_telnet.exp" %script_path
	## 2. Start tcprelay monitor.
	tcp_cmd = "%s/runTcprelay.exp %s %d %s " %(script_path, loc_id, tcp_port, TelnetExpPath)
	for item in cLogsList:
		print("Running tcp_cmd:%s"%(tcp_cmd + item), sn)
		#res , rev = readCMD(["%s '%s'" %(tcp_cmd,item)], True)
		res , rev = readCMD([script_path+"runTcprelay.exp", loc_id, str(tcp_port), TelnetExpPath, item], False)
		if res and rev:
			#print("run_OS_CMDs rev=%s" %rev , sn)
			print "\n".join(rev)
			return rev
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
		print("Warning: Already exec reset, but maybe the cable:%s is not connecting to unit." %cableName, sn)
		readCMD([script_path+"/auto_reset.exp", "0"], False)
	else:
		print("The cable '%s' will be reset later." %cableName, sn)
		readCMD([script_path+"/auto_reset.exp", probe_id], False)


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
			print("Expect script command:\n%s \nreturn_status:%s" % (cmd1, res1))
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

def startSyncData(syncTime=15):
	"""
	# 开启同步任务（默認15s一次）
	:return: Never (Only when program exit and return False)
	"""
	import time

	(res, rev) = readCMD(["ps -ef | grep 'PanicToolPackage.py startSyncData' | grep -v 'grep' | awk -F ' ' '{print $2}'"], True)
	if len(rev) > 1:
		print("startSyncData already in starting.")
		exit(0)
	else:
		print("startSyncData...")

	while True:
		sync_Adapter()
	#time.sleep(600)
		time.sleep(syncTime)
	return False


def readCMD(args=[], isShell=True):
	'''
	#Running the command and read String from stdout.
	#@param args(list): cmd script path & cmd params
	#@param isShell(Bool): The cmd is shell cmd or not.
	#@return (res, rev): res: result status code
	#                   rev: result string
	'''
	import subprocess
	from subprocess import Popen
	
	res = False
	rev = []
	#print("readCMD args=%s" %args, logpath)
	p = subprocess.Popen( args, shell=isShell, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

	(rev, status) = p.communicate()
	return (status, rev)         ## res(Bool): The cmd is running successful?
							## rev(list): The cmd result list.

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


def run_marvin(cableName, args=[]):
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

        if (not args) :
                print("ERROR: run_marvin params incorrect.")
                exit(1)

        # Get panic type
        result=True
        panic_type="Unknown"
        panic_log=""
        panic_log_host = DOCUMENT_PATH + "/PanicLog/"+args[-1]+"/"    ##以SN命名Log文件夹

        sn_no = args[6]

        _args = args[:]

        # Judge device connection status
        if getLocId(cableName):
                panic_type = "Error: Device current in DFU/Recovery/iOS mode."
                print (panic_type)
                exit(2)

	# Run marvin factory
        probe_id = getMarvinProbeID(cableName)
        if not probe_id:
               panic_type = "ERROR: No probes connected" 
               print (panic_type)
               exit(3)

        _args.insert(0, probe_id)        ## Put key "probe_id" to args
        _args.insert(0, script_path+"/auto_marvin.exp")      ## Put the cmd script path to args
	
        time.sleep(1)
        marvin_log = readCMD(_args, False)
	res, rev = marvin_log[0], marvin_log[1].split("\n")
        print ("rev=%s" %rev)
       
        for item in rev:
                if re.search("Passive Coredump : Failed!", item):
                        result=False
                elif re.search('Explore Failure', item):
                        # Some bug in it 🚩
                        if re.search('marvin crashed', "\n".join(rev)):
                                panic_type = "marvin crashed"
                                result=False
                                print("marvin crashed.")
                elif re.search('-Report-', item):
                        panic_type=rev[rev.index(item)+2].strip()  ## strip() 默认是去字串首尾空格
#               elif re.search('-System Triage-', item):
#                       panic_type=rev[rev.index(item)+2].strip()  ## strip() 默认是去字串首尾空格

                elif "factory-debug.zip" in item:
                        panic_log=item
                        readCMD(["/bin/mkdir","-p",panic_log_host], False)
                        (res, rev2) = readCMD(["/bin/mv", panic_log, panic_log_host], False)

                        try:
                                radar_txt = panic_log.replace("factory-debug.zip", "radar.txt")
                                readCMD(["/bin/mv", radar_txt, panic_log_host], False)
                        except:
                                print("Move radar.txt file failed.")

                        if res==True:
                                print("Corefile has been moved to localhost.")
                                panic_log = panic_log_host+"/factory-debug.zip"

        # replace “//” as “/”
        try:
                pattern = re.compile(r"(/{2,}?)")
                panic_log = re.sub(pattern, "/", panic_log)
        except Exception as e:
                print("panic_log get failed: %s" %e )

        print("res=%s" %result)
        print("type=%s" %panic_type)
        print("log=%s" %panic_log)
        print("done")

        return (res, rev, panic_type, panic_log)



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
