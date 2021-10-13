"""
Example usage of the ODrive python library to monitor and control ODrive devices
"""

from time import sleep
import odrive
from odrive.enums import *
import ODrive_Ease_Lib


def startup(od):
    assert od.config.enable_brake_resistor is True, "Check for faulty brake resistor."

    # Selecting an axis to talk to, axis0 and axis1 correspond to M0 and M1 on the ODrive
    ax = ODrive_Ease_Lib.ODrive_Axis(od.axis0)

    print("Current Position in Turns = ", ax.get_pos())
    print("Encoder Position in Turns = ", ax.get_raw_pos())
    ax.set_vel_limit(10)  # Sets the velocity limit to be 10 turns/s
    ax.set_vel(5)  # Starts turning the motor 5 turns/s
    sleep(3)
    print("Encoder Measured Velocity = ", ax.get_vel())
    ax.set_vel(0)  # Stops motor
    print("Current Position in Turns = ", ax.get_pos())  # Should be at 15 turns
    print("Encoder Position in Turns = ", ax.get_raw_pos())
    ax.set_raw_pos(0)
    while ax.is_busy(1):
        sleep(.1)
    ax.idle()


if __name__ == "__main__":
    print("ODrive Version: ", odrive.version.get_version_str())

    # Find a connected ODrive (this will block until you connect one)
    print("finding an odrive...")
    odrv0 = odrive.find_any()
    print("odrive found!")

    odrv0.clear_errors()
    assert odrv0.error == 0, "Odrive has errors present, please diagnose using odrivetool"

    startup(odrv0)
    #ODrive_Ease_Lib.dump_errors(odrv0)
