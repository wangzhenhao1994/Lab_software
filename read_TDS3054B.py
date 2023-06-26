import requests
import numpy as np
import matplotlib.pyplot as plt
import time
import datetime
import os
import h5py
from pi_stage import PI_stage

response = requests.post(
    'http://129.27.156.205/Comm.html', data={'COMMAND': 'DATA:SOURCE?'})
dataSource = response.text[634:-93]
if dataSource == 'CH1':
    print('The data source is <' + dataSource +'>.')
    pass
else:
    response = requests.post(
        'http://129.27.156.205/Comm.html', data={'COMMAND': 'DATA:SOURCE CH1'})
    print('The data source is modified to <' + dataSource +'>.')

sweepTime = 100 #seconds
numCycle = 1 # number of cycle after initiation of the wave generator
numSweeps = 30 # number of sweeps
stage = PI_stage('COM23')
stage.setSweepTime(100)
stage.setCycleNum(numCycle)#number of the cycle after initiate the wave generator

now = datetime.datetime.now()
os.makedirs(
    now.strftime('%Y-%m') + '/'
    + now.strftime('%Y-%m-%d'), exist_ok=True)
fname = (now.strftime('%Y-%m') + '/'
         + now.strftime('%Y-%m-%d')
         + '/scan_osc_'
         + now.strftime('%Y-%m-%d-%H-%M-%S'))
with h5py.File(fname + '.hdf5', 'w') as f:
    for i in range(numSweeps):
        stage.move_absolute_um(0)
        time.sleep(0.5)
        stage.initWaveGen()
        print('This is the No.' + str(i) + ' sweep.')
        time.sleep(sweepTime+1)
        stage.stopWaveGen()
        response = requests.post(
            'http://129.27.156.205/Comm.html', data={'COMMAND': 'CURVe?'})
        r = response.text
        endOfHeader = r.find("NAME=\"name\""+">")+len("NAME=\"name\""+">")
        endOfData = r.find("</TEXTAREA>")
        data = r[endOfHeader:endOfData]  # remove the header info from the response
        data = np.fromstring(data, sep=',')  # 10k points
        #print(data.shape)

        #plt.plot(data)
        #plt.show(block=False)

        try:
            # save data hdf5

            f.create_dataset('scan'+str(i), data=data)
            f.flush()
        except Exception as e:
            print('save error')
            print(e)

