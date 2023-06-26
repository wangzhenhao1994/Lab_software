import time
import numpy as np
import nidaqmx
from nidaqmx import constants
from nidaqmx import stream_readers
from matplotlib import pyplot as plt
system = nidaqmx.system.System.local()
system.driver_version

for device in system.devices:
    print(device.name)
    print(device.ai_simultaneous_sampling_supported)
    print(device.ai_samp_modes)

class PLLreadout_nidaqmx(object):
    def __init__(self, scanTime, sampRate=300, bufferSize=1000, triggerSrc='', delayer=None) -> None:
        super().__init__()
        self.Ch00_name = 'A00'
        self.scanTime = scanTime
        self.sampRate= sampRate
        self.bufferSize = bufferSize
        print('scan time is'+str(self.scanTime))
        self.dataSize = int(self.scanTime*self.sampRate)
        self.triggerSrc = triggerSrc
        self.delayer=delayer

    def sleep(self, duration, get_now=time.perf_counter):
        now = get_now()
        end = now + duration
        while now < end:
            now = get_now()

    def read(self):
        
        with nidaqmx.Task() as task, nidaqmx.Task() as task2, nidaqmx.Task() as task3:
            task.ai_channels.add_ai_voltage_chan(physical_channel="/Dev1/ai0:7", min_val=-10, max_val=10)
            task.ai_channels.add_ai_voltage_chan(physical_channel="/Dev1/ai16:18", min_val=-10, max_val=10)
            #if self.triggerSrc == '':
            #    print('Using start trigger from SRS delay generator')
            #    task.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source="/Dev1/PFI0", trigger_edge=constants.Edge.RISING)#step by step measurement doesn't need the trigger
            #startTrigger
            #task2.di_channels.add_di_chan(lines="Dev1/PFI0")#PFI0 is the trigger from the Standform delayer generator
            #task.ci_channels.add_ci_count_edges_chan(counter="Dev1/ctr0")
            #task.timing.cfg_samp_clk_timing(rate=self.sampRate, source=self.triggerSrc,sample_mode=constants.AcquisitionType.FINITE, samps_per_chan=self.dataSize)
            task.timing.cfg_samp_clk_timing(rate=self.sampRate,sample_mode=constants.AcquisitionType.FINITE, samps_per_chan=self.dataSize)
            #trigger source is empty for fast scan for using internal clock. Use laser trigger as source for step-by-step measurement.
            
            # input_buf_size
            task.in_stream.input_buf_size = self.sampRate * 5  # plus some extra space      
            reader = stream_readers.AnalogMultiChannelReader(task.in_stream)     
               

 
            task.start()
            
            data = np.zeros((11, self.dataSize))
            
            reader.read_many_sample(data, self.dataSize, timeout=constants.WAIT_INFINITELY) 
            print('Ahhhahahhahaha')
            task.wait_until_done(self.scanTime)

            if self.triggerSrc == '':
                return data
            else:
                return np.sum(data,axis=1)/self.sampRate
            
if __name__ == '__main__':
    a = PLLreadout_nidaqmx(scanTime=0.5)
    
    delay =a.read()
    delay = np.array(delay).flatten()
    print(delay)


    plt.plot(delay)
    plt.show()


