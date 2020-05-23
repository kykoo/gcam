#!/usr/bin/python3
import picamera
import time
import datetime
import socket_client
import logging
from logging.handlers import TimedRotatingFileHandler
import subprocess
import sys
import argparse
from shutil import copyfile
from shutil import copy


parser = argparse.ArgumentParser()
parser.add_argument('filename', help='output filename (without mp4)')
parser.add_argument('-t',help='number of seconds to record', default=10, type=int)
args=parser.parse_args()

filename = args.filename
T_rec = args.t

#T_rec = 10

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

path = 'log/state6_video_rec.log'
fh = TimedRotatingFileHandler(path,when="midnight",backupCount=0)
fh.setLevel(logging.DEBUG)
formatter1 = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter1)
logger.addHandler(fh)
  
logger.debug('Quering CTLR...')
if 0:
    responses = socket_client.request('get,icam;')
    responses_list = responses.split(';')
    iCAM = int(responses_list[0])
else:
    iCAM = 1
    
logger.debug('Quering CTLR Done.')

#fileName = 'videos/timestamped.h264'
#fileName = 'videos/gcam{}-{}.h264'.format(iCAM,datetime.datetime.now().strftime('%Y-%m%d-%H%M%S'))
fileName = 'cpanel/static/cpanel/video/{}.h264'.format(filename)
                              
logger.debug('Recording h264 video...')    
with picamera.PiCamera() as camera:
    # camera.resolution = (1920,1080)
    camera.resolution = (1080,1920)
    camera.framerate = 24
    camera.rotation = 0
    #camera.start_preview()
    camera.annotate_background = picamera.Color('black')
    camera.annotate_text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    camera.start_recording(fileName)
    t_start = time.time()
    while time.time() - t_start < T_rec:
        camera.annotate_text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        camera.wait_recording(0.2)
    camera.stop_recording()
logger.debug('Recording h264 video Done.')    


 # Converting to mp4 and compressing
logger.debug('Converting to mp4 and compressing...')    
fileName_mp4 = fileName[:-4]+'mp4'
MyOut = subprocess.Popen(['/usr/bin/ffmpeg','-i',fileName,'-vcodec','copy',fileName_mp4], 
                       stdout=subprocess.PIPE, 
                       stderr=subprocess.STDOUT)
MyOut.wait()
fileName_mp4_ = fileName[:-5]+'_.mp4'
MyOut = subprocess.Popen(['/usr/bin/ffmpeg','-i',fileName,'-ss','2','-to','4','-vcodec','copy',fileName_mp4_], 
                       stdout=subprocess.PIPE, 
                       stderr=subprocess.STDOUT)
MyOut.wait()
stdout,stderr = MyOut.communicate()

#copyfile(fileName_mp4 ,fileName_mp4[7:])
#copyfile(fileName_mp4_,fileName_mp4_[7:])
copy(fileName_mp4  ,fileName_mp4[7:] ,follow_symlinks=True)
copy(fileName_mp4_ ,fileName_mp4_[7:],follow_symlinks=True)

logger.debug(stdout)
logger.debug(stderr)
logger.debug('Converting to mp4 and compressing Done.')   


import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders

logger.info('Sending video by email...')   

strFrom = 'shm.fsdl.mon@gmail.com'
strTo = 'dr.ki.koo@gmail.com'
#password = "veshm1234"
password = 'qgmbctvbhszgcrpn'

msgRoot = MIMEMultipart()
msgRoot['Subject'] = 'GuyMon: Event Report'
msgRoot['From'] = strFrom
msgRoot['To'] = strTo
msgRoot.preamble = 'This is a multi-part message in MIME format.'


msgText = MIMEText("""\
<p>A new video file has been recorded </p>
""", 'html')
msgRoot.attach(msgText)

part = MIMEBase('application',"octet-stream")
part.set_payload(open(fileName_mp4_ ,"rb").read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', 'attachment; filename={}'.format(fileName_mp4_ ))
msgRoot.attach(part)


import smtplib, ssl
context = ssl.create_default_context()
try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(strFrom, password)
        server.sendmail(
            strFrom, strTo, msgRoot.as_string()
        )
    logger.info('Sending video by email Done.')
except:
    logger.exception('exception in sending email')
    

