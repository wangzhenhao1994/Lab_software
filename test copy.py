import h5py
import numpy as np
import pathlib as pl
import os
import datetime
from matplotlib import pyplot as plt
ch0=np.loadtxt(r'C:\Users\TU-IEP-Schultze\Downloads\CH0.isf',delimiter=',')
ch1=np.loadtxt(r'C:\Users\TU-IEP-Schultze\Downloads\CH1.isf',delimiter=',')
ch2=np.loadtxt(r'C:\Users\TU-IEP-Schultze\Downloads\CH2.isf',delimiter=',')
ch3=np.loadtxt(r'C:\Users\TU-IEP-Schultze\Downloads\CH3.isf',delimiter=',')
ch4=np.loadtxt(r'C:\Users\TU-IEP-Schultze\Downloads\CH4.isf',delimiter=',')
#plt.plot(ch0[:,0],ch0[:,1],label='CH0')
#plt.plot(ch1[:,0],ch0[:,1],label='CH1')
#plt.plot(ch2[:,0],ch0[:,1],label='CH2')
#plt.plot(ch3[:,0],ch0[:,1],label='CH3')
#plt.plot(ch4[:,0],ch0[:,1],label='CH4')
#plt.legend()
#plt.show()
print(np.sum(ch0[:,1]),np.sum(ch1[:,1]),np.sum(ch2[:,1]),np.sum(ch3[:,1]),np.sum(ch4[:,1]))