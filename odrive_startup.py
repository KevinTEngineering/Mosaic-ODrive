"""
Example usage of the ODrive python library to monitor and control ODrive devices
"""

from time import sleep
import odrive
import ODrive_Ease_Lib


def startup(od):
    assert od.config.enable_brake_resistor is True, "Check for faulty brake resistor."
    ODrive_Ease_Lib.dump_errors(odrv0)

    # Selecting an axis to talk to, axis0 and axis1 correspond to M0 and M1 on the ODrive
    ax = ODrive_Ease_Lib.ODrive_Axis(od.axis1, 20, 40)

    if not ax.is_calibrated() or od.error != 0:
        print("calibrating...")
        ax.set_calibration_current(40)
        ax.calibrate()

    # print("Velocity Tolerance: ", ax.axis.controller.config.vel_limit_tolerance)
    # print("Tolerance is: ", ax.axis.controller.config.enable_overspeed_error)
    # ax.axis.controller.config.vel_limit_tolerance = 2


    print("Current Position in Turns = ", round(ax.get_pos(), 2))
    ax.set_vel_limit(10)  # Sets the velocity limit to be 10 turns/s
    ax.set_vel(5)  # Starts turning the motor 5 turns/s
    sleep(3)
    print("Encoder Measured Velocity = ", round(ax.get_vel(), 2))
    ax.set_vel(0)  # Stops motor
    print("Current Position in Turns = ", round(ax.get_pos(), 2))  # Should be at 15 turns
    ax.set_pos(0)
    while ax.is_busy():
        sleep(.1)
    print("Current Position in Turns = ", round(ax.get_pos(), 2))

    sleep(3)

    ax.set_vel_limit(10)
    ax.set_pos(50)
    while ax.is_busy():
        sleep(.1)
    print("Current Position in Turns = ", round(ax.get_pos(), 2))
    ax.set_pos(0)
    while ax.is_busy():
        sleep(.1)
    print("Current Position in Turns = ", round(ax.get_pos(), 2))

    ax.idle()


if __name__ == "__main__":
    print("ODrive Version: ", odrive.version.get_version_str())

    # Find a connected ODrive (this will block until you connect one)
    print("finding an odrive...")
    odrv0 = odrive.find_any()
    print("odrive found!")

    odrv0.clear_errors()

    startup(odrv0)
    ODrive_Ease_Lib.dump_errors(odrv0)
