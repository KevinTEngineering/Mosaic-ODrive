import odrive
from time import sleep
odrv0 = odrive.find_any()
print(str(odrv0.vbus_voltage))

odrv0.axis0.controller.config.control_mode = 3
      
p1 = 0
p2 = 50000

odrv0.axis0.controller.config.pos_gain = 50

for i in range(5):
    odrv0.axis0.controller.pos_setpoint = p1
    while(abs(odrv0.axis0.encoder.pos_estimate - p1) > 3):
        print((odrv0.axis0.encoder.pos_estimate - p1))
    print(i, "part1")
    odrv0.axis0.controller.pos_setpoint = p2
    while(abs(odrv0.axis0.encoder.pos_estimate - p2) > 3):
        print((odrv0.axis0.encoder.pos_estimate - p2))
    
    print(i, "part2")
