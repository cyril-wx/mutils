#!/bin/bash
# -*- coding:UTF-8 -*-
# 允许输入退格
stty erase ^H

while true
do
 echo "=====CentOS7 System Tools==========="
 echo "-----------Author：Cyril------------"
 echo "-----------Alter Time：181015-------"
 echo "-----------Ver：v1.0----------------"
 echo "Functions："
 echo "--1.Search port is whoese process---"
 echo "--2.Search program all process------"
 echo "===================================="

# '-n1'只接受输入单个字符，'-p'允许读入的字符存入变量
 read -n1 -p "请选择功能前对应的数字：" input
 echo ""
 
 if [ $input == 1 ];then
	echo "Search port is whoese process---"
	read -p "Please input search port no.(Only one):" port
	pro=`netstat -lnp|grep $port`
	echo "port: $port | process(PID): $pro"
 elif [ $iput == 2 ];then
	echo "Search program all process by CMD_name..."
	read -p "Please input search program name: " pname
	echo `ps -ef | grep $pname`
 else
   echo "非法输入，请重新选择功能1/2/3/4"
 fi
 read -n1 -p "请按q键退出.按其他键继续。" input 
 if [[ "$input" == "q" ||  "$input" == "Q" ]];then
   exit 0
 fi
done


