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
import time
import commands
import subprocess
from subprocess import Popen

#----------------------------路径(调试1)----------------------------------------
#script_path = os.environ['HOME']+"/Desktop/AutoPanic.app/Contents/Resources/"
#------------------------------------------------------------------------------

#----------------------------路径(调试2)----------------------------------------
script_path = os.path.split(os.path.realpath(__file__))[0]+"/" # Current script real path.
#------------------------------------------------------------------------------

marvin_path = "/usr/local/bin/marvin"
astris_path = "/usr/local/bin/astris"
LOG_PATH = "/tmp/panic_tool_package.log"    ## Log路径 - 和Swift中的log输出路径一致


# 根据proc_id关闭tcprelay进程
def kill_tcprelay(proc_id):
        readCMD(["kill -9 %s " %str(proc_id) ], True)
        writeLogs("Tcprelay PID-%s is closed." %(str(proc_id)))

def getMarvinProbeID(cableName):
	"""
	# Get Marvin Probe ID for expect auto run.
	# @param cableName(str):
	# @return probeID(int):  //If get null, return -1
	"""
	# 处理未格式化的 cablename 字符串
	cableName_0 = cableName
	if re.search("-", cableName_0):
		cableName_0 = cableName_0.split("-")[1]
	# writeLogs("Python script current path = %s" %script_path)
	res, rev = readCMD(["%s/runMarvin.rep"%(script_path)], False, 2)
	for item in rev:
		if re.search(cableName_0, item):
			return re.search( "[0-9]?", item).group()     ## probeID
	return "-1"

def getAstrisProbeID(cableName):
	"""
		# Get Astris Probe ID for expect auto run.
		# @param cableName(str):
		# @return probeID(int):  //If get null, return -1
		"""
	# 处理未格式化的 cablename 字符串
	cableName_0 = cableName
	if re.search("-", cableName_0):
		cableName_0 = cableName_0.split("-")[1]
	# writeLogs("Python script current path = %s" %script_path)
	res, rev = readCMD([script_path+"/auto_reset.rep", "-1"], False)
	for item in rev:
		if re.search(cableName_0, item):
			return re.search( "[0-9]?", item).group()     ## probeID
	return "-1"

def run_marvin(cableName, args):
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

	    # Run marvin factory
        probe_id = getMarvinProbeID(cableName)
        args.insert(0, probe_id)        ## Put key "probe_id" to args
        args.insert(0, script_path+"/auto_marvin.rep")      ## Put the cmd script path to args
		
        writeLogs("run_marvin args = %s" %args)
        res, rev = readCMD(args, False)
        writeLogs("run_marvin rev = %s" %rev)
        # Get panic type
        panic_type="Unknown"
        panic_log=""
        panic_log_host=""
        for item in rev:
                if item=='Explore Failure':
						# Some bug in it 🚩
                        if 'marvin crashed' in rev:
                                panic_type = "marvin crashed"
                                writeLogs("marvin crashed.")
                                exit(1)
                elif item=='-System Triage-':
                        panic_type=rev[rev.index(item)+2].strip()  ## strip() 默认是去字串首尾空格
                elif "factory-debug.zip" in item:
                        panic_log=item
                        panic_log_host="/Users/gdlocal/Desktop/"+args[8]+"/"    ##以SN命名Log文件夹
                        readCMD(["/bin/mkdir","-p",panic_log_host], False)
						#writeLogs("panic_log=%s, panic_log_host=%s" %(panic_log,panic_log_host))
                        (res, rev2) = readCMD(["/bin/mv", panic_log, panic_log_host], False)
                        if res==True:
                                writeLogs("Corefile has been moved to localhost.")
                                panic_log = panic_log_host+"/factory-debug.zip"
        return (res, rev, panic_type, panic_log)


def run_jebdump(cableName, args=[]):
	"""
	# @Description: get jebdump by cable name.
	# @param cableName(str):
	# @param args(list): args[0]=<probe_id> args[1]=<rep._script_path> args[3...]=<rep._script_args>
	#			'args' can be NULL.
	# @return jebdump_path(str) / None
	"""
	probe_id = getMarvinProbeID(cableName)
	args.insert(0, probe_id)        ## Put key "probe_id" to args	
	args.insert(0, script_path+"/auto_jebdump.rep")      ## Put the cmd script path to args
	res, rev = readCMD(args, False)
	for item in rev:
		info = re.search("/(.*).zip", item)
		if info:
			return info.group()
	writeLogs("Cable:%s jebdump log failed."%(cableName))
	return None

