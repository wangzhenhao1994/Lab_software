import numpy as np
from matplotlib import pyplot as plt
import os

os.chdir(r'C:\Users\TU-IEP-Schultze\Documents\Experiment\femto_ion_spectra\2021-10\2021-10-12')
goodSpec = np.loadtxt('good.txt')
print(goodSpec.shape)
todaySpec = np.loadtxt('today_2.txt')
print(todaySpec[:,1].shape)
plt.plot(np.arange(10,2048),todaySpec[10:2048,1]*2+2500, goodSpec[10:2048])
plt.legend()
plt.show()