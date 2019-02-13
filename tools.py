# coding: utf-8
import odrive
from odrive.enums import *
import ODrive_Ease_Lib
import time


def setup():
    
    od = odrive.find_any()
    print("setup od")
    ax1 = ODrive_Ease_Lib.ODrive_Axis(od.axis0)
    ax2 = ODrive_Ease_Lib.ODrive_Axis(od.axis1)

    ax1.set_vel(-15000)
    ax2.set_vel(-15000)
    time.sleep(5)
    ax1.set_vel(15000)
    ax2.set_vel(15000)
    time.sleep(3)
    ax1.set_vel(0)
    ax2.set_vel(0)

    od.axis0.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE 
    od.axis1.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
    start = time.time()
    while od.axis0.current_state != AXIS_STATE_IDLE or od.axis1.current_state != AXIS_STATE_IDLE:
        time.sleep(0.1)
        if time.time() - start > 15:
            print("could not calibrate, try rebooting odrive")
            return False

    ax1.set_curr_limit(5)
    ax2.set_curr_limit(5)
    ax1.set_vel_limit(150000)
    ax2.set_vel_limit(150000)

    ax1.home_with_vel(-20000)
    ax2.home_with_vel(-20000)

    return ax1, ax2


def setup_enc():

    od = odrive.find_any()
    print("setup")
    ax0 = ODrive_Ease_Lib.ODrive_Axis(od.axis0)
    ax1 = ODrive_Ease_Lib.ODrive_Axis(od.axis1)
    od.axis0.requested_state = AXIS_STATE_ENCODER_OFFSET_CALIBRATION
    od.axis1.requested_state = AXIS_STATE_ENCODER_OFFSET_CALIBRATION
    start = time.time()

    while od.axis0.current_state != AXIS_STATE_IDLE or od.axis1.current_state != AXIS_STATE_IDLE:
        time.sleep(0.1)
        if time.time() - start > 15:
            print("could not calibrate, try rebooting odrive")
            return False

    ax0.set_vel_limit(150000)
    ax1.set_vel_limit(150000)


    ax0.set_vel(15000)
    ax1.set_vel(15000)
    time.sleep(15)
    ax0.set_vel(0)
    ax1.set_vel(0)
    ax0.set_zero(ax0.get_raw_pos())
    ax1.set_zero(ax1.get_raw_pos())
    print(ax0.get_pos())
    print(ax1.get_pos())  
 
    return ax0, ax1


def test(ax1, ax2, n=20):
    
    ax1.set_vel(-3000)
    ax2.set_vel(-3000)
    time.sleep(5)
    ax1.set_vel(0)
    ax2.set_vel(0)
    
    start = ax1.get_pos()
    diff = abs(ax1.get_pos() - ax2.get_pos())
    increment = 100000 / (n - 1)
    
    for x in range(n):

        ax1.set_vel(((-1) ** x) * (-5000 - (x * increment)))
        ax2.set_vel(((-1) ** x) * (-5000 - (x * increment)))
        
        while abs(start - ax1.get_pos()) < 70000:
            time.sleep(0.1)
            curr_diff = abs(ax1.get_pos() - ax2.get_pos())
            if diff < curr_diff:
                diff = curr_diff
                print(str(diff) + " - " + str(x))
                
        start = ax1.get_pos()
    
    ax1.set_vel(0)
    ax2.set_vel(0)
    return diff


def test_pos(ax1, ax2, n=20):
    
    ax1.set_pos(-20000)
    ax2.set_pos(-20000)
    time.sleep(5)

    start = ax1.get_pos()
    diff = abs(ax1.get_pos() - ax2.get_pos())
    increment = 100000 / (n - 1)

    for x in range(n):
        ax1.set_vel_limit(5000 + (x * increment))
        ax2.set_vel_limit(5000 + (x * increment))
        ax1.set_pos(-55000 - (((-1) ** x) * 35000))
        ax2.set_pos(-55000 - (((-1) ** x) * 35000))
        
        while ax1.is_busy() or ax2.is_busy():
            time.sleep(0.1)
            curr_diff = abs(ax1.get_pos() - ax2.get_pos())
            if diff < curr_diff:
                diff = curr_diff
                print(str(diff) + " - " + str(x))

        start = ax1.get_pos()
    
    ax1.set_vel(0)
    ax2.set_vel(0)
    return diff