def run_reboot(cableName, args):
	writeLogs("Start Cable:%s reboot log collecting."%(cableName))
	sn = args[0]
	reboot_log_host="/tmp/reboot_%s.log" %sn    ##以SN命名Log文件夹
	## readCMD 在这里的超时时间设置无效，在auto_reboot.rep里面默认设置25s
	res, reboot_log_str = readCMD(["%s/auto_reboot.rep %s >> %s" %(script_path, cableName, reboot_log_host)], True, 25)
	writeLogs("reboot_log_str=%s" %reboot_log_str)
	return reboot_log_host

def run_sysdiagnose(cableName):
	"""
	# @Description: get sysdiagnose by cable name.
	# @param cableName(str):
	# @param args(list): args[0]=<probe_id> args[1]=<rep._script_path> args[3...]=<rep._script_args>
	#			'args' can be NULL.
	# @return sysdiagnose_path(str) / None
	"""
	args=[]
	probe_id = getMarvinProbeID(cableName)
	args.insert(0, probe_id)        ## Put key "probe_id" to args	
	args.insert(0, script_path+"/auto_sysdiagnose.rep")      ## Put the cmd script path to args
	res, rev = readCMD(args, False)
	for item in rev:
		info = re.search("/(.*).tar.gz", item)
		if info:
			return info.group()
	writeLogs("Cable:%s sysdiagnose log failed."%(cableName))
	return None

# Need to zip log files (Coding ongoing)
def run_burnin(cableName):
	"""
	# @Description: get burnin by cable name. 
	# @param cableName(str):
	# @return burnin_path(str) / None
	# Tips: burnin_path is a folder path.
	"""
	probe_id = getMarvinProbeID(cableName)
	args=[]
	args.insert(0, probe_id)        ## Put key "probe_id" to args	
	args.insert(0, script_path+"/auto_burnin.rep")      ## Put the cmd script path to args
	res, rev = readCMD(args, False)
	for item in rev:
		info = re.search("/(.*)LogCollector", item)
		if info:
			return info.group()
		if "File exists:" in item:	## Burnin file has exists
			return re.search("/(.*)[0-9]{12}", info).group() + "/LogCollector"
	writeLogs("Cable:%s burnin log failed."%(cableName))
	return None

##  现在还不能用，待修改 🚩
def getLocId(cableName):
    pass

def run_remote():
	"""
	# @Description: Runing  OS CMDs on OS mode.
	# @param cableName(str)
	# @param args(list):	which CMDs run on OS mode
	# @return resultStr(str) / None
	"""
	#probe_id = getMarvinProbeID(cableName)
	#args.insert(0, probe_id)        ## Put key "probe_id" to args
	#args.insert(0, script_path+"/auto_remote.rep")      ## Put the cmd script path to args
	#res, rev = readCMD(args, False)
	#return res, rev
	res, rev = readCMD(["scout remote &"], False)
	return res

##  现在还不能用，待修改 🚩
def getOSLogs(cableName, cLogsList):
	#remove_burnin_args()
	#astris_reset(cableName)  # OK
	#
	#get_reboot_log()
	#loc_id = getLocId(cableName)
    
	## init tcp_port value to 10000
	tcp_port = 10000
	## tcprelay process id (str)
	tcp_proc_id = ""

	try:
		## 1. Get eixsts tcprelay_ports list
		res, tcp_port_list = readCMD(["lsof -i tcp | grep tcprelay | awk -F ':' '{print $2}' | awk -F ' ' '{print $1}' | awk -F/ '!a[$1,$2]++'"], True)
		if res:
			## Produce a legal tcp_port for a new tcprelay connection.
			while (str(tcp_port+23) in tcp_port_list):
				tcp_port = tcp_port + 1
        
		## 2. Start tcprelay monitor.
		#    res, rev = readCMD(["tcprelay --locationid %s --portoffset %s 873 23" %(loc_id, tcp_port_list) ], True)
		res, rev = readCMD(["/usr/local/bin/tcprelay --portoffset  '%d' '%d' '%d' &" %(tcp_port,  873, 23)], True, 1)
	        #    if res: ## 'res' is always False, should not be judged.
        
		## 3. Get Current tcprelay proc_id
		telnet_port = tcp_port + 23
		res, rev = readCMD( ["lsof -i tcp:%s | awk -F ' ' '{print $2}' | sed '/PID/d' | awk -F/ '!a[$1,$2]++'" %(telnet_port)], True)
		tcp_proc_id = rev[0]
		writeLogs("Current tcprelay process_id = %s" %tcp_proc_id)
        
		#get_sysdiagnose_log()
		#get_crstackshot_log()
		#get_Burnin_logs(locID, logPathInUnit, logPathToLocal)
        
		## 4. Open telnet connection
		#telnet_cmd = script_path + "/auto_telnet.rep %s %s" %( str(telnet_port), str(cLogsList.count))
		telnet_cmd = script_path + "/auto_telnet.rep ls pwd"
		#res, telnet_rev = readCMD( [script_path+"/auto_telnet.rep %s %s" %(str(tcp_port + 23), str(cLogsList.count)) ], True)
		telnet_rev_list = []
	        #	cLogsList.append("exit")
        	for item in cLogsList:
			telnet_cmd = telnet_cmd + ' "%s" "%s" ' %( telnet_port, item)
			res, rev = readCMD( [telnet_cmd ], True)
			telnet_rev_list.append(rev)
