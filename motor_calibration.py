import odrive
from fibre.protocol import ChannelBrokenException
from odrive.enums import *


def reboot_odrive():
    """
    Save the configuration and reboot the ODrive.
    """
    try:
        print("Rebooting ODrive")
        od.save_configuration()
        od.reboot()
    except ChannelBrokenException:
        print('motor calibration complete')
        exit(0)


def calibrate_motor(axis):
    """
    Calibrate the ODrive motor
    @param axis: The axis number the ODrive is connected to
    """
    global od
    od = odrive.find_any()

    print("odrive found: " + str(od.serial_number))

    if od.axis0.motor.config.pre_calibrated:
        print("The motor is already calibrated, setting pre_calibrated to false. Please rerun this script")
        od.axis0.motor.config.pre_calibrated = False
        reboot_odrive()

    if axis :
        od.axis1.requested_state = AXIS_STATE_MOTOR_CALIBRATION
    else:
        od.axis0.requested_state = AXIS_STATE_MOTOR_CALIBRATION

    print('motor calibrated')

    if axis:
        od.axis1.motor.config.pre_calibrated = True
    else:
        od.axis0.motor.config.pre_calibrated = True

    print('configuration saved')


if __name__ == "__main__":
    print("Enter axis number")
    calibrate_motor(int(input()))
    reboot_odrive()
