#!/bin/bash
#指定锁文件=========
lockfile=/tmp/lock.txt
#检测锁文件,避免重复启动========
function check()
{
	#==============kill -0不发送信号，判断进程是否存在，返回1/0
	if [ -e $lockfile ] && cat ${lockfile} | xargs kill -0 ;
	then
		echo "process is already running!!"
		exit
	fi
	trap "rm -f ${lockfile};exit" INT TERM EXIT
}
#======监控lockfile=
monitor_lockfile()
{
	if [ ! -e $lockfile ]
	then
		echo "Process has stoped,because lockfile has been delete"
		exit
	fi
}
#=======main方法
function work()
{
	check
	echo $$ > ${lockfile}
	while true
	do
		monitor_lockfile
		echo "working !! ===>"
		sleep 1
	done
}

work
