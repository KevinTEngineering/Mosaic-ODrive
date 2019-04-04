# coding: utf-8
import odrive
from odrive.enums import *
import ODrive_Ease_Lib
import time
import usb.core
import svg.path
from xml.dom import minidom
import numpy
import math

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
#        self._blake = stepper(port=1, microsteps=32, spd = 1000)
#        self._blake.set_max_speed(1000)
#        self._blake.set_speed(100)
        self.set_x_vel_limit(500000)
        self.set_y_vel_limit(500000)
        self.set_x_accel_limit(1000000)
        self.set_y_accel_limit(200000)
        self.set_x_decel_limit(1000000)
        self.set_y_accel_limit(200000)
        self.set_x_A_per_css(0)
        self.set_y_A_per_css(0)
        self.set_x_current_limit(15)
        self.set_y_current_limit(15)

        self.set_x_zero()
        self.set_y_zero()

        self.set_x_vel_no_pid(50000)
        self.set_y_vel_no_pid(100000)
        time.sleep(8)
#        self._blake.home(1)
        self.set_x_vel_no_pid(0)
        self.set_y_vel_no_pid(0)

        self.set_x_zero()
        self.set_y_zero()
#        self._blake.go_to_position(-1800)

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
        self._xavier.axis0.controller.config.vel_limit = limit
        self._xavier.axis0.trap_traj.config.vel_limit = limit

    def get_x_vel_limit(self):
        return self._xavier.axis0.controller.config.vel_limit

    def set_y_vel_limit(self, limit):
        self._yannie.axis0.controller.config.vel_limit = int(limit * 1.1)
        self._yannie.axis1.controller.config.vel_limit = int(limit * 1.1)
        self._yannie.axis0.trap_traj.config.vel_limit = limit
        self._yannie.axis1.trap_traj.config.vel_limit = limit

    def get_y_vel_limit(self):
        return self._yannie.axis0.trap_traj.config.vel_limit

    def set_x_accel_limit(self, limit):
        self._xavier.axis0.trap_traj.config.accel_limit = limit

    def get_x_accel_limit(self):
        return self._xavier.axis0.trap_traj.config.accel_limit
    
    def set_y_accel_limit(self, limit):
        self._yannie.axis0.trap_traj.config.accel_limit = limit
        self._yannie.axis1.trap_traj.config.accel_limit = limit

    def get_y_accel_limit(self):
        return self._yannie.axis0.trap_traj.config.accel_limit

    def set_x_decel_limit(self, limit):
        self._xavier.axis0.trap_traj.config.decel_limit = limit

    def get_x_decel_limit(self):
        return self._xavier.axis0.trap_traj.config.decel_limit

    def set_y_decel_limit(self, limit):
        self._yannie.axis0.trap_traj.config.decel_limit = limit
        self._yannie.axis1.trap_traj.config.decel_limit = limit
    
    def get_y_decel_limit(self):
        return self._yannie.axis0.trap_traj.config.decel_limit

    def set_x_current_limit(self, limit):
        self._xavier.axis0.motor.config.current_lim = limit
    
    def get_x_current_limit(self):
        return self._xavier.axis0.motor.config.current_lim

    def set_y_current_limit(self, limit):
        self._yannie.axis0.motor.config.current_lim = limit
        self._yannie.axis1.motor.config.current_lim = limit
    
    def get_y_current_limit(self):
        return self._yannie.axis0.motor.config.current_lim

    def set_x_A_per_css(self, A):
        self._xavier.axis0.trap_traj.config.A_per_css = A

    def get_x_A_per_css(self):
        return self._xavier.axis0.trap_traj.config.A_per_css

    def set_y_A_per_css(self, A):
        self._yannie.axis0.trap_traj.config.A_per_css = A
        self._yannie.axis1.trap_traj.config.A_per_css = A

    def get_y_A_per_css(self):
        return self._yannie.axis0.trap_traj.config.A_per_css
        
    def get_x_pos(self):
        return self._xavier_axis0.get_pos()
    
    def get_y_pos(self):
        return (self._yannie_axis0.get_pos() + self._yannie_axis1.get_pos()) / 2

    def set_x_pos_no_pid(self, pos):
        self._xavier_axis0.set_pos(pos)

    def set_y_pos_no_pid(self, pos):
        self._yannie_axis0.set_pos(pos)
        self._yannie_axis1.set_pos(pos)

    def set_x_pos_trap(self, pos):
        self._xavier_axis0.set_pos_trap(pos)

    def set_y_pos_trap(self, pos):
        self._yannie_axis0.set_pos_trap(pos)
        self._yannie_axis1.set_pos_trap(pos)

    def set_y_vel_time(self, t, vel, d_kp=125, d_ki=0.4, d_kd=100):

        start = time.time()
        
        diff = self._yannie_axis0.get_pos() - self._yannie_axis1.get_pos()
        diff_sum = diff
        last_diff = diff

        self.set_y_vel_no_pid(vel)
        curr_diff = 0
        
        while time.time() < start + t:

            curr_diff = self._yannie_axis0.get_pos() - self._yannie_axis1.get_pos()
            diff_sum += curr_diff

            self._yannie_axis0.set_vel(vel - curr_diff * d_kp - diff_sum * d_ki - (curr_diff - last_diff) * d_kd)
            self._yannie_axis1.set_vel(vel + curr_diff * d_kp + diff_sum * d_ki + (curr_diff - last_diff) * d_kd)

            last_diff = curr_diff

        self.set_y_vel_no_pid(0)
    
    def set_x_pos_vel_pid(self, pos, vel, t_kp=0.0, t_ki=0.0, t_kd=0.0):
        
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
    def set_y_pos_vel_pid(self, pos, vel, kp=0.0, ki=0.0, kd=0.0, t_kp=0.0, t_ki=0.0, t_kd=0.0):
        #kp=125, 0.4, 100
        
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

    def set_x_pos_pos_pid(self, pos, vel, t_kp=200, t_ki=0.0, t_kd=0.0, dt=0.001):
        step = numpy.sign(pos - self.get_x_pos()) * abs(vel) * dt
        targ_pos = self.get_x_pos()

        err = 0
        err_sum = 0
        last_err = 0

        curr_pos = self.get_x_pos()

        mark = time.time()
        while curr_pos < pos - abs(step) or curr_pos > pos + abs(step):

            targ_pos += step
            curr_pos = self.get_x_pos()
            err = curr_pos - targ_pos
            
            err_sum += err
            
            self._xavier_axis0.set_vel(- err * t_kp - err_sum * t_ki - (err - last_err) * t_kd)
            
            while time.time() < mark + dt:
                pass

            mark = time.time()

            last_err = err

        targ_pos = pos

        while abs(self.get_x_vel()) > 1:

            err = self.get_x_pos() - targ_pos
            
            err_sum += err

            self._xavier_axis0.set_vel(- err * t_kp - err_sum * t_ki - (err - last_err) * t_kd)

            while time.time() < mark + dt:
                pass

            mark = time.time()

            last_err = err
        
    def circle(self, times, vel, x_kp=0.0002, x_ki=0.0, x_kd=0.0, y_kp=0.0002, y_ki=0.0, y_kd=0.0, dt=0.001, d_kp=0.000125, d_ki=0.0000004, d_kd=0.0001):
        self.set_x_pos_no_pid(-25000)
        self.set_y_pos_vel_pid(-30000, 20000, kp=125, ki=0.4, kd=100)
        time.sleep(2)

        targ_x = 1 * 25000 - 50000
        targ_y = 0 * 25000 - 30000

        x_err = 0
        x_err_sum = 0
        x_last_err = 0

        y_err = 0
        y_err_sum = 0
        y_last_err = 0

        diff_err = 0
        diff_err_sum = 0
        diff_last_err = 0
        
        num_pieces = int(50000 * math.pi / (vel * dt))
        piece = vel * dt / 25000

        mark = time.time()

        for x in range(0, times):
            for x in range(0, num_pieces):
                targ_x = numpy.cos(x * piece) * 25000 - 50000
                targ_y = numpy.sin(x * piece) * 25000 - 30000

                x_err = self.get_x_pos() - targ_x
                x_err_sum += x_err

                y_err = self.get_y_pos() - targ_y
                y_err_sum += y_err
                
                diff_err = self._yannie_axis0.get_pos() - self._yannie_axis1.get_pos()
                diff_err_sum += diff_err
                
                while time.time() < mark + dt:
                    pass

                self.set_x_vel_no_pid(- x_err * vel * x_kp - x_err_sum * vel * x_ki - (x_err - x_last_err) * vel * x_kd)
                
                self._yannie_axis0.set_vel(- diff_err * vel * d_kp - diff_err_sum * vel * d_ki - (diff_err - diff_last_err) * vel * d_kd
                                           - y_err * vel * y_kp - y_err_sum * vel * y_ki - (y_err - y_last_err) * vel * y_kd)
                self._yannie_axis1.set_vel(  diff_err * vel * d_kp + diff_err_sum * vel * d_ki + (diff_err - diff_last_err) * vel *d_kd
                                           - y_err * vel * y_kp - y_err_sum * vel * y_ki - (y_err - y_last_err) * vel * y_kd)
                
                mark = time.time()

                x_last_err = x_err
                y_last_err = y_err
                diff_last_err = diff_err

        self.set_x_vel_no_pid(0)
        self.set_y_vel_no_pid(0)
                

    def circle_pos(self, times, vel, dt=0.001):
        self.set_x_pos_no_pid(-25000)
        self.set_y_pos_trap(-30000)
        time.sleep(2)

        targ_x = [1 * 25000 - 50000]
        targ_y = [0 * 25000 - 30000]

        num_pieces = int(50000 * math.pi / (vel * dt))
        piece = vel * dt / 25000

        for x in range(0, num_pieces):
            targ_x.append(numpy.cos(x * piece) * 25000 - 50000)
            targ_y.append(numpy.sin(x * piece) * 25000 - 30000)

        mark = time.time()

        for x in range(0, num_pieces):
            self.set_x_pos_no_pid(targ_x[x])
            self.set_y_pos_no_pid(targ_y[x])
            
            print(time.time() - mark)

            while time.time() < mark + dt:
                pass

            mark = time.time()


        self.set_x_vel_no_pid(0)
        self.set_y_vel_no_pid(0)

    def circle_trap(self, times, vel, dt=0.001):
        self.set_x_pos_no_pid(-25000)
        self.set_y_pos_vel_pid(-30000, 50000, kp=125, ki=0.4, kd=100)
        time.sleep(2)

        targ_x = 1 * 25000 - 50000
        targ_y = 0 * 25000 - 30000

        num_pieces = int(50000 * math.pi / (vel * dt))
        piece = vel * dt / 25000

        mark = time.time()

        for x in range(0, times):
            for x in range(0, num_pieces):
                targ_x = numpy.cos(x * piece) * 25000 - 50000
                targ_y = numpy.sin(x * piece) * 25000 - 30000

                while time.time() < mark + dt and abs(self._yannie_axis0.get_pos() - self._yannie_axis1.get_pos()) > 200:
                    pass

                self.set_x_pos_trap(targ_x)
                self.set_y_pos_trap(targ_y)
                mark = time.time()

    def calc_draw(self, file_name, save_name, scale=10, vel=10000, dt=0.005):
        doc = minidom.parse(file_name)
        path_strings = [path.getAttribute('d') for path in doc.getElementsByTagName('path')]
        paths = []

        for p in path_strings:
            paths.append(svg.path.parse_path(p))

        stp_lng = abs(vel) * dt / scale
        plans = []
        num_paths = len(paths)
        
        for i in range(0, num_paths):

            plan = []
            num_segments = len(paths[i])

            for x in range(0, num_segments):
                l = paths[i][x].length()
                num_stp = int(l / stp_lng)
                pt = []

                for y in range(0, num_stp):
                    pt.append(paths[i][x].point(stp_lng * y / l))
                    if(pt[y].real * scale > 120000 or pt[y].imag * scale > 50000):
                        print(str(pt[y].real) + " " + str(pt[y].imag))
                        return

                plan.append(pt)
                print("Segment " + str(x) + " of " + str(num_segments))

            plans.append(plan)
            print("Path " + str(i) + " of " + str(num_paths))

        numpy.save(save_name + "_plans", plans)
        numpy.save(save_name + "_paths", paths, allow_pickle=True)


    def draw_from_file(self, file_name, scale=10, vel=10000, dt=0.005):
        plans = numpy.load(file_name + "_plans.npy")
        paths = numpy.load(file_name + "_paths.npy", allow_pickle=True)

        for i in range(0, len(paths)):
            for x in range(0, len(paths[i])):
                if(isinstance(paths[i][x], svg.path.path.Move)):
                    self._blake.go_to_position(-1800)
                    self.set_x_pos_trap(-paths[i][x].start.real * scale - 20000)
                    self.set_y_pos_trap(-paths[i][x].start.imag * scale - 5000)
                    time.sleep(0.25)
                    while self.is_x_busy() or self.is_y_busy():
                        pass
                    time.sleep(0.25)
                else:
                    self._blake.go_to_position(-1600)
                    mark = time.time()
                    for stp in plans[i][x]:
                        self.set_x_pos_no_pid(-stp.real * scale - 20000)
                        self.set_y_pos_no_pid(-stp.imag * scale - 5000)
                        while time.time() < mark + dt:
                            pass
                        mark = time.time()
            self.set_x_vel_no_pid(0)
            self.set_y_vel_no_pid(0)
            self._blake.go_to_position(-1800)



    def draw_test(self, paths, vel, dt, scale=10):
        stp_lng = abs(vel) * dt / scale
        plans = []
        for i in range(0, len(paths)):
            
            plan = []

            for x in range(0, paths[i].__len__()):
                l = paths[i][x].length()
                num_stp = int(l / stp_lng)
                pt = []
                for y in range(0, num_stp):
                    pt.append(paths[i][x].point(stp_lng * y / l))
                plan.append(pt)
                print(";]")
            plans.append(plan)
            print("Path " + str(i) + " calculated")

        for i in range(0, len(paths)):

            for x in range(0, paths[i].__len__()):
                if(isinstance(paths[i][x], svg.path.path.Move)):
                    self._blake.go_to_position(-1800)
                    self.set_x_pos_trap(-paths[i][x].start.real * scale - 20000)
                    self.set_y_pos_trap(-paths[i][x].start.imag * scale - 10000)
                    time.sleep(0.25)
                    while self.is_x_busy() or self.is_y_busy():
                        pass
                    time.sleep(0.25)
                else:
                    self._blake.go_to_position(-1600)
                    mark = time.time()
                    for stp in plans[i][x]:
                        self.set_x_pos_no_pid(-stp.real * scale - 20000)
                        self.set_y_pos_no_pid(-stp.imag * scale - 10000)
                        while time.time() < mark + dt:
                            pass
                        mark = time.time()

            self.set_x_vel_no_pid(0)
            self.set_y_vel_no_pid(0)
            self._blake.go_to_position(-1800)



    def set_x_zero(self):
        self._xavier_axis0.set_zero(self._xavier_axis0.get_raw_pos())

    def set_y_zero(self):
        self._yannie_axis0.set_zero(self._yannie_axis0.get_raw_pos())
        self._yannie_axis1.set_zero(self._yannie_axis1.get_raw_pos())

    def is_x_busy(self):
        return self._xavier_axis0.is_busy()

    def is_y_busy(self):
        return self._yannie_axis0.is_busy() or self._yannie_axis1.is_busy()
