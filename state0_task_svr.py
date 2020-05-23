#!/usr/bin/python3

import socket_client
import datetime
import subprocess
import logging
from logging.handlers import TimedRotatingFileHandler
import time
import sys
from numpy import *
import os
import state7_upload2gcloud


os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


if 'logger' not in globals():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # CONSOLE HANDLER
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    # FILE HANDLER
    path = 'log/gcam-rpi-svr.log'
    fh = TimedRotatingFileHandler(path,when="midnight",backupCount=0)
    fh.setLevel(logging.DEBUG)
    formatter1 = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter1)
    logger.addHandler(fh)

def system_cmd(cmdString,cwd=None):
    if cwd==None:
        MyOut = subprocess.Popen(cmdString.split(' '),stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
    else:
        MyOut = subprocess.Popen(cmdString.split(' '),stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,cwd=cwd)
    MyOut.wait()
    response = MyOut.communicate()[0]
    logger.info('STDOUT:{}'.format(response))

def system_shutdown():
    requests = 'set,rpi_state,4;'
    #responses = socket_client.request(requests)
    system_cmd('/usr/bin/sudo /home/pi/wittypi/start_shutdown.sh','/home/pi/wittypi')
    
def video_rec(icam, event_timestamp):
    video_filename = 'gcam{}-{}'.format(icam,event_timestamp)
    system_cmd('/var/www/gcam/gcam/state6_video_rec.py -t 6 {}'.format(video_filename),\
               '/var/www/gcam/gcam/')
    Event(measure_time=event_timestamp).save()   
    
state_prev = 1

while True:
    requests = 'get,state;get,time;get,arms;get,icam;'
    #responses = socket_client.request(requests)
    #if responses:
    if True:
        #responses_ = responses.split(';')
        #state = int(responses_[0])
        state=2
        
        # DEFINE SINK CONDITIONS: ending up with a shutdown, 
        if state in [3,4,5,6,7,67]:
            #acc_rms = responses_[2].split(',')[0::2]
            #icam = int(responses_[3])
            #event_timestamp = max(acc_rms)
            icam = 1
            event_timestamp = '2020-0522-221300'
            logger.info('CTLR State={}.'.format(state))
            if state in [6,67]: 
                logger.info('video recording started...')
                try:
                    video_rec(icam,event_timestamp)
                except:
                    logger.exception('exception in video_rec()') 
                logger.info('video recorded.')
            if state in [7,67]:
                logger.info('files to cloud...')
                try:
                    state7_upload2gcloud.upload()
                except:
                    logger.exception('exception in uploading to gc') 
                logger.info('files to cloud done.')
            if state in [6,7,67]:
                #responses = socket_client.request('set,rpi_state,4;')
                logger.info('rpi_state=4 reported.')
            logger.info('system shutting down...'.format(state))
            # break
            system_shutdown()
        
        # # DEFINE TRANSITION RULES
        # if state_prev == 1:
        #     if state in [2,8]:
        #         logger.info('CTLR State={}.'.format(state))
        #         time_str = datetime.datetime.fromtimestamp(int(responses_[1])).strftime('%Y-%m-%d %H:%M:%S')
        #         system_cmd('/usr/bin/sudo /bin/date --set "{}"'.format(time_str))
        #         logger.info('system time updated to {}.'.format(time_str))
        #         logger.info('nginx starting...')
        #         system_cmd('/usr/bin/sudo /bin/systemctl start nginx.service')
        #         logger.info('nginx started.')
        # elif state_prev == 2:
        #     if state in [8]:
        #         pass # do nothing
        # elif state_prev == 8:
        #     if state in [2]:
        #         pass # do nothing
        # 
        # # prepare next iteration
        # state_prev = state
    time.sleep(10)
