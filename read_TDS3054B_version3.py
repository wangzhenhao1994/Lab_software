import requests
import numpy as np
import matplotlib.pyplot as plt
import time
import datetime
import os
import h5py
from pi_stage import PI_stage
from calculate_k_b import Calibration_mass

calclator = Calibration_mass(mass=[1,58], pixel=[2363,8610])#def __init__(self, mass=[18.01528,31.99880], pixel=[2659,4575])


response = requests.post(
    'http://192.168.3.14/Comm.html', data={'COMMAND': 'DATA:SOURCE?'})
dataSource = response.text[634:-93]
if dataSource == 'CH1':
    print('The data source is <' + dataSource +'>.')
    pass
else:
    response = requests.post(
        'http://192.168.3.14/Comm.html', data={'COMMAND': 'DATA:SOURCE CH1'})
    dataSource = response.text[634:-93]
    print('The data source is modified to <' + dataSource +'>.')

response = requests.post(
    'http://192.168.3.14/Comm.html', data={'COMMAND': 'CURVe?'})
r = response.text
endOfHeader = r.find("NAME=\"name\""+">")+len("NAME=\"name\""+">")
endOfData = r.find("</TEXTAREA>")
data = r[endOfHeader:endOfData]  # remove the header info from the response
data = np.fromstring(data, sep=',')  # 10k points
plt.plot(data)
plt.show()
def pixel2mass(t):
    [k,b]=calclator.cal_k_b()
    return ((t-b)/k)**2
now = datetime.datetime.now()
os.makedirs(
    now.strftime('%Y-%m') + '/'
    + now.strftime('%Y-%m-%d'), exist_ok=True)
fname = now.strftime('%Y-%m') + '/' + now.strftime('%Y-%m-%d') +'/OscMass.txt'
np.savetxt(fname,[pixel2mass(np.arange(10000)),data])
plt.plot(pixel2mass(np.arange(10000)),data)
plt.show()
