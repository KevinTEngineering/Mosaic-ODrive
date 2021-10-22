from time import sleep

from time import sleep
import odrive
import ODrive_Ease_Lib
from pidev.Joystick import Joystick
from threading import Thread
from odrive.enums import *

od = odrive.find_any()
joy = Joystick(0, False)

class xAxis():
    print("LOp")

    def start_joy_thread(self):
        print("okl")
        Thread(target=self.joy_update).start()

    def joy_update(self):
        print("lll")
        stick = True
        while stick:
            if joy.get_button_state(3):
                print("Check 4")

                self.ax.set_vel(-3)
                sleep(.1)
                self.ax.set_vel(0)

            if joy.get_button_state(4):
                print("Check 5")

                self.ax.set_vel(3)
                sleep(0.1)
                self.ax.set_vel(0)

            if joy.get_button_state(2):
                stick = False
            if self.ax.axis.min_stop.axis_state:
                print("Contact w/ sensor")

# Port 8


    def onstartup(self):
        ODrive_Ease_Lib.dump_errors(od)
        od.clear_errors()
        self.ax = ODrive_Ease_Lib.ODrive_Axis(od.axis0, 15, 15)  # currentlim, vlim

        self.ax.set_pos_gain(20)
        self.ax.set_vel_gain(0.16)
        self.ax.set_vel_integrator_gain(0.32)
        self.ax.axis.controller.config.enable_overspeed_error = False
        od.clear_errors()
        if not self.ax.is_calibrated():  # or od.error != 0:
            print("calibrating...")
            self.ax.calibrate_with_current(35)
        # bugtesting
        # print(od.vbus_voltage)
        # print(self.ax.get_calibration_current(), self.ax.axis.mot)
        # endbug
        # self.ax.idle()


if __name__ == "__main__":
    print("ODrive Version: ", odrive.version.get_version_str())

    # Find a connected ODrive (this will block until you connect one)
    print("finding an odrive...")
    odrv0 = odrive.find_any()
    print("odrive found!")

    odrv0.clear_errors()
    x = xAxis()
    x.onstartup()
    x.start_joy_thread()
    x.joy_update()
