#! coding: utf-8
# This python script is used for NonUI reboot unit, and save all syslog info
#
#
import serial
import subprocess
import time
import re
import os
import sys


def Port():
    Temp = subprocess.os.listdir("/dev")
    SerialPort = [line for line in Temp if "cu.kanzi" in line or "cu.usb" in line]
    if len(SerialPort) == 0:
        raise Exception("No serial device found, pls check\n没有找到串口设备，请重试")
    elif len(SerialPort) != 1:
        SerialPort = raw_input("Pls choose the Correct prot:\n%s" % ())
    else:
        SerialPort = SerialPort[0]
    return SerialPort


class DownloadData():
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        #self.data = ""
        self.index = 0
        self.SN = "NA"
        self.CFG = "NA_NA_NA"
        file("%s/%s" % (os.path.dirname(sys.argv[0]), "Output/debug.log"), "w")
        self.debughandle = file("%s/%s" % (os.path.dirname(sys.argv[0]), "Output/debug.log"), "a+")
        try:
            self.Device = serial.Serial(port=self.port, baudrate=self.baudrate)
            self.Device.reset_output_buffer()
            self.Device.reset_input_buffer()
        # help(self.Device)
        except:
            raise Exception("Sorry,Serial port init faild, pls try again\n串口初始化异常，请重试")

    def printF(self, Object):
        #print Object
        self.debughandle.write("%s"%Object)

    def Index_Init(self):
        self.index = 0

    def Read(self):
        #data_cache = None
        error_count = 0
        while True:
            try:
                yield self.Device.readline(self.Device.inWaiting())
            except:
                error_count += 1
                if error_count > 3:
                    self.printF("Can't connect to device. exit.")
                    time.sleep(1)
                    return
                continue
            finally:
                self.Device.flushOutput()
                time.sleep(0.01)



    # return self.data
    def sendCmd(self, cmd):
        # debughandle = file(os.path.join(os.curdir,"debug.txt"),"a+")
        # self.data =""
        cmd = cmd + "\n"
        chunks = [cmd[i:i + 8] for i in range(0, len(cmd), 8)]
        for chunk in chunks:
            self.Device.write(chunk)
            time.sleep(0.05)
        time.sleep(0.1)
        self.Read()
        time.sleep(0.1)
        self.Device.flushOutput()

    def Login(self):

        Count = 5

        while Count:
            self.printF("********Attemping NonUI login: %s *****************" % (5 - Count))
            self.sendCmd("")

            line = next(self.Read())
            while True:
                line = next(self.Read())
                if "login:" in line:
                    self.sendCmd("root")
                if "Password:" in line:
                    self.sendCmd("alpine")
                    self.sendCmd("")
                if "iPhone:~ root#" in line:
                    print "Login successful"
                    break
            elif "iPhone:~ root#" in next(self.Read()):
                print "Alread in NonUI root mode"
                break
            Count = Count - 1
            if not bool(Count):
                raise ValueError("Can not Login NonUI mode, pls check the unit status")

    def SN_Grab(self):
        self.sendCmd("sysconfig read -k SrNm")
        # print self.data
        try:
            line = next(self.Read())
            while not re.search("Key  | Type | Data", line):
                line = next(self.Read())
                continue
            sn_line = next(self.Read())
            SN = sn_line.strip().split("|")[2].strip()
            self.SN = SN
            if len(SN) != 12:
                raise ValueError
        # print "--------------------------------->",self.SN
        except Exception, e:
            print "Wrong SN type, pls call DRI, %s" %e

    def CFG_Grab(self):
        # This function still has some issues
        self.sendCmd("sysconfig read -k CFG#")
        try:
            line = next(self.Read())
            while not re.search("CFG# | STR  |", line):
                line = next(self.Read())
                continue
            CFG = line.split("|")[2].strip().split("/")
            self.CFG = "%s_%s_%s" % (CFG[0], CFG[-2], CFG[-1])
        except Exception, e:
            CFG = "NA_NA_NA"

    def TimeLine(self):
        return time.strftime("%Y-%m-%d_%H-%M-%S")

    def UpdateLogName(self):
        UpdateName = "%s/%s" % (
        os.path.dirname(sys.argv[0]), "Output/%s_%s_%s.log" % (self.SN, self.CFG, self.TimeLine()))
        os.rename("%s/%s" % (os.path.dirname(sys.argv[0]), "Output/debug.log"), UpdateName)


if __name__ == '__main__':

    SerialPort = Port()
    Dev = DownloadData('%s/%s' % ("/dev", SerialPort), 115200)
    Dev.sendCmd("")
 #   while True:
 #       Dev.sendCmd("")
 #       time.sleep(0.5)
 #       print(next(Dev.Read()))

    Dev.Login()
    Dev.SN_Grab()
    Dev.CFG_Grab()
    print Dev.SN

    '''
    Count = 0
    while Count < 50:
        Count = Count + 1
        Dev.sendCmd("")
        Dev.Login()
        Dev.sendCmd("#reboot ********%s_reboot**********" % (Count))
        # Dev.printF("#reboot ******** %s reboot **********"%(Count))
        time.sleep(0.1)
        # Dev.sendCmd("")
        # Use cold boot instead reboot
        # Dev.sendCmd("reboot")


        
        # command to shut down the unit by putting unit into shipping mode.

        Dev.sendCmd("smcif -r CHI1")
        Dev.sendCmd("smcif -w CHI1 0")
        Dev.sendCmd("smcif -r CHI1")
        Dev.sendCmd("smcif -smbWritePEC 2 0x16 0xC5 2 0x0E 0x55")

        # time.sleep(0.1)
        Start = time.time()
        while True:
            Dev.Read()

            """
            if "tx_flush:" in Dev.data:
                Dev.sendCmd("")
                Dev.Read()
                if "login:" in Dev.data:
                    break
            """

            ## Modified by Cyril - 07/23D BEGIN
            if re.search("tx_flush:", Dev.data):
                Dev.sendCmd("")
                Dev.Read()
                if re.search("login:", Dev.data):
                    break
            ## Modified by Cyril - 07/23D	END

            if time.time() - Start > 45:
                break
    Dev.UpdateLogName()
    '''