#			yield telnet_rev_list
		        if "Connection closed by foreign host." in rev and "Connection closed by foreign host." not in rev[-1]:
				writeLogs("Telnet port-%s open failed, OS cmd executed failed." %(telnet_port) )
				kill_tcprelay(tcp_proc_id)
				return res, telnet_rev_list
	except Exception as e:
        	writeLogs(e)
	        # Kill Tcprelay conn
        	kill_tcprelay(tcp_proc_id)
	else:
		# Kill Tcprelay conn
		kill_tcprelay(tcp_proc_id)
		return res, telnet_rev_list

def createRadar(corefilePath, reportPath):
    """
	# @Description: createRadar and upload corefile to Radar, export panic report data.
	# @param corefilePath(str):
	# @param reportPath(str): Panic report file path
	"""
    args = []
    rep_path = script_path+"/auto_fileradar.rep"
    scout_cmd = '"scout radar --attachment %s --report %s"' %(corefilePath, reportPath)
    ifNewUmbreRadar = "n"
    ifRelateToUmbreRadar = "n"
    args.append(rep_path)
    args.append(scout_cmd)
    args.append(ifNewUmbreRadar)
    args.append(ifRelateToUmbreRadar)
	
    res, rev = readCMD(args, False)
    if not res:
        print("[Error] createRadar failed..")
        print(res, rev)

	
def astris_reset(cableName):
        '''
        ##########################################
        #@Descript astris_reset is for a Unit/MLB reset opt.
        #@param cableName(str)
        #@return None
        ##########################################
        '''
        import re
        # Get Probe number
        probe_id=getAstrisProbeID(cableName)
        if probe_id == "-1":
            writeLogs("WARNING: Already exec reset, but maybe the cable:%s is not connecting." %cableName)
        else:
            writeLogs("The cable '%s' will be reset later." %cableName)
            readCMD([script_path+"/auto_reset.rep", probe_id], False)
        
	
# 异常处理方法
def handler(signum, frame):
#        raise AssertionError
	pass

def readCMD(args=[], isShell=True, timeout=-1):
        '''
        #Running the command and read String from stdout.
        #@param args(list): cmd script path & cmd params
        #@param isShell(Bool): The cmd is shell cmd or not.
        #@param timeout(int): set timeout(must > 0), default -1 means never timeout
        #@return (res, rev): res: result status code
        #                   rev: result string
        '''
        if timeout < 0 and timeout != -1:
                writeLogs("Timeout setting value illegal")
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
# 字符串转列表
def str_to_list(str):
    """
    # 字符串转列表
    # @param str(str): string
    # @return []
    """
    try:
        info = str.split(",") ##只转化以空格分隔的字符串
        return info
    except Exception as e:
        print(e)
        return []
# 列表转字符串
def list_to_str(lt):
    return " ".join(lt) ##以空格分隔的字符串

# str写入log
def writeLogs(info):
    """
    # 所有print输出都应写入log文件，使用writeLogs方法
    # @param info(str):log
    # @return none
    """
	## print("PYT > %s" %info)     ## 仍然做一个终端输出以做调试
    import datetime
    now = datetime.datetime.now()
    with open(LOG_PATH, 'a+') as f:
        try:
            f.write("PYT:[%s] %s \n" %(now, info))
        except Exception as e:
            #f.write("PYT:[%s] %s \n" %(now,e))
            print("Write to Logs Error: %s" %e)
            #exit(250)

# str写入log
def writeLogs_EXP(info):
	"""
		# 所有print输出都应写入log文件，使用writeLogs方法
		# @param info(str):log
		# @return none
		"""
	## print("PYT > %s" %info)     ## 仍然做一个终端输出以做调试
	import datetime
	now = datetime.datetime.now()
	with open(LOG_PATH, 'a+') as f:
		try:
			f.write("EXP:[%s] %s \n" %(now, info))
		except Exception as e:
			#f.write("PYT:[%s] %s \n" %(now,e))
			print("Write to Logs Error: %s" %e)
#exit(250)

def test():
	writeLogs("PyScript Testing... args = 1")
	writeLogs("PyScript Testing... args = 2")
	time.sleep(1)
	writeLogs("PyScript Testing... delay args = 3")
	time.sleep(1)
	writeLogs("PyScript Testing... delay args = 4")






