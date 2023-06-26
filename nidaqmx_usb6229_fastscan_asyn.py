import time
import numpy as np
import nidaqmx
from nidaqmx import constants
from nidaqmx import stream_readers
from matplotlib import pyplot as plt
from threading import Thread, Event
from functools import partial
import inspect
from tqdm import tqdm
system = nidaqmx.system.System.local()
system.driver_version

for device in system.devices:
    print(device.name)
    print(device.ai_simultaneous_sampling_supported)
    print(device.ai_samp_modes)

class PLLreadout_nidaqmx(Thread):
    def __init__(self, scanTime, sampRate=300, bufferSize=1000, triggerSrc='') -> None:
        super().__init__()
        self.Ch00_name = 'A00'
        self.scanTime = scanTime
        print('The sweep time is '+str(self.scanTime)+' !\n')
        self.sampRate= sampRate
        self.bufferSize = bufferSize
        self.dataSize = int(self.scanTime*self.sampRate)
        self.triggerSrc = triggerSrc
        
        self.container = np.zeros((11, self.dataSize))


        # container for the init function output
        self.init_output = None
        # container for the finish function output
        self.finish_output = None
        # stop event to stop measurement prematurely
        self.stop_event = Event()

    def stop(self):
        """stops the measurement before executing the next step and if
        supported by the sequence functions also the currently running step"""
        self.stop_event.set()

    def run(self):
        """performs the measurement. do not call directly, use start()"""
        while 1:
            self.read()

    def sleep(self, duration, get_now=time.perf_counter):
        now = get_now()
        end = now + duration
        while now < end:
            now = get_now()

    def read(self):
        with nidaqmx.Task() as task, nidaqmx.Task() as task2, nidaqmx.Task() as task3:
            task.ai_channels.add_ai_voltage_chan(physical_channel="/Dev1/ai0:7", min_val=-10, max_val=10)
            task.ai_channels.add_ai_voltage_chan(physical_channel="/Dev1/ai16:18", min_val=-10, max_val=10)
            if self.triggerSrc == '':
                print('Using start trigger from SRS delay generator')
                task.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source="/Dev1/PFI0", trigger_edge=constants.Edge.RISING)#step by step measurement doesn't need the trigger
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
            print('Start Scan!')
            reader.read_many_sample(self.container, self.dataSize, timeout=constants.WAIT_INFINITELY) 
            print('Stop Scan!')
            task.wait_until_done(self.scanTime)
            time.sleep(5)
            
if __name__ == '__main__':
    a = PLLreadout_nidaqmx(scanTime=10)
    
    a.start()
    delay = np.array(a.container).flatten()
    print(delay)


    plt.plot(delay)
    plt.show()


