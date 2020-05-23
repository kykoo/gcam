import time
import datetime 
from ftplib import FTP
import sys
import logging
import os
from kk_util import *


def datetimerange(start_datetime, end_datetime,timedelta):
    dt = timedelta.seconds
    for i in range(int ((end_datetime - start_datetime).seconds/dt)):
        yield start_datetime + datetime.timedelta(seconds=i*dt)
        
def files_dict(IPADDRESS,ID,PW,remote_dir):
    ftp = FTP(IPADDRESS)
    ftp.login(ID,PW)
    try:
        ftp.cwd(remote_dir)
    except:
        ftp.close()
        return {}
    files_ = []
    ftp.dir(files_.append)
    ftp.close()

    files = {}
    for file in files_:
        filesize = file[25:36]
        filename = file[49:]
        files[filename] = int(filesize)
    return files


def daterange(start_date, end_date):
    for i in range(int ((end_date - start_date).days)):
        yield start_date + datetime.timedelta(days=i)
        

def datetime_string(time_sec):
    t_ = time.localtime(time_sec)
    return '{}-{:0>2d}{:0>2d}-{:0>2d}{:0>2d}{:0>2d}'.format(t_[0],t_[1],t_[2],t_[3],t_[4],t_[5])

def date_string(time_sec):
    t_ = time.localtime(time_sec)
    return '{}-{:0>2d}{:0>2d}'.format(t_[0],t_[1],t_[2])

def getNextGridTime(T_now,T_exec):
    res = T_now%T_exec
    if res != 0:
        T_start = T_now - res + T_exec
    else:
        T_start = T_now
    return T_start

def waitUntil(T_start):
    while True:
        if time.time() >= T_start:
            break
    return