print(getOSLogs('30F455', ['ls','pwd']))

exit(0)

## Swift 调用 Python的入口开始
import sys

func_name = ""
func_args = []
res = False

if len(sys.argv) < 2:
    print("Usage: ./PanicToolPackage.py <pyFunc> <arg1> <arg2>...")
    exit(255)
try:
    func_name = str(sys.argv[1])
except Exception as e:
    print("Python Func Unknown Error:", e)
    exit(1)

if func_name == 'run_marvin':
    cableName = sys.argv[2]
    args = str_to_list(sys.argv[3])
    writeLogs("run_marvin...%s . args=%s" %(cableName,args))
    #print("DEBUG 11: cablename = %s ; args = %s" % (cableName, args))
#   args = ["D42_EVT_BUILD","D42_EVT_FF","YukonNanshan16A999","Burnin","Black","3CAA","C39XXX_001"]
    (res, rev, panic_type, panic_log) = run_marvin(cableName,args)
    print("res=%s" %res)
    print("rev=%s" %rev)
    print("type=%s" %panic_type)
    print("log=%s" %panic_log)
#    print("res=True")
#    print("rev=TEST")
#    print("type=Kernel Panic!")
#    print("log=TEST_LOG")
  
			  
elif func_name == 'run_jebdump':
    cableName = sys.argv[2]
    writeLogs("run_jebdump...%s" %cableName)
    try:
        jebdump_path = run_jebdump(cableName)
    except Exception as e:
        writeLogs(e)
        print("jebdump=None")
    print("jebdump=%" %jebdump_path)

elif func_name == 'run_burnin': 	## 注意⚠️不支持多线程
    cableName = sys.argv[2]
    writeLogs("run_burnin...%s" %cableName)

    res, rev = readCMD(["/bin/ps -ef | grep 'scout remote' | awk -F ' ' '{print $2}'"], True)
    for item in rev:
        readCMD(["/bin/kill -9 %s" %item], True)
	
    readCMD(["scout remote &"], True)
    try:
        burnin_path = run_burnin(cableName)
        print("burnin=%s" %burnin_path)
    except Exception as e:
        writeLogs(e)
        print("burnin=None")

			  
elif func_name == 'run_sysdiagnose':	## 注意⚠️不支持多线程
    cableName = sys.argv[2]
    writeLogs("run_sysdiagnose...%s" %cableName)
    try:
        sysdiagnose_path = run_sysdiagnose(cableName)
    except Exception as e:
        writeLogs(e)
        print("sysdiagnose=None")
    print("sysdiagnose=%s" %sysdiagnose_path)
			  
elif func_name == 'astris_reset':
    cableName = sys.argv[2]
    writeLogs("astris_reset...%s" %cableName)
    astris_reset(cableName)


elif func_name == 'run_remote':			## 注意⚠️不支持多线程
    cableName = sys.argv[2]
    #args = str_to_list(sys.argv[3])
    writeLogs("run_remote...%s. args=" %(cableName))
    #   args = ["D42_EVT_BUILD","D42_EVT_FF","YukonNanshan16A999","Burnin","Black","3CAA","C39XXX_001"]
    #try:
    #    run_remote(cableName,args)
    #except Exception as e:
    #    writeLogs(e)
    res = run_remote()
    print("res=%s" %res)

elif func_name == 'run_reboot':
    cableName = sys.argv[2]
    args = str_to_list(sys.argv[3])
    writeLogs("run_reboot...%s" %cableName)
    log_path = run_reboot(cableName, args)
    print("log=%s" %log_path)
			  
elif func_name == 'createRadar':
    cableName = sys.argv[2]
    writeLogs("createRadar...%s" %cableName)
			  
    #createRadar
elif func_name == 'logout_AC':
    writeLogs("logout_AppleConnect")
    try:
        readCMD(["scout devalidate"], True)
    except Exception as e:
        writeLogs(e)
    print("Done.")

elif func_name == 'getOSLogs':
    cableName = sys.argv[2]
    cLogsList = str_to_list(sys.argv[3])
    cableName = sys.argv[2]
    writeLogs("createRadar...%s . cLogsList=%s" %(cableName,cLogsList))
    #   args = ["D42_EVT_BUILD","D42_EVT_FF","YukonNanshan16A999","Burnin","Black","3CAA","C39XXX_001"]
    (res, telnet_rev_list) = getOSLogs(cableName,cLogsList)
    print("res=%s" %res)
    print("list=%s" %list)

elif func_name == 'test':
    test()
    writeLogs("func test")
    print("Done.")
else:
    print("Func:%s Not Found Error" %func_name)
    writeLogs("Func:%s Not Found Error" %func_name)
	
