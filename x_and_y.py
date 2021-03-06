from time import sleep
import odrive
import ODrive_Ease_Lib
from pidev.Joystick import Joystick
from threading import Thread
from odrive.enums import *

od = odrive.find_any(serial_number='208D3388304B')
odz = odrive.find_any(serial_number='2065339E304B')
joy = Joystick(0, False)


class xAxis():
    #  booleans to keep things running
    sensor = True
    stick = True

    def start_threads(self):
        print("Start joystick thread")
        print("Start proximity sensor thread")
        Thread(target=self.joy_update).start()
        # Thread(target=self.proximity_update).start()

    def joy_update(self):
        print("lll")

        while self.stick:
            if joy.get_button_state(3):
                print("Check 4")

                self.ax.set_ramped_vel(-4, 1)
                sleep(.5)
                # self.ax.set_vel(0)

            # When pressing button 5 on joystick, move it toward from motor
            if joy.get_button_state(4):
                print("Check 5")

                self.ax.set_ramped_vel(4, 1)
                sleep(0.5)
                # self.ax.set_vel(0)

            if joy.get_button_state(1):
                print("Check 2")
                self.ay.set_ramped_vel(-4, 1)
                sleep(.5)

            elif joy.get_button_state(2):
                print("Check 3")

                self.ay.set_ramped_vel(9,1)  # Rising is delayed, hold it down to move it, stop by pressing down
                sleep(.05)

                # self.ay.set_ramped_vel(0, 4)
               # self.ay.set_vel(0)  # Nvm, I'm just being dumb; set this to be associated with ay

            if joy.get_button_state(0) == 1:
                self.ay.set_vel(0)
                self.ax.set_vel(0)
                self.az.set_vel(0)

        # else:
            #     self.ay.set_vel(0)

            if joy.get_button_state(10):
                self.ay.set_pos_traj(self.ay.get_pos()+2, 1, 5, 1)
                sleep(1)

            if joy.get_button_state(9):
                self.ay.set_pos_traj(self.ay.get_pos()-2, 1, 5, 1)
                sleep(1)

            if joy.get_button_state(7):
                print("Check 8")

                self.az.set_ramped_vel(-3, 1)  # Set velocity to -3 revs/turn, stops after 0.1 secs
                sleep(.5)


            # When pressing button 5 on joystick, move it toward from motor
            if joy.get_button_state(8):
                print("Check 9")

                self.az.set_ramped_vel(3, 1)  # Set velocity to 3 revs/turn, stops after 0.1 secs

            if joy.get_button_state(5):
                ODrive_Ease_Lib.dump_errors(od)

            if joy.get_button_state(6):
                print("Idle all motors")
                self.ax.idle()
                self.ay.idle()
                self.az.idle()
                sleep(0.4)

# axis x is moving for no reason after releasing trigger.
    # Resolved. Leftover code moved x-axis when detected z-axis on sensor.

# 2065339E304B z-axis

    # def proximity_update(self):
    #     if joy.get_button_state(5):
    #         print("Check 6")
    #     print("FUUUUUUUUUUAS")
    #     while self.sensor:
    #         if self.ax.axis.min_endstop.endstop_state:
    #             print("Contact w/ sensor")
    #             od.clear_errors()  # clear errors to allow the rest of the machine to run
    #             print("Checking after")  # ensure that errors don't halt the deliverance of commands



    # Port 8 x axis
    # Port 2 axis z

    def onstartup(self):
        # dumperrors
        ODrive_Ease_Lib.dump_errors(od)
        # define ax and ay
        self.ax = ODrive_Ease_Lib.ODrive_Axis(od.axis0, 15, 15)
        self.ay = ODrive_Ease_Lib.ODrive_Axis(od.axis1, 50, 15)
        self.az = ODrive_Ease_Lib.ODrive_Axis(odz.axis0, 15, 15)
        # calibrate
        if not self.ax.is_calibrated():  # calibrate x (left right)
            print("calibrating...")
            self.ax.calibrate_with_current_lim(25)

        if not self.ay.is_calibrated():
            self.ay.calibrate_with_current_lim(40)

        if not self.az.is_calibrated():
            self.az.calibrate_with_current_lim(25)

        self.ax.set_pos_gain(20)
        self.ax.set_vel_gain(0.16)
        self.ax.set_vel_integrator_gain(0.32)
        self.ax.axis.controller.config.enable_overspeed_error = False
        od.clear_errors()

        self.ax.idle()
        self.ay.idle()


if __name__ == "__main__":
    print("ODrive Version: ", odrive.version.get_version_str())

    # Find a connected ODrive (this will block until you connect one)
    print("finding an odrive...")
    odrv0 = odrive.find_any()
    print("odrive found!")

    odrv0.clear_errors()
    x = xAxis()
    x.onstartup()
    x.start_threads()
