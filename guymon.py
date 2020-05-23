import struct
from numpy import *
from matplotlib.pyplot import *
from scipy import signal
import os

from ftplib import FTP
import sys
import logging
import os
from kk_util import *
import guymon



def download(filename):

    #filename = 'gcam1-acc1-acc-2020-0510-144000'
    ##           0         1         2
    
    local_filename = 'data/{}'.format(filename)
    if os.path.exists(local_filename):
        return
    ftp = FTP('192.168.1.51')
    ftp.login('micro','python')
    ftp.cwd('sd/data/incoming')
    with open(local_filename,'wb') as fp:
        ftp.retrbinary('RETR '+filename,fp.write)
        ftp.close()
    return


class guymon:
    def __init__(self):
        self.time = []
        self.acc = []
        self.Fs = 25.0
        self.dt = 1/self.Fs
        self.fullPath = []
        self.fileName = []
        self.fileTime = []
        self.npt = 0
    def load(self, fullPath):
        # READ FILE
        self.fullPath = fullPath
        path_filename = os.path.split(fullPath)
        self.fileName = path_filename[1]
        self.fileTime = time.strptime(self.fileName[15:],'%Y-%m%d-%H%M%S')

        with open(fullPath,'rb') as fp:
            data_ = fp.read()
        self.npt = int(len(data_)/(4*3))
        data = []
        for i in range(self.npt):
            data.append(struct.unpack('<fff',data_[i*12:(i+1)*12]))
        self.acc = array(data).T
        self.time = self.dt*array(range(self.npt))
        for data_ in data:
            print('{:.4f},{:.4f},{:.4f}'.format(data_[0], data_[1], data_[2]))
        return self.time, self.acc
    
    def genPlots(self,path):
        
        figure(1, figsize=(8,6))
        clf()
        plot(self.time,self.acc[0,:],'.-',label='x')
        plot(self.time,self.acc[1,:],'.-',label='y')
        plot(self.time,self.acc[2,:],'.-',label='z')
        xlabel('Time (sec)')
        ylabel('Acceleration (g)')
        title(self.fileName)
        legend()
        grid(True)
        xlim([0 ,self.npt*self.dt])

        F, Pxx = signal.welch(signal.detrend(self.acc),self.Fs,nperseg=2**5)
        figure(2,figsize=(8,6))
        clf()
        semilogy(F,Pxx[0,:],label='x')
        semilogy(F,Pxx[1,:],label='y')
        semilogy(F,Pxx[2,:],label='z')
        xlabel('Frequency (Hz)')    
        ylabel('g/sqrt(Hz)')
        xlim([0, self.Fs/2])
        title(self.fileName)
        legend() 
        grid(True)

        #figure(1).savefig(path+"th01.png".format(self.fileName), bbox_inches='tight', dpi=300)
        #figure(2).savefig(path+"psd01.png".format(self.fileName), bbox_inches='tight', dpi=300)
        figure(1).savefig(path+"th01.png".format(self.fileName),  dpi=300)
        figure(2).savefig(path+"psd01.png".format(self.fileName), dpi=300)
        

if __name__ == '__main__':
    gmo = guymon()
    fileName = 'data/gcam1-acc1-2020-0415-164300'
    gmo.load(fileName)
    gmo.genPlots('plots/')
    
