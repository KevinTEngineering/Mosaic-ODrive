import time

import odrive
import usb.core
from odrive.enums import *


def find_odrive():
    print("ODrive Version: ", odrive.version.get_version_str())
    od = odrive.find_any()

    od.clear_errors()
    assert od.error == 0, "Odrive has errors present, please diagnose using odrivetool"

    return od


def find_odrives():
    dev = usb.core.find(find_all=1, idVendor=0x1209, idProduct=0x0d32)
    ods = []
    try:
        while True:
            a = next(dev)
            ods.append(odrive.find_any('usb:%s:%s' % (a.bus, a.address)))
            print('added')
    except:
        pass
    return ods


def dump_errors(od):
    odrive.utils.dump_errors(od)


# Reboots a singular odrive. You will need to reconnect to it in your code after rebooting
def reboot_odrive(od):
    try:
        od.reboot()
    except:
        print('rebooted')


class ODrive_Axis(object):

    def __init__(self, axis, vel_lim=10, current_lim=10):
        self.axis = axis
        self.home = axis.encoder.pos_estimate
        self.axis.controller.config.vel_limit = vel_lim   # defaults at 100 turns/s
        self.axis.motor.config.current_lim = current_lim  # defaults to 10 Amps

    # sets the current allowed during the calibration sequence
    # Higher currents are needed when the motor encounters more resistence to motion
    def set_calibration_current(self, curr):
        self.axis.motor.config.calibration_current = curr

    # returns the allowed calibraiton current. By default it is 5 amps (3 phase not DC)
    def get_calibration_current(self):
        return self.axis.motor.config.calibration_current

    # enters full calibration sequence (calibrates motor and encoder)
    def calibrate(self, state=AXIS_STATE_FULL_CALIBRATION_SEQUENCE):
        self.axis.requested_state = state
        start = time.time()
        while self.axis.current_state != AXIS_STATE_IDLE:
            time.sleep(0.1)
            if time.time() - start > 15:
                print("could not calibrate, try rebooting odrive")
                return False
        return True

    # enters encoder offset calibration
    def calibrate_encoder(self):
        return self.calibrate(AXIS_STATE_ENCODER_OFFSET_CALIBRATION)

    def is_calibrated(self):
        return self.axis.motor.is_calibrated and self.axis.encoder.is_ready

    def set_current_limit(self, val):
        self.axis.motor.config.current_lim = val

    def get_curr_limit(self):
        return self.axis.motor.config.current_lim

    # sets the motor's velocity limit. Default starts slow at 100
    def set_vel_limit(self, vel):
        self.axis.controller.config.vel_limit = vel

    # sets the motor to a specified velocity. Does not go over the velocity limit
    def set_vel(self, vel):
        self.axis.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
        self.axis.controller.config.control_mode = CONTROL_MODE_VELOCITY_CONTROL

        self.axis.controller.input_vel = vel

    # returns the velocity measured from the encoder
    def get_vel(self):
        return self.axis.encoder.vel_estimate

    # returns the velocity limit
    def get_vel_limit(self):
        return self.axis.controller.config.vel_limit

    # sets the home to the current_position
    def set_home(self):
        self.home = self.get_raw_pos()

    # sets the home pos to a specified position
    def set_home_to(self, pos):
        self.home = pos

    def get_home(self):
        return self.home

    # sets the desired position relative to the encoder
    def set_raw_pos(self, pos):
        self.axis.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
        self.axis.controller.config.control_mode = CONTROL_MODE_POSITION_CONTROL

        self.axis.controller.input_pos = pos

    # returns the current position directly from the encoder
    def get_raw_pos(self):
        return self.axis.encoder.pos_estimate

    # sets the desired position relative to the home position
    def set_pos(self, pos):
        self.set_raw_pos(pos + self.home)

    # returns the current position relative to the home
    def get_pos(self):
        return self.axis.encoder.pos_estimate - self.home

    # sets the desired position relative to the current position
    def set_relative_pos(self, pos):
        self.set_raw_pos(pos + self.get_pos())
    
    # TODO: Implement Trajectory Control
    # sets position using the trajectory control mode
    #def set_pos_trap(self, pos):
    #    desired_pos = pos + self.home
    #    self.axis.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
    #    self.axis.controller.config.control_mode = CTRL_MODE_TRAJECTORY_CONTROL
    #    self.axis.controller.move_to_pos(desired_pos)

    # sets the current sent to the motor
    def set_current(self, curr):  # this is now torque control
        self.axis.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
        self.axis.controller.config.control_mode = CONTROL_MODE_TORQUE_CONTROL

        self.axis.controller.input_torque = curr

    def set_torque(self, torque):
        self.set_current(torque)

    # Sets the position gain value
    def set_pos_gain(self, val):
        self.axis.controller.config.pos_gain = val

    # returns the position gain value
    def get_pos_gain(self):
        return self.axis.controller.config.pos_gain

    # sets the velocity proportional gain value
    def set_vel_gain(self, val):
        self.axis.controller.config.vel_gain = val

    # returns the velocity proportional gain value
    def get_vel_gain(self):
        return self.axis.controller.config.vel_gain

    # sets the velocity integrator gain value. Usually this is 0
    def set_vel_integrator_gain(self, val):
        self.axis.controller.config.vel_integrator_gain = val

    # returns the velocity integrator gain value. Usually this is 0
    def get_vel_integrator_gain(self):
        return self.axis.controller.config.vel_integrator_gain

    # checks if the motor is moving. Need to use a threshold speed. by default it is 0 turns/second
    def is_busy(self, speed=0):
        time.sleep(.5)  # allows motor to start moving, specifically for position control
        if (abs(self.get_vel())) > speed:
            return True
        else:
            return False

    # method to home ODrive using where the chassis is mechanically stopped
    # length is expected length of the track the ODrive takes
    # set length to -1 if you do not want the ODrive to check its homing
    # direction = 1 or -1 depending on which side of the track you want home to be at
    # use direction = 1 if you want the track to be of only positive location values
    def home(self, current1, current2, length=-1, direction=1):
        self.set_current(current1 * -1 * direction)
        print('here')
        time.sleep(1)
        print('there')
        while self.is_busy():
            pass

        time.sleep(1)

        self.set_home()
        print(self.get_pos())

        time.sleep(1)

        if not length == -1:
            self.set_current(current2 * 1 * direction)
            time.sleep(1)
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

    # homes the motor by having it move towards one side with a constant velocity. Once it can no longer move, it considers this its home
    # The direction can be specified either by the sign of the velocty passed in or through the direction parameter
    # If the length of the track is known, it can be passed in. If this is done, after moving to one side, the motor will move to the other to find if the homing was successful.
    def home_with_vel(self, vel = .5, length=-1, direction=1):
        self.set_vel(vel * -1 * direction)
        print('here')
        time.sleep(1)
        print('there')
        while self.is_busy():
            pass

        time.sleep(1)

        self.set_home()
        print(self.get_pos())

        time.sleep(1)

        if not length == -1:
            self.set_vel(vel * 1 * direction)
            time.sleep(1)
            while self.is_busy():
                pass

            print(self.get_pos())

            # end pos should be length
            if abs(self.get_pos() - length) > 50:
                print('ODrive could not home correctly')
                # maybe throw a more formal error here
                return False

        print('ODrive homed correctly')
        return True

    # only use with Wetmelon's endstop firmware
    def home_with_endstops(self, vel):
        self.axis.min_endstop.config.enabled = True
        self.axis.max_endstop.config.enabled = True
        self.set_vel(vel)
        while (self.axis.error == 0):
            pass
        if self.axis.error == 0x800 or self.axis.error == 0x1000:
            self.set_home()
            self.axis.error = 0

        self.axis.min_endstop.config.enabled = False
        self.axis.max_endstop.config.enabled = False

    # basically just runs into the wall for a set number of seconds, seems to be the most consistant
    def scuffed_home(self, seconds=5, torque=.1, dir=1):
        print("homing")
        if not(dir == 1 or dir == -1):
            raise Exception("direction should be 1 or -1")

        self.axis.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
        self.axis.controller.config.control_mode = CONTROL_MODE_TORQUE_CONTROL

        self.axis.controller.input_torque = torque * dir * -1  # multiply by -1 to make this make actual sense
        time.sleep(seconds)
        self.axis.controller.input_torque = 0
        self.set_home()

    # returns phase B current going into motor
    def get_curr_B(self):
        return self.axis.motor.current_meas_phB

    # returns phase C current going into motor
    def get_curr_C(self):
        return self.axis.motor.current_meas_phC

    # only use if doing encoder index search calibration and if setup is already done
    def index_and_hold(self, dir=2, good_dir=2):
        if dir != 2:
            self.axis.motor.config.direction = dir
        self.axis.requested_state = AXIS_STATE_ENCODER_INDEX_SEARCH
        while self.axis.current_state != AXIS_STATE_IDLE:
            time.sleep(0.1)
        if good_dir != 2:
            self.axis.motor.config.direction = good_dir
        self.set_pos(self.get_pos())

    # Clears all the errors on the axis
    def clear_errors(self):
        self.axis.error = 0
        self.axis.encoder.error = 0
        self.axis.motor.error = 0
        self.axis.controller.error = 0
        #There is also sensorless estimator errors but those are super rare and I am not sure what the object field is called to ima just leave it

    ##################################################
    ##########     TESTING FUNCTIONS        ##########
    ##################################################

    def idle(self):
        self.axis.requested_state = AXIS_STATE_IDLE



