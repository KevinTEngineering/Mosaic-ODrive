import odrive
from odrive.enums import *
import time

# Used to make using the ODrive easier Version 1.2.1
# Last update October 18, 2018 by Blake Lazarine

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
            return False
        else:
            return True

    # method to home ODrive using where the chassis is mechanically stopped
    # length is expected length of the track the ODrive takes
    # set length to -1 if you do not want the ODrive to check its homing
    # direction = 1 or -1 depending on which side of the track you want home to be at
    # use direction = 1 if you want the track to be of only positive location values
    def home(self, current, length, direction=1):
        self.set_current(current * -1 * direction)
        time.sleep(0.05)
        while self.is_busy():
            pass
        self.set_zero(self.get_pos())

        if not length == -1:
            self.set_current(current * 1 * direction)
            time.sleep(0.05)
            while self.is_busy():
                pass

            # end pos should be length
            if abs(self.get_pos() - length) > 50:
                print('ODrive could not home correctly')
                # maybe throw a more formal error here
                return False

        self.set_pos(0)
        print('ODrive homed correctly')
        return True



print('ODrive Ease Lib 1.1')
'''
odrv0 = odrive.find_any()
print(str(odrv0.vbus_voltage))

ax0 = ODrive_Axis(odrv0.axis0)

'''
