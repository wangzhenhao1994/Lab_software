from simpleFROG.piStage import Stage
from pipython import GCSDevice, pitools
import numpy as np
import time
longstage = False

if longstage:
    from smc100pp import SMC100
    stage = SMC100(1, 'COM22', silent=True)
else:
    pidevice=GCSDevice('E-709') 
    stage = Stage(pidevice)
pos = np.linspace(5450,6000,num=100)
stage.move_absolute_um(0)
#for i in pos:
 #   if i == pos[0]:
  #      time.sleep(2)
   # stage.move_absolute_um(i)
print(stage.get_position_um())
    #time.sleep(0.3)