class double_ODrive(object):

    # ax_X and ax_Y are ODrive_Axis objects
    def __init__(self, ax_X, ax_Y):
        self.y = ax_X
        self.x = ax_Y

    def calibrate(self):
        self.x.axis.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
        self.y.axis.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
        start = time.time()
        while self.x.axis.current_state != AXIS_STATE_IDLE or self.x.axis.current_state != AXIS_STATE_IDLE:
            time.sleep(0.1)
            if time.time() - start > 15:
                print('could not calibrate, try rebooting odrive')
                return False

    def get_pos(self):
        return [self.x.get_pos, self.y.get_pos()]

    def set_pos(self, pos_x, pos_y):
        self.x.set_pos(pos_x)
        self.y.set_pos(pos_y)

    def home_with_vel(self, vel_x, vel_y):
        self.x.set_vel(vel_x)
        self.y.set_vel(vel_y)
        time.sleep(1)
        while (self.x.is_busy() or self.y.is_busy()):
            time.sleep(0.3)

        time.sleep(1)
        self.x.set_zero(self.x.get_raw_pos())
        self.y.set_zero(self.y.get_raw_pos())
        print("done homing")

    # only use with Wetmelon's endstop firmware
    def home_with_endstops(self, vel_x, vel_y):
        self.x.axis.min_endstop.config.enabled = True
        self.x.axis.max_endstop.config.enabled = True
        self.y.axis.min_endstop.confid.enabled = True
        self.y.axis.max_endstop.config.enabled = True
        self.x.set_vel(vel_x)
        self.y.set_vel(vel_y)
        while (self.x.axis.error == 0 or self.y.axis.error == 0):
            pass
        if self.x.axis.error == 0x800 or self.x.axis.error == 0x1000:
            self.x.set_zero(self.x.get_raw_pos())
            self.x.axis.error = 0

        if self.y.axis.error == 0x800 or self.y.axis.error == 0x1000:
            self.y.set_zero(self.y.get_raw_pos())
            self.y.axis.error = 0

        self.x.axis.min_endstop.config.enabled = False
        self.x.axis.max_endstop.config.enabled = False
        self.y.axis.min_endstop.confid.enabled = False
        self.y.axis.max_endstop.config.enabled = False


