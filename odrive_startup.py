"""
Example usage of the ODrive python library to monitor and control ODrive devices
"""

from time import sleep
from ODrive_Ease_Lib import *


def startup(od):
    # od.config.enable_brake_resistor = True
    assert od.config.enable_brake_resistor is True, "Check for faulty brake resistor."
    dump_errors(od)

    # Selecting an axis to talk to, axis0 and axis1 correspond to M0 and M1 on the ODrive
    ax = ODrive_Axis(od.axis0)
    # Basic motor tuning, for more precise tuning follow this guide: https://docs.odriverobotics.com/control.html#tuning
    ax.set_gains()

    if not ax.is_calibrated():
        print("calibrating...")
        # ax.calibrate()
        ax.calibrate_with_current(20)

    print("Current Limit: ", ax.get_current_limit())
    print("Velocity Limit: ", ax.get_vel_limit())

    # ax.axis.controller.config.vel_limit_tolerance = 2
    # ax.axis.controller.config.enable_overspeed_error = True
    print("Velocity Tolerance: ", ax.axis.controller.config.vel_limit_tolerance)
    print("Using Velocity Tolerance: ", ax.axis.controller.config.enable_overspeed_error)

    # SETTING VELOCITY
    # print("Current Position in Turns = ", round(ax.get_pos(), 2))
    # ax.set_vel_limit(5)  # Sets the velocity limit to be X turns/s
    # ax.set_vel(1)  # Starts turning the motor X turns/s
    # sleep(3)
    # print("Encoder Measured Velocity = ", round(ax.get_vel(), 2))
    # ax.set_vel(0)  # Stops motor
    # print("Current Position in Turns = ", round(ax.get_pos(), 2))
    # ax.set_pos(0)
    # while ax.is_busy():
    #     sleep(.01)
    # print("Current Position in Turns = ", round(ax.get_pos(), 2))
    #
    # sleep(2)

    # SETTING RAMPED VELOCITY
    # TODO: NEEDS TESTING
    ax.set_vel_limit(10)  # Sets the velocity limit to be X turns/s
    print("speeding up")
    ax.set_ramped_vel(5, 1)  # Starts accelerating motor to X turns/s
    sleep(10)
    print("slowing down")
    ax.set_ramped_vel(0, 1)  # Stops motor
    while ax.is_busy():
        sleep(.01)

    sleep(2)

    # SETTING POSITION
    ax.set_vel_limit(5)
    ax.set_pos(3)
    while ax.is_busy():
        sleep(.01)
    print("Current Position in Turns = ", round(ax.get_pos(), 2))
    ax.set_pos(0)
    while ax.is_busy():
        sleep(.01)
    print("Current Position in Turns = ", round(ax.get_pos(), 2))

    ax.idle()  # Removes motor from CLOSED_LOOP_CONTROL, essentially 'frees' the motor


if __name__ == "__main__":
    od = find_odrive()
    startup(od)
    dump_errors(od)