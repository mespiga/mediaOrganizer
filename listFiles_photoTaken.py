#!/usr/bin/env python
import datetime
import time
from threading import Thread
import urllib
import urllib2
import csv
import sys						
import socket
import os
import stat
import time
import shutil
import glob
import errno
import pickle
import EXIF
						

# --------------------------------------------------
# Functions 
# --------------------------------------------------

def monthName(monthNum):
    if monthNum == "01":
	return "Janeiro"
    if monthNum == "02":
	return "Fevereiro"
    if monthNum == "03":
	return "Marco"
    if monthNum == "04":
	return "Abril"
    if monthNum == "05":
	return "Maio"
    if monthNum == "06":
	return "Junho"
    if monthNum == "07":
	return "Julho"
    if monthNum == "08":
	return "Agosto"
    if monthNum == "09":
	return "Setembro"
    if monthNum == "10":
	return "Outubro"
    if monthNum == "11":
	return "Novembro"
    if monthNum == "12":
	return "Dezembro"
    else:
	return ""

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise

def getInfo(path, fileName):
    time_format = "%Y/%m/%d %H:%M:%S"
    file_stats = os.stat(os.path.join(path,fileName))
    modification_time = time.strftime(time_format,time.localtime(file_stats[stat.ST_MTIME]))
    access_time = time.strftime(time_format,time.localtime(file_stats[stat.ST_ATIME]))
    creation_time = time.strftime(time_format,time.localtime(file_stats[stat.ST_CTIME]))
    return modification_time, access_time, creation_time

########################################################

def createName(fileInfo, pathSrc, pathDest, specialStr, count):
    if(str.isspace(specialStr)):
        fileName = str(fileInfo).replace(" ","_")
        fileName = fileName.replace("/","-")
        fileName = fileName.replace(":","-")
	#print "ole"
	pathDest = pathDest+fileName[0:4]+"/"+ monthName(fileName[5:7])	
	mkdir_p(pathDest)
        for inFile in glob.glob( os.path.join(pathDest, '*.*') ):
            if(inFile.find(fileName) != -1):
                return createName(fileInfo, pathSrc, pathDest, fileName, count)
            else:
                continue
    else:
	count = count + 1 
        fileName = specialStr + "_" + str(count)
        for inFile in glob.glob( os.path.join(pathDest, '*.*') ):
            if(inFile.find(fileName) != -1):
                return createName(fileInfo, pathSrc, pathDest, specialStr, count)
            else:
                continue
    return pathDest+"/"+fileName
            
########################################################  

def listFiles(pathOrigin, pathDest):
    i = 0
    listError = []
    for (path, dirs, files) in os.walk(pathOrigin):
        print "*** START Processing the following files in path:" + path
	print files
	#print dirs
	newFileName=""
        for fileNameOrigin in files:
	    i = i+1
            fileInfo = getInfo(path, fileNameOrigin)
            fileExtension = str.split(fileNameOrigin,".")
            index = len(fileExtension)
    
	    if ( ("JPG" in str(fileNameOrigin)) ):		
		p = open(path+"/"+fileNameOrigin,"rb")
                tags = EXIF.process_file(p)
		p.close()
		for key in tags.keys():
			if "datetimeoriginal" in str(key).lower():
				dateTaken = str(tags[key]).split(' ')
				dateTakenNew = str(dateTaken[0]).replace(':','-') # 2009-12-13
				dateTakenTimeNew = str(dateTaken[1]).replace(':','-')
				newFileName = createName((dateTakenNew+"_"+dateTakenTimeNew), path, pathDest, " ",0)
	    else:
	        newFileName = createName(fileInfo[0], path, pathDest, " ",0)
            
	    newFileName = newFileName + "." + fileExtension[index-1]
	    newFileName.replace(" ","")

	    print "Path: " + path + " -> Processing " + str(i) + " files OK"
	    fileSource = open(path+"/"+fileNameOrigin, 'r')
	    fileDest = 	open(newFileName,"w")
	   # print "Convert FROM " + path+"/"+fileNameOrigin + " TO " + 	newFileName
	    try:
		shutil.copyfileobj(fileSource, fileDest)
		shutil.copystat(path+"/"+fileNameOrigin, newFileName)
		fileSource.close()
		fileDest.close()
	    except IOError as err:
		fileSource.close()
		fileDest.close()
		listError.append(path+"/"+fileNameOrigin)
		print err	    	
		pass
    print "FOUND "+ str(len(listError)) +" ERRORS"
    print "Error List"
    print listError   
    fileError = open("Fotos_List_Errors.log","a") 
    fileError.write(time.strftime("%a, %d %b %Y %H:%M:%S ", time.gmtime()))
    pickle.dump(listError, fileError)
    fileError.close()

    return

# --------------------------------------------------
# Main program
# --------------------------------------------------

pathOrigin = "/media/Data/Pictures/"
pathDest = "/media/Data/temp/Pictures/"

print "\n"
listFiles(pathOrigin, pathDest)


print "\n"
