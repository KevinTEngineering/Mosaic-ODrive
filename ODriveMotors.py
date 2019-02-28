# coding: utf-8
import odrive
from odrive.enums import *
import ODrive_Ease_Lib
import time
import usb.core

import numpy

# for future note: two motor vert serial # 61951538836535
#                  one motor hori serial # 61985896477751

xavier_serial = 61985896477751
yannie_serial = 61951538836535
       
        
class GGMotors(object):

    def __init__(self):

        dev = usb.core.find(find_all=1, idVendor=0x1209, idProduct=0x0d32)
        od = []

        a = next(dev)
        od.append(odrive.find_any('usb:%s:%s' % (a.bus, a.address)))
        a = next(dev)
        od.append(odrive.find_any('usb:%s:%s' % (a.bus, a.address)))
        
        if od[0].serial_number == xavier_serial:
            self._xavier = od[0]
            self._yannie = od[1]
        else:
            self._xavier = od[1]
            self._yannie = od[0]
        
        self._xavier_axis0 = ODrive_Ease_Lib.ODrive_Axis(self._xavier.axis0)

        self._yannie_axis0 = ODrive_Ease_Lib.ODrive_Axis(self._yannie.axis0)
        self._yannie_axis1 = ODrive_Ease_Lib.ODrive_Axis(self._yannie.axis1)

        self._xavier.axis0.requested_state = AXIS_STATE_ENCODER_OFFSET_CALIBRATION
        self._yannie.axis0.requested_state = AXIS_STATE_ENCODER_OFFSET_CALIBRATION
        self._yannie.axis1.requested_state = AXIS_STATE_ENCODER_OFFSET_CALIBRATION

        start = time.time()

        while (self._xavier.axis0.current_state != AXIS_STATE_IDLE or
               self._yannie.axis0.current_state != AXIS_STATE_IDLE or
               self._yannie.axis1.current_state != AXIS_STATE_IDLE):
            time.sleep(0.1)
            if time.time() - start > 15:
                print("could not calibrate, try rebooting odrive")
                return
        
        self.set_x_vel_limit(500000)
        self.set_y_vel_limit(500000)

        self.set_x_vel_no_pid(50000)
        self.set_y_vel_no_pid(50000)
        time.sleep(8)
        self.set_x_vel_no_pid(0)
        self.set_y_vel_no_pid(0)

        self.set_x_zero()
        self.set_y_zero()

    def set_x_vel_no_pid(self, vel):
        self._xavier_axis0.set_vel(vel)

    def set_y_vel_no_pid(self, vel):
        self._yannie_axis0.set_vel(vel)
        self._yannie_axis1.set_vel(vel)
    
    def get_x_vel(self):
        return self._xavier_axis0.get_vel()

    def get_y_vel(self):
        return (self._yannie_axis0.get_vel() + self._yannie_axis1.get_vel()) / 2

    def set_x_vel_limit(self, limit):
        self._xavier_axis0.set_vel_limit(limit)

    def set_y_vel_limit(self, limit):
        self._yannie_axis0.set_vel_limit(limit)
        self._yannie_axis1.set_vel_limit(limit)

    def get_x_pos(self):
        return self._xavier_axis0.get_pos()
    
    def get_y_pos(self):
        return (self._yannie_axis0.get_pos() + self._yannie_axis1.get_pos()) / 2

    def set_x_pos_no_pid(self, pos):
        self._xavier_axis0.set_pos(pos)

    def set_y_pos_no_pid(self, pos):
        self._yannie_axis0.set_pos(pos)
        self._yannie_axis1.set_pos(pos)
    
    def set_x_pos(self, pos, vel, t_kp=0.0, t_ki=0.0, t_kd=0.0):
        
        targ_vel = numpy.sign(pos - self.get_x_pos()) * abs(vel)
        
        err = 0
        err_sum = 0
        last_err = 0

        self.set_x_vel_no_pid(targ_vel)
        curr_err = 0

        while self.get_x_pos() > pos + 500 or self.get_x_pos() < pos - 500:
            curr_err = self.get_x_vel() - targ_vel
            err_sum += curr_err
            
            self.set_x_vel_no_pid(targ_vel - curr_err * t_kp - err_sum * t_ki - (curr_err - last_err) * t_kd)
            
            last_err = curr_err

        self.set_x_vel_no_pid(0)
    def set_y_pos(self, pos, vel, kp=0.0, ki=0.0, kd=0.0, t_kp=0.0, t_ki=0.0, t_kd=0.0):
        
        targ_vel = numpy.sign(pos - self.get_y_pos()) * abs(vel)

        err = 0
        err_sum = 0
        last_err = 0

        diff = self._yannie_axis0.get_pos() - self._yannie_axis1.get_pos()
        diff_sum = diff
        last_diff = diff

        self.set_y_vel_no_pid(targ_vel)
        curr_err = 0
        curr_diff = 0

        while self.get_y_pos() > pos + 1000 or self.get_y_pos() < pos - 1000:
            curr_err = self.get_y_vel() - targ_vel
            err_sum += curr_err

            curr_diff = self._yannie_axis0.get_pos() - self._yannie_axis1.get_pos()
            diff_sum += curr_diff

            self._yannie_axis0.set_vel(targ_vel - curr_diff * kp - diff_sum * ki - (curr_diff - last_diff) * kd
                                                - curr_err * t_kp - err_sum * t_ki - (curr_err - last_err) * t_kd)
            self._yannie_axis1.set_vel(targ_vel + curr_diff * kp + diff_sum * ki + (curr_diff - last_diff) * kd
                                                - curr_err * t_kp - err_sum * t_ki - (curr_err - last_err) * t_kd)

            last_err = curr_err
            last_diff = curr_diff

        self.set_y_vel_no_pid(0)


    def set_x_zero(self):
        self._xavier_axis0.set_zero(self._xavier_axis0.get_raw_pos())

    def set_y_zero(self):
        self._yannie_axis0.set_zero(self._yannie_axis0.get_raw_pos())
        self._yannie_axis1.set_zero(self._yannie_axis1.get_raw_pos())
