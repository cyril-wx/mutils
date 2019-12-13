#!/usr/bin/python
# -*- coding:utf-8 -*-

import pexpect
import getpass
import time
from MyLogger import MyLogger
from ExecTimeAnalysis import func_time
from ExecTimeAnalysis import func_cprofile
from jc import utils
import sys

try:
    raw_input
except NameError:
    raw_input = input


# SMTP:25 IMAP4:143 POP3:110
# tunnel_command = 'ssh -C -N -f -L 25:127.0.0.1:25 -L 143:127.0.0.1:143 -L 110:127.0.0.1:110 %(user)@%(host)'
#tunnel_command = "ssh %(user)@%(host)"


def get_process_info ():

    # This seems to work on both Linux and BSD, but should otherwise be considered highly UNportable.

    ps = pexpect.run ('ps ax -O ppid')
    pass

def start_tunnel ():
    tunnel_command = "ssh coreos@10.172.245.109"
    host = raw_input('Hostname: ')
    user = raw_input('Username: ')
    X = getpass.getpass('Password: ')

    try:
        ssh_tunnel = pexpect.spawn (tunnel_command % globals())
        ssh_tunnel.expect("(yes/no)")
        time.sleep(0.1)
        ssh_tunnel.sendline("yes\r")
        ssh_tunnel.expect ('Password:')
        time.sleep (0.1)
        ssh_tunnel.sendline ("helloworld")
        time.sleep(3)
        ssh_tunnel.sendline("")
        time.sleep (1) # Cygwin is slow to update process status.
        ssh_tunnel.interact()
        #ssh_tunnel.expect (pexpect.EOF)

    except Exception as e:
        print(str(e))

def main ():
    start_tunnel()
    """
    while True:
        ps = pexpect.spawn ('ps')
        time.sleep (1)
        index = ps.expect (['/usr/bin/ssh', pexpect.EOF, pexpect.TIMEOUT])
        if index == 2:
            print('TIMEOUT in ps command...')
            print(str(ps))
            time.sleep (13)
        if index == 1:
            print(time.asctime())
            print('restarting tunnel')
            start_tunnel ()
            time.sleep (11)
            print('tunnel OK')
        else:
            # print 'tunnel OK'
            time.sleep (7)
    """


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
    # print("readCMD args=%s" %args, logpath)
    p = subprocess.Popen(args, shell=isShell, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    (rev, status) = p.communicate()
    return (status, rev)  ## res(Bool): The cmd is running successful?


## rev(list): The cmd result list.

@func_time
def test_pexpect():

    child = pexpect.spawn("ls", ["-al"])
    child.timeout=100
    child.logfile=sys.stdout
    child.expect(pexpect.EOF)
    child.close()
    """

    ret = pexpect.run("ls -al", withexitstatus=True, timeout=-1)
    print (ret[1], ret[0], )
    """

@func_time
def test_readCMD():
    status, rev = readCMD(['/bin/bash -c "find / -iname test | grep test > logs.txt"'], True)
    print status, rev


def test_run():
    (command_output, exitstatus) = pexpect.run("ls -al", timeout=-1, withexitstatus=True, logfile="/tmp/test.txt")
    print exitstatus, command_output

def test_ssh():
    import sys
    import pexpect

    # User& PWD
    username = "coreos"
    pwd = "helloworld"
    remote_ip = "10.173.140.230"

    # FTP服务器的标准提示符
    sshPrompt = '(.*)coreos\$'

    # 启动FTP服务器，并将运行期间的输出都放到标准输出中
    process = pexpect.spawn('/usr/bin/ssh %s@%s' %(username, remote_ip))
    process.logfile_read = sys.stdout

    # 服务器登陆过程

    key_pattern = [
        "Are you sure you want to continue connecting",
        '[Nn]ame',
        '[Pp]assword',
        pexpect.EOF,
        pexpect.TIMEOUT]

    #process.expect("Are you sure you want to continue connecting (yes/no)")
    #process.sendline('yes')
    #process.expect('[Nn]ame')
    #process.sendline('coreos')
    process.expect('[Pp]assword')
    process.sendline(pwd)

    # 先自动输入一些预定命令
    cmdList = ("ls", 'whoami', "exit")

    for cmd in cmdList:
        process.expect(sshPrompt)
        process.sendline(cmd)

    process.expect(sshPrompt)
    # 在这里将FTP控制权交还给用户，用户输入完成后按 ctrl+] 再将控制权还给脚本
    # ctrl+] 交还控制权给脚本是默认值，用户还可以设置其他的值，比如 ‘\x2a’
    # 就是用户按星号的时候交还。这个值实际上是 ASCII 的16进制码，它们的对应关系
    # 可以自己去其他地方找一下，但是注意必须是16进制的，并且前缀是 \x
    process.interact()

    # 当用户将控制权交还给脚本后，再由脚本退出ftp服务器
    # 注意下面这个空的sendline()命令，它很重要。用户将控制权交还给脚本的时候，
    # 脚本缓存里面是没任何内容的，所以也不可能匹配，这里发送一个回车符会从服务器取得
    # 一些内容，这样就可以匹配了。
    # 最后的EOF是确认FTP连接完成的方法。
    process.sendline()
    process.expect(sshPrompt)
    process.sendline('exit')
    process.expect(pexpect.EOF)

def test_demo1():
    import os
    # User& PWD
    username = "coreos"
    pwd = "helloworld"
    remote_ip = "10.173.140.230"

    # FTP服务器的标准提示符
    sshPrompt = '(.*)coreos\$'

    # 启动FTP服务器，并将运行期间的输出都放到标准输出中
    process = pexpect.spawn('/usr/bin/ssh %s@%s' % (username, remote_ip))
    process.logfile_read = sys.stdout

    # 服务器登陆过程

    key_pattern = [
        "Are you sure you want to continue connecting",
        'assword',
        sshPrompt,
        pexpect.EOF,
        pexpect.TIMEOUT]

    while True:
        index = process.expect(key_pattern, timeout=-1)
        if index == 0:
            process.sendline("yes")
            pass
        elif index == 1:
            process.sendline(pwd)
            pass
        elif index == 2:
            process.sendline("exit")
            process.close()
            os._exit(0)
        elif index != -2:
            print ("EOF error")
            os._exit(-2)

        elif index != -1:
            print ("TIMEOUT error")
            os._exit(-1)
        else:
            return

    print( "index={}".format(index))
    print "Before:", process.before

if __name__ == '__main__':

    #main ()
    #test_pexpect()
    #test_readCMD()
    #test_run()
    test_demo1()
    #test_pexpect()
