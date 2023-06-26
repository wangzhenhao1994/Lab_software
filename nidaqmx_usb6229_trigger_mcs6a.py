from re import A
import time
from nidaqmx._task_modules.triggering.start_trigger import StartTrigger
import numpy as np
import nidaqmx
import nidaqmx._task_modules.ci_channel_collection as ntc
from nidaqmx.constants import AcquisitionType, Edge, Signal, TriggerType, CountDirection, Level, TaskMode
from matplotlib import pyplot
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
