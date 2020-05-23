#!/usr/bin/python
import datetime
from numpy import *
from kk_util import *
from ftplib import FTP
import pysftp
import sys
import logging
import os


cltr_IPADDRESS = '192.168.1.51'
cltr_incoming_dir = '/sd/data/incoming'
rpi_data_dir = 'data'
cloud_IPADDRESS = '35.189.121.145'
cloud_username = "pi"
private_key = '/home/pi/.ssh/id_rsa'
cloud_remote_dir = 'data/incoming'

def upload():
    if 'logger' not in globals():
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)  

    #
    # DOWNLOAD FILES FROM CLTLR/INCOMING TO RPI/DATA
    #
    # - CONNECTING
    ntrial = 5
    files0 = {}

    for iter in range(ntrial):
        try:
            ftp = FTP(cltr_IPADDRESS)
            ftp.login('micro','python')
            ftp.cwd(cltr_incoming_dir)
            files0_ = []
            ftp.dir(files0_.append)
            for file in files0_:
                filesize = file[25:36]
                filename = file[49:]
                files0[filename] = int(filesize)
            break
        except:
            ftp.close()
            time.sleep(5)
            logger.debug('ftp retrial #{}...'.format(iter))
    # - DOWNLOADING        
    if iter == ntrial-1:
        logger.debug('ftp connection to CTRL failed after all.')
    else:
        nfiles0 = len(files0)
        for idx, filename in enumerate(files0):
            local_filename = '{}/{}'.format(rpi_data_dir,filename)
            with open(local_filename,'wb') as fp:
                ftp.retrbinary('RETR '+filename,fp.write)
            if os.stat(local_filename).st_size == files0[filename]:
                ftp.delete(filename)
            logger.info('downloading {} ({}/{}) Done.'.format(filename, idx+1, nfiles0))
            if 0:
                if idx == 0: 
                    break
        ftp.close()

    #
    #     UPLOADING TO CLOUD
    #

    files1_=os.listdir('data')  # list of files to upload
    files1 = {}
    for file in files1_:
        files1[file] = os.stat('data/'+file).st_size
    # files1
    nfiles1 = len(files1)
    with pysftp.Connection(cloud_IPADDRESS, username=cloud_username, private_key=private_key) as sftp:
        with sftp.cd(cloud_remote_dir):
            for idx,file in enumerate(files1):
                response=sftp.put('data/'+file)
                if response.st_size == files1[file]:
                    os.remove('data/'+file)
                logger.info('uploading {} ({}/{}) Done.'.format(file, idx+1, nfiles1))

                
if __name__ == '__main__':
    upload()
