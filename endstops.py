#For use with wetmelon's endstop branch
#Updated 4/1/19 by Blake Lazarine


'''
import odrive
from odrive.enums import *
od = odrive.find_any()
import ODrive_Ease_Lib
ax = ODrive_Ease_Lib.ODrive_Axis(od.axis1)
ax.axis.min_enstop.config.gpio_num = 2
ax.axis.min_enstop.is_active_high = True
ax.axis.min_endstop.config.enabled = True
'''


def home_with_endstop(ax, direction=1, speed=5000):
    ax.axis.min_endstop.config.enabled = True
    ax.axis.max_endstop.config.enabled = True
    ax.set_vel(direction * speed)
    while(ax.axis.error == 0):
        pass
    if ax.axis.error == 2048:
        ax.set_zero(ax.get_raw_pos())
        ax.axis.error = 0
    ax.axis.min_endstop.config.enabled = False
    ax.axis.max_endstop.config.enabled = False
