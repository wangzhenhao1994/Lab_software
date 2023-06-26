from re import A
import time
from nidaqmx._task_modules.triggering.start_trigger import StartTrigger
import numpy as np
import nidaqmx
import nidaqmx._task_modules.ci_channel_collection as ntc
from nidaqmx.constants import AcquisitionType, Edge, Signal, TriggerType, CountDirection, Level, TaskMode
system = nidaqmx.system.System.local()
system.driver_version

for device in system.devices:
    print(device.name)

class PLLreadout_nidaqmx(object):
    def __init__(self) -> None:
        super().__init__()

    def sleep(self, duration, get_now=time.perf_counter):
        now = get_now()
        end = now + duration
        while now < end:
            now = get_now()

    def start(self, PLLreadout_buffer):
        with nidaqmx.Task() as task, nidaqmx.Task() as task2, nidaqmx.Task() as task3:
            #PFI0 is the trigger from the Standform delayer generator
            task.stop()
            task2.stop()
            task3.stop()
            PLL_output = task.ci_channels.add_ci_count_edges_chan(counter='Dev1/ctr0',initial_count=0, edge=Edge.RISING, count_direction=CountDirection.COUNT_UP)
            PLL_output.ci_count_edges_term = "PFI1"
            arm_trigger = task.triggers.arm_start_trigger
            arm_trigger.trig_type = TriggerType.DIGITAL_EDGE
            arm_trigger.dig_edge_edge = Edge.RISING
            arm_trigger.dig_edge_src="PFI0"

            gate = task2.di_channels.add_di_chan(lines="Dev1/PFI0")

            PLL_input = task3.ai_channels.add_ai_voltage_chan(physical_channel="Dev1/ai0")
            task3.start()

            i=0
            task.start()
            task2.start()

            while task2.read(1)[0] is False:
                self.sleep(0.001)
            while task2.read(1)[0] is True:
                PLLreadout_buffer[i,1]=time.perf_counter()
                PLLreadout_buffer[i,0]=task.read(1)[0]
                PLLreadout_buffer[i,3]=time.perf_counter()
                PLLreadout_buffer[i,2]=task3.read(1)[0]
                self.sleep(0.01)
                i=i+1
            
if __name__ == '__main__':
    PLLreadout_buffer = np.zeros((1000,4),dtype=float)
    a = PLLreadout_nidaqmx()
    a.start(PLLreadout_buffer)
    for i in range(1,100):
        print(PLLreadout_buffer[i]-PLLreadout_buffer[i-1])


import nidaqmx
from nidaqmx import constants
from nidaqmx import stream_readers
from nidaqmx import stream_writers
import matplotlib.pyplot as plt

import numpy as np

#user input Acquisition
Ch00_name = 'A00'
Sens_Ch00 = 100#sensibilidade em mV/g
Ch01_name = 'A01'
Sens_Ch01 = 100#sensibilidade em mV/g
num_channels = 2
fs_acq = 1651 #sample frequency
t_med = 2 #time to acquire data


with nidaqmx.Task() as task:
    task.ai_channels.add_ai_accel_chan(physical_channel="cDAQ9191-1B7B393Mod1/ai0", name_to_assign_to_channel=Ch00_name,
                                       sensitivity=Sens_Ch00, min_val=-5, max_val=5, current_excit_val=0.002)
    task.ai_channels.add_ai_accel_chan(physical_channel="cDAQ9191-1B7B393Mod1/ai1", name_to_assign_to_channel=Ch01_name,
                                       sensitivity=Sens_Ch01, min_val=-5, max_val=5, current_excit_val=0.002)

    task.timing.cfg_samp_clk_timing(rate=fs_acq, sample_mode=constants.AcquisitionType.CONTINUOUS, 
                                    samps_per_chan=(t_med * fs_acq),) # you may not need samps_per_chan

    # I set an input_buf_size
    samples_per_buffer = int(fs_acq // 30)  # 30 hz update
    # task.in_stream.input_buf_size = samples_per_buffer * 10  # plus some extra space

    reader = stream_readers.AnalogMultiChannelReader(task.in_stream)
    writer = stream_writers.AnalogMultiChannelWriter(task.out_stream)

    def reading_task_callback(task_idx, event_type, num_samples, callback_data=None):
        """After data has been read into the NI buffer this callback is called to read in the data from the buffer.

        This callback is for working with the task callback register_every_n_samples_acquired_into_buffer_event.

        Args:
            task_idx (int): Task handle index value
            event_type (nidaqmx.constants.EveryNSamplesEventType): ACQUIRED_INTO_BUFFER
            num_samples (int): Number of samples that was read into the buffer.
            callback_data (object)[None]: No idea. Documentation says: The callback_data parameter contains the value
                you passed in the callback_data parameter of this function.
        """
        buffer = np.zeros((num_channels, num_samples), dtype=np.float32)
        reader.read_many_sample(buffer, num_samples, timeout=constants.WAIT_INFINITELY)

        # Convert the data from channel as a row order to channel as a column
        data = buffer.T.astype(np.float32)

        # Do something with the data

    task.register_every_n_samples_acquired_into_buffer_event(samples_per_buffer, reading_task_callback)
