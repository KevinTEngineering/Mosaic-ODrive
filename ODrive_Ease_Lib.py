import odrive
from odrive.enums import *
import time

# Used to make using the ODrive easier Version 1.0
# Last update August 18, 2018 by Blake Lazarine

class ODrive_Axis(object):

    def __init__(self, axis):
        self.axis = axis
        self.zero = 0;
        self.axis.controller.config.vel_limit = 20000

    def calibrate(self):
        self.axis.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
        while(self.axis.current_state != AXIS_STATE_IDLE):
            time.sleep(0.1)
    
    def set_vel(self, vel):
        self.axis.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
        self.axis.controller.config.control_mode = CTRL_MODE_VELOCITY_CONTROL
        self.axis.controller.vel_setpoint = vel

    def set_vel_limit(self, vel):
        self.axis.controller.config.vel_limit = vel

    def get_vel_limit(self):
        return self.axis.controller.config.vel_limit

    def set_zero(self, pos):
        self.zero = pos
    
    def get_pos(self):
        return self.axis.encoder.pos_estimate - self.zero

    def get_raw_pos(self):
        return self.axis.encoder.pos_estimate

    def set_pos(self, pos):
        desired_pos = pos + self.zero
        self.axis.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
        self.axis.controller.config.control_mode = CTRL_MODE_POSITION_CONTROL
        self.axis.controller.pos_setpoint = desired_pos

    def set_curr_limit(self, val):
        self.axis.motor.config.current_lim = val

    def get_curr_limit(self):
        return self.axis.motor.config.current_lim
    
    def set_current(self, curr):
        self.axis.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
        self.axis.controller.config.control_mode = CTRL_MODE_CURRENT_CONTROL
        self.axis.controller.current_setpoint = curr

    def get_vel(self):
        return self.axis.encoder.pll_vel

    def set_pos_gain(self, val):
        self.axis.controller.config.pos_gain = val

    def get_pos_gain(self):
        return self.axis.controller.config.pos_gain

    def set_vel_gain(self, val):
        self.axis.controller.config.vel_gain = val

    def get_vel_gain(self):
        return self.axis.controller.config.vel_gain

    def set_vel_integrator_gain(self, val):
        self.axis.controller.config.vel_integrator_gain = val

    def get_vel_integrator_gain(self):
        return self.axis.controller.config.vel_integrator_gain

    def is_busy(self):
        if(self.get_vel()) > 0:
            return false
        else
            return true

odrv0 = odrive.find_any()
print(str(odrv0.vbus_voltage))

ax1 = ODrive_Axis(odrv0.axis1)
ax1.calibrate()

#ax0 = ODrive_Axis(odrv0.axis0)
#ax0.calibrate()

ax1.set_zero(ax1.get_pos())
print(str(ax1.get_pos()))
ax1.set_pos(50000)
while(ax1.is_busy()):
    continue
print(str(ax1.get_pos()))

print("done")