# calibrates a list of ODrive_Axis objects the minimal amount
def calibrate_list(odrives):
    calibrated = []
    i = 0
    for o in odrives:
        calibrated.append(False)
        if o.axis.motor.is_calibrated:
            if o.axis.encoder.is_ready:
                calibrated[-1] = True
            else:
                o.axis.requested_state = AXIS_STATE_ENCODER_OFFSET_CALIBRATION
        else:
            o.axis.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
    is_done = False

    while not is_done:
        i = -1
        for o in odrives:
            i += 1
            if o.axis.current_state == AXIS_STATE_IDLE or calibrated[i] == True:
                calibrated[i] = True
                continue
            else:
                time.sleep(0.2)
                break
        else:
            is_done = True


# configures a hoverboard motor. Requires save and reboot
def configure_hoverboard(ax):
    ax.axis.motor.config.pole_pairs = 15
    ax.axis.motor.config.resistance_calib_max_voltage = 4
    ax.axis.motor.config.requested_current_range = 25
    ax.axis.motor.config.current_control_bandwidth = 100
    ax.axis.controller.config.pos_gain = 1
    ax.axis.controller.config.vel_gain = 0.02
    ax.axis.controller.config.vel_integrator_gain = 0.1
    ax.axis.controller.config.vel_limit = 1000
    ax.axis.controller.config.control_mode = CTRL_MODE_VELOCITY_CONTROL