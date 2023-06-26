#%%
import numpy as np
import matplotlib.pyplot as plt
import h5py
from pi_stage_marcus import PI_stage
import time

import nidaqmx
from matplotlib import pyplot as plt
from tqdm import tqdm 

folder = 'C:/Users/TU-IEP-Schultze/Documents/Experiment/femto_ion_spectra/daniel_data/'
name = 'data' + str(int(np.round(time.time())))

stage = PI_stage('COM3')
poss = np.arange(38, 62, 0.05/4)
#poss = np.arange(49, 52, 0.05/4)
voltages = np.zeros(poss.size)
NumCycles = 5

for bigInd in range(NumCycles):
    stage.move_absolute_um(poss[0])
    time.sleep(1)

    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan("Dev1/ai20")

        for idx, pos in enumerate(tqdm(poss)):
            stage.move_absolute_um(pos)
            time.sleep(0.05) #0.11
            voltages[idx] = np.mean(
                task.read(number_of_samples_per_channel=1)) #5
            # print(str(round(idx*100/len(poss))) + '%')

    time_fs = poss*4*1e-6/3e8*1e15
    
    matrix = np.zeros((len(poss),2))  #np.array([time_fs , voltages,])
    matrix[:,0]=poss
    matrix[:,1]=voltages
    
    if NumCycles == 1:
        np.savetxt(folder + name + '.txt', matrix, header = 'position in um,   integrated Voltage in V')
    else:
        np.savetxt(folder + name + 'Nr' + str(bigInd) + '.txt', matrix, header = 'position in um,   integrated Voltage in V')
    #plt.plot(time_fs, voltages)
    #plt.xlabel('t / fs')

    plt.plot(poss, voltages)
plt.title(name)
plt.xlabel('position / um')

plt.ylabel('integrated voltage / V')
plt.savefig(folder + name + '.pdf')
plt.show()





# %%