def test_not_pid(ax1, ax2, n=20, kp=0.0, ki=0.0):  # kp=10 and ki=0.0008 is nice

    ax1.set_pos(-10000)
    ax2.set_pos(-10000)
    
    time.sleep(5)

    start = ax1.get_pos()
    diff = abs(ax1.get_pos() - ax2.get_pos())
    increment = 100000 / (n - 1)
    
    for x in range(n):
        
        curr_vel = ((-1) ** x) * (-5000 - (x * increment)) 
        ax1.set_vel(curr_vel)
        ax2.set_vel(curr_vel)
        
        while abs(start - ax1.get_pos()) < 70000:
            curr_diff = ax1.get_pos() - ax2.get_pos()
            if diff + 10 < abs(curr_diff):
                diff = abs(curr_diff)
                print(str(diff) + " - " + str(x))
            
            ax1.set_vel(curr_vel - curr_diff * kp - curr_diff * ki * abs(curr_vel))
            ax2.set_vel(curr_vel + curr_diff * kp + curr_diff * ki * abs(curr_vel))
 
        start = ax1.get_pos()
    
    ax1.set_vel(0)
    ax2.set_vel(0)
    return diff

def test_pid(ax1, ax2, n=20, kp=0.0, ki=0.0, kd=0.0):  # kp=50 and ki=0.006 is nice

    ax1.set_pos(-10000)
    ax2.set_pos(-10000)
    time.sleep(5)
    
    start = ax1.get_pos()
    diff = abs(ax1.get_pos() - ax2.get_pos())
    increment = 150000 / (n - 1)
    diff_sum = diff
    last_diff = diff
    
    for x in range(n):
        
        curr_vel = ((-1) ** x) * (-5000 - (x * increment)) 
        ax1.set_vel(curr_vel)
        ax2.set_vel(curr_vel)
        curr_diff = 0

        while abs(start - ax1.get_pos()) < 70000:
            curr_diff = ax1.get_pos() - ax2.get_pos()
            diff_sum += curr_diff
            if diff + 10 < abs(curr_diff):
                diff = abs(curr_diff)
                print(str(diff) + " - " + str(x))
            
            ax1.set_vel(curr_vel - curr_diff * kp - diff_sum * ki - (curr_diff - last_diff) * kd)
            ax2.set_vel(curr_vel + curr_diff * kp + diff_sum * ki + (curr_diff - last_diff) * kd)
       
            last_diff = curr_diff
        
        diff_sum = curr_diff
        start = ax1.get_pos()
    
    ax1.set_vel(0)
    ax2.set_vel(0)
    return diff

def pid_pid(ax1, ax2, n=20, kp=0.0, ki=0.0, kd=0.0, t_kp=0.0, t_ki=0.0, t_kd=0.0):  # kp=50 and ki=0.006 is nice

    ax1.set_pos(-10000)
    ax2.set_pos(-10000)
    time.sleep(5)
    
    start = ax1.get_pos()
    err = 0
    diff = abs(ax1.get_pos() - ax2.get_pos())
    increment = 150000 / (n - 1)

    err_sum = 0
    last_err = 0
    diff_sum = diff
    last_diff = diff
    
    for x in range(n):
        
        curr_vel = ((-1) ** x) * (-5000 - (x * increment)) 
        ax1.set_vel(curr_vel)
        ax2.set_vel(curr_vel)
        curr_diff = 0
        curr_err = 0

        while abs(start - ax1.get_pos()) < 70000:
            avg_vel = (ax1.get_vel() + ax2.get_vel()) / 2
            curr_err = avg_vel - curr_vel
            err_sum += curr_err
            
            curr_diff = ax1.get_pos() - ax2.get_pos()
            diff_sum += curr_diff
            if err + 10 < abs(curr_err):
                err = abs(curr_err)
                print(str(err) + " - " + str(x))
            
            ax1.set_vel(curr_vel - curr_diff * kp - diff_sum * ki - (curr_diff - last_diff) * kd
                         - curr_err * t_kp - err_sum * t_ki - (curr_err - last_err) * t_kd)
            ax2.set_vel(curr_vel + curr_diff * kp + diff_sum * ki + (curr_diff - last_diff) * kd
                         - curr_err * t_kp - err_sum * t_ki - (curr_err - last_err) * t_kd)
 
            last_diff = curr_diff
            last_err = curr_err
        
        diff_sum = curr_diff
        err_sum = curr_err
        start = ax1.get_pos()
    
    ax1.set_vel(0)
    ax2.set_vel(0)
    return diff


