#!/usr/bin/env python

from subprocess import Popen,PIPE
from httplib import HTTPConnection
import subprocess
import commands
import socket
import csv
import sys
import re
import time
import urllib
import collections
import optparse
import logging
import time
import StringIO
import HTMLParser
import threading
import argparse


def nano_cmd():
	nano_status, nano_cmd = commands.getstatusoutput('which nanokdp')
	if nano_status != 0:
		logger.warning('command nanokdp not foudn,try to use nanocom instead')
		nano_status, nano_cmd = commands.getstatusoutput('which nanocom')
		if nano_status != 0:
			logger.error('command nanocom didn\'t existing')
			return False
	return nano_cmd

def usb_device_list():
	usb_status, usb_strings = commands.getstatusoutput('ls -1 /dev/cu.*')
	
	if usb_status != 0:
		logger.error('no usb device found')
		return  []
	usb_list = re.findall('^\/dev\/cu\.(?:usbserial|kanzi).+', usb_strings, re.M)
	return usb_list

def connect_to_device(usb_device):
	if nano_cmd():
		cmd = '{} -d {}'.format(nano_cmd(), usb_device)
		proc = Popen(cmd, shell=True, bufsize=0, universal_newlines=True, stdin=PIPE, stdout=PIPE, stderr=sys.stderr)
		return proc

if __name__ == '__main__':

	print '\033[31m========================================================================================\033[0m'
	print '\033[31m Firstly, pls double check device which on recover/diags mode then run this python file \033[0m'	
	print '\033[31m========================================================================================\033[0m'
	Mod=None
	Regn=None
	sn=None

	usb_device_list = usb_device_list()
	for usb_device in usb_device_list:
			break
	if  len(usb_device) == 20 or len(usb_device) ==26:
		print usb_device	
	else :
		print 'usb port incorrect'
		exit(-1)
	print(sys.argv)
	#for arg in sys.argv:
		#arg_strip=arg.strip()
		#if len(arg_strip)==12:
	sn=sys.argv[1].strip()
	#	if len(arg_strip)==9:
	Mod=sys.argv[2].strip() 
	#	if len(arg_strip)==4:
	Regn=sys.argv[3].strip() 				

	#if ( Mod==None or Regn==None or len(Mod) !=9 or len(Regn) !=4):	
	#	print 'Mod&Regn len is incorrect'
	#	exit(-1)

	##write Regn/MPN		
	print '=================write mpn/regn================'
	proc = connect_to_device(usb_device)			
	proc.stdin.write('diags'+'\n')
	time.sleep(3)	
	ModifyKey='\n'+'sn '+sn+'\n'+'syscfg add Mod# '+Mod+'\n'+'syscfg add Regn '+Regn+'\n'+'res'+'\n'
	print ModifyKey	
	#output = proc.communicate(input='syscfg add Mod# 993-14163\nsyscfg add Regn LL/A'+'\n')[0]
	output = proc.communicate(input=ModifyKey)[0]
	for line in iter(output.split('\n')):
				line_strip = line.strip()
				if line_strip:
					if len(line_strip) == 7:
						print line_strip

	proc.stdout.close()
	proc.stdin.close()	
	

	proc.stdout.close()
	proc.stdin.close()	
	print '*******************(0K***OK***OK)***************\n'					
