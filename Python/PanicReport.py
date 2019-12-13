#!/usr/bin/python
# -*- coding: UTF-8 -*-

import zipfile
import os
import sys
import csv
import shutil

########
#Usage:
#    sys.argv[1] zipPath
#    sys.argv[2] csvPath and sys.argv[3-5] will radar/umbrellaRadar/OSDVersion
#    if sys.argv[2] is not *.csv, csvPath will default "~/Desktop/PanicReport.csv" and  sys.argv[2-4] radar/umbrellaRadar/OSDVersion
########

location = "FXGL"
try:
    zipPath = sys.argv[1]
except IndexError:
    print "sys.argv[1] zipPath is null, please confirm"
    exit(1)
if os.path.splitext(zipPath)[1] != ".zip":
    print "argv[1] is not zip file,error!!!!"
    exit(1)

csvFlag=1
homePath = os.path.expanduser('~')
csvPath = homePath + "/Desktop/PanicReport.csv"
try:
    csvPath = sys.argv[2]
except IndexError:
    csvFlag=0
    print "sys.argv[2] csvPath is null, csvPath will defaults",csvPath

radar = "/"
umrellaRadar = "/"
OSDVersion = "/"
if csvFlag==0:
    try:
        radar = sys.argv[2]
        umrellaRadar = sys.argv[3]
        OSDVersion = sys.argv[4]
    except IndexError:
        print "radar/umbrellaRadar/OSDVersion if not set, will defaults /"
else:
    try:
        radar = sys.argv[3]
        umrellaRadar = sys.argv[4]
        OSDVersion = sys.argv[5]
    except IndexError:
        print "radar/umbrellaRadar/OSDVersion if not set, will defaults /"

if os.path.splitext(zipPath)[1]  == ".zip":
    print "run zip",zipPath
    file_zip = zipfile.ZipFile(zipPath, 'r')
    zip_pathdir = os.path.splitext(zipPath)[0]
    zip_pathparent = os.path.split(zip_pathdir)[0]
    zip_filepath = os.path.split(zip_pathdir)[0] +"/__MACOSX"
    file_zip.extractall(zip_pathparent)
    flag=0
    for file in file_zip.namelist():
        if file.rfind("MACOSX") != -1:
            if os.path.exists(zip_filepath):
                shutil.rmtree(zip_filepath)
        else:
            if file.rfind("radar.txt") != -1:
                flag=1
                flag_path = file
                print "txtPath is",flag_path
    txt =  zip_pathparent+"/"+flag_path
    print "radar txt path is",txt
    with open(txt) as f:
        NO=1
        validation=station=cfg=unitN=sn=sw=panicInfo=Date=" "
        datalist = f.readlines()
        for data in datalist:
            if data.find("Serial: ")!=-1:
                sn = data.split("Serial: ",1)[1].split("\n")[0].split("_",1)[0]
                try:
                    unitN = data.split("Serial: ",1)[1].split("_",1)[1].split("\n")[0]
                except IndexError:
                    print("\033[1;31;47mWarning: Serial: is incompletion,please confirm\033[0m")
                continue
            if data.find("SW Bundle: ")!=-1:
                print data
                sw = data.split("SW Bundle: ",1)[1].split("\n")[0]
                continue
            if data.find("Config: ")!=-1:
                cfg = data.split("Config: ",1)[1].split("\n")[0]
                continue
            if data.find("Test: ")!=-1:
                station = data.split("Test: ",1)[1].split("\n")[0]
                continue
            if data.find("Failure: ")!=-1:
                panicInfo = data.split("Failure: ",1)[1].split("\n")[0]
                continue
            if data.find("Build Phase: ")!=-1:
                try:
                    validation = data.split("Build Phase: ",1)[1].split("_")[2].split("\n")[0].capitalize()
                except IndexError:
                    print("\033[1;31;47mWarning: Build Phase: is incompletion,please confirm\033[0m")
                if validation.find("line")==-1:
                    validation =" "
                continue
            
            if data.find("Folder: ")!=-1:
                date = data.split("Folder: ",1)[1].split("Kanzi",1)[1].split("_")[1][0:8]
                Date = date[0:2] + date[3:5]
                if date[6:8] >= "13" or date[6:8] <= "08":
                    Date = Date + "N"
                else :
                    Date = Date + "D"
                continue
            if os.path.exists(csvPath):
                csv_reader = csv.reader(open(csvPath))
                if len(list(csv_reader)) < 1:
                    csvFlag=0
                else:
                    csvFlag=1
                    NO = len(list(csv.reader(open(csvPath))))
        print [NO, location, validation, station, cfg, unitN, sn,sw,OSDVersion, panicInfo, umrellaRadar, radar, Date]
        shutil.rmtree( zip_pathdir)
        print " "
        csv_head = ["NO", "Location", "Validation", "Station", "Config", "UINT#", "SrNm","Bundle","OSD Version", "Panic info", "Umbrella Radar", "Radar","Statu/Action", "Comment/Solution", "Date"]
        csv_data = [NO, location, validation, station, cfg, unitN, sn,sw,OSDVersion, panicInfo, umrellaRadar, radar," ", " ", Date]
        if csvFlag==0:
            csvFile = open(csvPath, "w")
            csv_write = csv.writer(csvFile)
            csv_write.writerow(csv_head)
            csv_write.writerow(csv_data)
        else:
            csvFile = open(csvPath, "a+")
            csv_write = csv.writer(csvFile)
            csv_write.writerow(csv_data)
            csvFile.close()
print "csvPath"+csvPath

