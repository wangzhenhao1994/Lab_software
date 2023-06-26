import h5py
import numpy as np
import pathlib as pl
import os
import datetime
from matplotlib import pyplot as plt
now = datetime.datetime.now()
dataPath = pl.PureWindowsPath(
        #r'C:\Users\user\Desktop\Data_newTOF\2021-08\2021-08-16')#150-150
        r'C:\Users\TU-IEP-Schultze\Documents\Experiment\femto_ion_spectra\2022-09\2022-09-12')#170-170
        #r'C:\Users\user\Desktop\Data_newTOF\2021-06\2021-06-14')#70-70
        #r'C:\Users\user\Desktop\Data_newTOF\2021-06\2021-06-19')#70-50
        #r'C:\Users\user\Desktop\Data_newTOF\2021-06\2021-06-20')#70-40
datafile =  os.path.join(dataPath, r'spec.hdf5')#150-150
with h5py.File(datafile, 'r') as f:
    for key in f.keys():
        print(key)
    #data = np.array(f['data'])
    #print(data.shape)
    #plt.plot(data)
    #plt.show()