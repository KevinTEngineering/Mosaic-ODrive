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
    sensor = True
    stick = True

    def start_threads(self):
        print("Start joystick thread")
        print("Start proximity sensor thread")
        Thread(target=self.joy_update).start()
        Thread(target=self.proximity_update).start()



    def joy_update(self):
        print("lll")

        while self.stick:
            # When pressing button 4 on joystick, move it away from motor
            if joy.get_button_state(3):
                print("Check 4")

                self.ax.set_vel(-3)  # Set velocity to -3 revs/turn, stops after 0.1 secs
                sleep(.1)
                self.ax.set_vel(0)

            # When pressing button 5 on joystick, move it toward from motor
            if joy.get_button_state(4):
                print("Check 5")

                self.ax.set_vel(3)  # Set velocity to 3 revs/turn, stops after 0.1 secs
                sleep(0.1)
                self.ax.set_vel(0)

            if joy.get_button_state(0):
                quit()

    def proximity_update(self):
        if joy.get_button_state(5):
            print("Check 6")
        print("FUUUUUUUUUUAS")
        while self.sensor:
            if self.ax.axis.min_endstop.endstop_state:
                print("Contact w/ sensor")
                od.clear_errors() # clear errors to allow the rest of the machine to run
                print("Checking after")
                self.ax.set_vel(-2)
                sleep(0.2)
                self.ax.set_vel(0)


    # Port 8 x axis
    # Port 2 axis z

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

        axax = self.ax.axis
        od.config.gpio8_mode = GPIO_MODE_DIGITAL
        axax.min_endstop.config.gpio_num = 2  # pin 8 for x, 2 for y, 2 for z
        self.Prox_Sensor_Number = axax.min_endstop.config.gpio_num  # setting to global class Runner variable just so that I can reference it in the Thread print statements
        axax.min_endstop.config.enabled = True  # Turns sensor on, says that I am using it
        axax.min_endstop.config.offset = 1  # stops 1 rotation away from sensor
        axax.min_endstop.config.debounce_ms = 20  # checks again after 20 milliseconds if actually pressed, which is what debounce is :D
        axax.min_endstop.config.offset = -1.0 * 8192  # hop back from GPIO in order to allow for function again
        od.config.gpio8_mode = GPIO_MODE_DIGITAL_PULL_DOWN


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
    x.joy_update()
