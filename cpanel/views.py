from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import subprocess

import time
import logging
import socket_client
import datetime

from cpanel.models import Acc1, Acc2, Acc3, Event, SystemState

import guymon
import os

from django.shortcuts import redirect
import subprocess
import sys


logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
 


def stop_streaming():
    # start the server                                                                                                                          
    MyOut = subprocess.Popen(['/usr/bin/sudo','systemctl','stop','64_video_streaming.service'],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    stdout,stderr = MyOut.communicate()
    return



def index(request):
    global latest_video_file

    stop_streaming()
    
    # return HttpResponse("Hello, world. You're at the polls index.")
    requests = 'get,icam;get,time;get,switch;get,state;get,astate;get,afile;get,arms;get,threshold;get,mem;get,disk;get,volt;get,pwrLED;'
    #           0        1        2          3         4          5         6        7             8       9        10       11
    logger.debug('socket_client.request  {}...'.format(requests))
    responses = socket_client.request(requests)
    if responses:
        response_list = responses.split(';')
        icam = int(response_list[0])
        time = datetime.datetime.fromtimestamp(int(response_list[1])).strftime('%Y-%m-%d %H:%M:%S')
        switch = int(response_list[2])
        state = int(response_list[3])
        acc_state = [int(i) for i in response_list[4].split(',')]
        acc_file  = response_list[5].split(',')
        acc_rms = response_list[6].split(',')
        acc_threshold = [float(thr) for thr in response_list[7].split(',')]
        mem = response_list[8].split(',')
        volt = response_list[10]
        disk = response_list[9].split(',')
        pwrLED = 'checked' if 'on'in response_list[11] else 'unchecked'


    else:
        icam = 0
        time = 'unknown'
        switch = 'unknown'
        state = 'unknown'
        acc_state = [None,None,None]
        acc_file = [None,None,None]
        acc_rms = ['',None,'',None,'',None]
        acc_threshold = [None,None,None]
        mem = [None,None]
        volt = 0
        disk = [None,None]
        pwrLED = 'unchecked'
        latest_accFiles = ['','','']

    if icam:
    # Database interaction: RMS
        logger.debug('*********************')
        logger.debug('acc_rms[0]={}'.format(acc_rms[0]))

        if acc_rms[0]:
            acc1_last = Acc1.objects.last()
            logger.debug('acc1_last={}'.format(acc1_last))
            if not acc1_last:
                logger.debug('acc1_last None')
                Acc1(measure_time = acc_rms[0],rmsACC=float(acc_rms[1])).save()
            elif acc_rms[0] > acc1_last.measure_time:
                logger.debug('acc_rms[0]>acc1_last.measure_time:{}>{}'.format(acc_rms[0],acc1_last.measure_time))
                Acc1(measure_time = acc_rms[0],rmsACC=float(acc_rms[1])).save()
        if acc_rms[2]:
            acc2_last = Acc2.objects.last()
            if not acc2_last:
                Acc2(measure_time = acc_rms[2],rmsACC=float(acc_rms[3])).save()
            elif acc_rms[2] > acc2_last.measure_time:
                Acc2(measure_time = acc_rms[2],rmsACC=float(acc_rms[3])).save()
        if acc_rms[4]:
            acc3_last = Acc3.objects.last()
            if not acc3_last:
                Acc3(measure_time = acc_rms[4],rmsACC=float(acc_rms[5])).save()
            elif acc_rms[4] > acc3_last.measure_time:
                Acc3(measure_time = acc_rms[4],rmsACC=float(acc_rms[5])).save()

        logger.debug('*************************')
        logger.debug('* acc_rms = [{}, {}]'.format(acc_rms[0], acc_rms[1]))    
        logger.debug('*************************')        

        # Database interaction: File
        for inode in range(3):
            if acc_file[inode]:
                if inode ==0:
                    logger.debug('acc_file[inode]={}'.format(acc_file[inode]))
                    acci = Acc1.objects.filter(measure_time=acc_file[inode])
                elif inode==1:
                    acci = Acc2.objects.filter(measure_time=acc_file[inode])
                elif inode==2:
                    acci = Acc3.objects.filter(measure_time=acc_file[inode])
                if len(acci):
                    acci_ = acci[0]
                    if not acci_.fileUploaded:
                        acci_.fileUploaded = True
                        acci_.save()
        logger.debug('*************************')
        logger.debug('* acc_file = [{}, {},{}]'.format(acc_file[0], acc_file[1], acc_file[2]))    
        logger.debug('*************************')        

        latest_accFiles = [ Acc1.objects.filter(fileUploaded=True).last().measure_time,
                            Acc2.objects.filter(fileUploaded=True).last().measure_time,
                            Acc3.objects.filter(fileUploaded=True).last().measure_time]
        logger.debug('*************************')
        logger.debug('* acc_file = [{}, {},{}]'.format(acc_file[0], acc_file[1], acc_file[2]))    
        logger.debug('*************************')        
        logger.debug('pwrLED={}'.format(pwrLED))


        # SystemStates
        sysState = SystemState.objects.last()
        if not sysState: # initialise
            SystemState(icam=icam).save()
        else: # update if different
            if icam != sysState.icam:
                sysState.icam = icam
                sysState.save()

    latest_event = Event.objects.last()
    if not latest_event:
        latest_videoFile = 'None'
    else:
        latest_videoFile = 'gcam{}-{}.mp4'.format(icam,latest_event.measure_time)

    for i in range(3):
        if acc_rms[2*i]:
            already_captured=Event.objects.filter(measure_time=acc_rms[2*i])
            if float(acc_rms[2*i+1]) > acc_threshold[i] and not already_captured:
                return redirect('/video_record?timestamp={}'.format(acc_rms[2*i]))

    contexts = {'icam':icam, 'time':time, 'switch':switch, 'state':state, \
                'acc_state':acc_state,'acc_file':acc_file, \
                'acc_rms':acc_rms, 'acc_threshold': acc_threshold, \
                'mem':mem, 'disk':disk, 'volt':volt, 'pwrLED':pwrLED, \
    		'latest_accFiles':latest_accFiles, 'latest_videoFile':latest_videoFile}

    logger.debug('socket_client.request done...')
         
    return render(request,'cpanel/index.html',contexts)


def video_play(request):

    try:
        filename = request.GET['filename']
        latest_videoFile = 'cpanel/video/{}'.format(filename)
    except:
        try:
            timestamp = request.GET['timestamp']
        except:
            timestamp = Event.objects.last().measure_time
        icam = SystemState.objects.last().icam
        latest_videoFile = 'cpanel/video/gcam{}-{}.mp4'.format(icam,timestamp)
        
    contexts = {'latest_videoFile':latest_videoFile}
    
    return render(request,'cpanel/video_play.html',contexts)

def gcam_view(request):

    # start the server
    MyOut = subprocess.Popen(['/usr/bin/sudo','systemctl','start','64_video_streaming.service'], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.STDOUT)
    stdout,stderr = MyOut.communicate()

    # move to the streaming server address
    contexts={}
    return render(request,'cpanel/gcam_view.html',contexts)
    

def setup(request):

    requests = 'get,threshold;'
    logger.debug('socket_client.request  {}...'.format(requests))
    responses = socket_client.request(requests)
    if responses:
        response_list = responses.split(';')
        threshold_1 = response_list[0].split(',')[0]
        threshold_2 = response_list[0].split(',')[1]
        threshold_3 = response_list[0].split(',')[2]
    else:
        threshold_1 = 'unknown'
        threshold_2 = 'unknown'
        threshold_3 = 'unknown' 
    
    contexts = {'acc_threshold': [threshold_1, threshold_2, threshold_3]}
    return render(request,'cpanel/setup.html',contexts)

def setup_update(request):

    thres = [request.POST['acc_threshold_1'],
             request.POST['acc_threshold_2'],
             request.POST['acc_threshold_3']]
    requests = 'set,threshold,{},{},{}'.format(thres[0],thres[1],thres[2])
    logger.debug('socket_client.request  {}...'.format(requests))
    responses = socket_client.request(requests)
        
    contexts = {'acc_threshold':thres}
    return render(request,'cpanel/setup_update.html',contexts)

def LED_control(request):

    try:
        if request.POST['pwrLED'] in 'on':
            pwrLED = True
    except:
        pwrLED = False
        
    if pwrLED:
        contexts = {'pwrLED':'on'}
        requests = 'set,pwrLED,on;'
    else:
        contexts = {'pwrLED':'off'}
        requests = 'set,pwrLED,off;'
        
    logger.debug('pwrLED={}'.format(pwrLED))
        
    logger.debug('socket_client.request  {}...'.format(requests))
    responses = socket_client.request(requests)
    
    return render(request,'cpanel/LED_control.html',contexts)


def acc_plot(request):

    
    filename = 'gcam{}-acc{}-acc-{}'.format(request.GET['icam'],request.GET['iacc'],request.GET['timestamp'])
    go = guymon.guymon()
    guymon.download(filename)
    go.load('data/'+filename)
    go.genPlots('cpanel/static/cpanel/img/')
    go.genPlots('static/cpanel/img/')
    
    contexts = {'filename':filename}
    
    return render(request,'cpanel/acc_plot.html',contexts)

def video_record(request):

    try:
        timestamp = request.GET['timestamp']
    except:
        timestamp = datetime.datetime.now().strftime('%Y-%m%d-%H%M%S')
    Event(measure_time=timestamp).save()
    icam = SystemState.objects.last().icam
    video_filename = 'gcam{}-{}'.format(icam,timestamp)
        
    MyOut = subprocess.Popen(['/var/www/gcam/gcam/state6_video_rec.py',video_filename,'-t','20'],\
                             stdout=subprocess.PIPE,stderr=subprocess.STDOUT,\
                             cwd='/var/www/gcam/gcam')

    #return HttpResponse('hello world')
    return render(request,'cpanel/video_record.html')

