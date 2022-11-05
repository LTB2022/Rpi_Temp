# Little Time Buddy-
# Integration with Capacitive TFT Screen-Release and customtkinter Code Rev. 8
# 2022-11-05
# CSheeran
# MHernandez
# Team 4, CSUS EEE193B

# pylint: disable=global-statement,stop-iteration-return,no-self-use,useless-super-delegation

import csv          # Not being used
import serial
import gpiozero

import time as t    # call the time module with "t"

from datetime import datetime, date, timedelta

import dateutil as du   # call the dateutil module with "du"
from dateutil import tz
from dateutil.relativedelta import relativedelta

import tkinter as tk
from tkinter import *
from tkinter import Tk, Label, Button, font
import customtkinter
import time
import sys
import RPi.GPIO as GPIO


###############################################################################

# Set to false to disable testing/tracing code
TESTING = False

################################################################################
# Setup hardware

# Adafruit 2.8" TFT Capacitive Touchscreen operates the following pins:
# I2C for touch sensing: Pin3-GPIO 2 (SDA), Pin5-GPIO 3 (SCL). Be sure to include the RTC on the I2C bus
# SPI pins: (SCK) Pin23-GPIO 11, (MOSI) Pin19-GPIO 10, (MISO) Pin21-GPIO 9, (CE0) Pin24-GPIO 8.
# Also: Pin18-GPIO 24, Pin22-GPIO 25

# Input Pins, DESIGNATED BY GPIO#
switch_1 = gpiozero.Button(26, pull_up=False)   # And/Or read the output pin below, DEMO green wire
switch_2 = gpiozero.Button(6, pull_up=False)   # And/Or read the output pin below, DEMO blue wire

# Output Pins, DESIGATED BY PIN# NOT GPIO#
gui_out1 = gpiozero.DigitalOutputDevice(23,active_high=True, initial_value=False)   # GUI button 1 is on the left side of the screen, DEMO orange wire
gui_out2 = gpiozero.DigitalOutputDevice(16, active_high=True, initial_value=False)  # GUI button 2 is o the right side of the screen, DEMO yellow wire
redLED = gpiozero.DigitalOutputDevice(5, active_high=True, initial_value=False)  # illuinate a red LED to indicate the timestamp operation


################################################################################
#Python datetime function
now = datetime.now(tz=tz.tzlocal())    #Use the actual time set in the Pi
print("Current device time:", now)     # uncomment for debugging
print('\n')


################################################################################
# Global variables

################################################################################
# Support functions

# Code tracing feature located in the "pressed" method of the "StateMachine" Class
def log(s):
    """Print the argument if testing/tracing is enabled."""
    if TESTING:
        print(s)


################################################################################
# State Machine, Manages states

class StateMachine():                         # Question: Why is the argument named "object?"

    def __init__(self):                             # Needed constructor
        self.state = None
        self.states = {}


    def add_state(self, state):                     # "add state" attribute, adds states to the machine
        self.states[state.name] = state

    def go_to_state(self, state_name):              # "go to state" attribute, facilittes transition to other states. Prints confirmation when "Testing = True"
        if self.state:
            log('Exiting %s\n' % (self.state.name))
            self.state.exit(self)
        self.state = self.states[state_name]
        log('Entering %s' % (self.state.name))
        self.state.enter(self)

    def pressed(self):                              # "button pressed" attribute. Accessed at the end of each loop, applies a pause and prints confirmaiton if setup.
        if self.state:
            log('Updating %s' % (self.state.name))
            self.state.pressed(self)
            #print("'StateMachine' Class occurrence")  # Use this print statement to understand how the states transition here to update the state in the serial monitor
            t.sleep(.50)                             # Critial pause needed to prevent the serial monitor from being "flooded" with data and crashing


################################################################################
# States
################################################################################

# Abstract parent class
# State Machine serves as a similiar inheritance structure to the states following the "State" class

class State():


    def __init__(self):         # Constructor. Sets variables for the class, in this instance only, "self". Note machine variable below in the "enter" attribute
        pass

    @property
    def name(self):             # Attribute. Only the name is returned in states below. The State object shouldn't be called and returns nothing
        return ''

    def enter(self, machine):   # Class Attribute. Does what is commanded when the state is entered
        pass

        def SW1ON(self):
            pass

        def SW2ON(self):
            pass

    def exit(self, machine):    # Class Attribute. Does what is commanded when exiting the state
        pass

    def pressed(self, machine): # Class Attribute. Has never been observed to be called
        pass


########################################
# This state is active when powered on and other states return here
class Home(State):

    # Declare global Home state variables
    stamp1 = "wasabi"
    #Intitalize global Home state variables

    def __init__(self):
        super().__init__()

    @property
    def name(self):
        return 'Home'

    def enter(self, machine):
        State.enter(self, machine)
        print('#### Home State ####')                                   # Print "Home State" to the serial monitor

        # tkinter Home Screen GUI
        customtkinter.set_appearance_mode("light")  # Modes: system (default), light, dark
        customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, gree
        win = customtkinter.CTk()                                       # create CTk window like you do with the Tk window
        # Define the tkinter window instance
        win.title("ltb Home")                                           # title for window
        win.geometry('320x240')                                         # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
        win.eval('tk::PlaceWindow . center')                            # Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
        #win.attributes('-fullscreen', True)                            # uncomment to use fullscreen
        # Window frame for the profile buttons
        win.frame = customtkinter.CTkFrame(master=win, width=320, height=180, corner_radius=8)
        win.frame.place(relx=0.5, rely=0.62, anchor=customtkinter.CENTER)

        def SW1ON():
            #global stamp1
            gui_out1.value=True                                         # Sets GPIO output
            print("gui_out1 = ", gui_out1.value)
            t.sleep(0.1)
            # Haptic placeholder
            # Sound placeholder
            win.quit()
            win.destroy()                                               # Closes GUI window
            machine.go_to_state('EEIntern')

        def SW2ON():
            gui_out2.value=True                                         # Sets GPIO output
            print("gui_out2 = ", gui_out2.value)
            # Haptic placeholder
            # Sound placeholder
            t.sleep(0.1)
            win.quit()
            win.destroy()                                               # Closes GUI window
            machine.go_to_state('EEE193B')

        def focusON():
            redLED.value=True                                         # Sets GPIO output
            print("redLED = ", redLED.value)
            # Haptic placeholder
            # Sound placeholder
            t.sleep(0.1)
            win.quit()
            win.destroy()                                               # Closes GUI window
            machine.go_to_state('FocusTimer')

        # Clock function, global display
        def get_time():
            time_Var = time.strftime("%I:%M:%S %p")
            date_Var = time.strftime("%Y-%m-%d")
            clock.configure(text= time_Var)
            date.configure(text= date_Var)
            clock.after(200, get_time)

        # Home Label
        LTB_label = customtkinter.StringVar(value="LTB\n" + "Litte Time Buddy")
        label = customtkinter.CTkLabel(master=win, textvariable=LTB_label, width=120, height=25,
                                       fg_color=("white", "black"),
                                       corner_radius=4)
        label.place(relx=0.82, rely=0.06, anchor=customtkinter.CENTER)
        # Define the tkinter switch instances
        SW1Button = customtkinter.CTkButton(master=win, text="EE Intern", command=SW1ON)
        SW1Button.place(relx=0.55, rely=0.8, anchor=customtkinter.W)
        SW2Button = customtkinter.CTkButton(master=win, text="CSUS 193B", command=SW2ON)
        SW2Button.place(relx=0.45, rely=0.8, anchor=customtkinter.E)
        # Focus Button
        Fbtn = customtkinter.CTkButton(master=win, text="Focus", width=120, height=25, corner_radius=4,
                                       command=focusON)
        Fbtn.place(relx=0.63, rely=0.14, anchor=customtkinter.NW)
        # Display Parameters for the Clock
        clkText = customtkinter.CTkLabel(master=win, text="Time:")
        clkText.place(relx=-0.15, rely=0.08, anchor=customtkinter.NW)
        clock = customtkinter.CTkLabel(master=win,
                                       width=60,
                                       height=25)
        clock.place(relx=0.13, rely=0.09, anchor=customtkinter.NW)
        # Display Parameters for the Date
        datetxt = customtkinter.CTkLabel(master=win, text="Date:")
        datetxt.place(relx=-0.15, rely=-0.01, anchor=customtkinter.NW)
        date = customtkinter.CTkLabel(master=win,
                                      width=60,
                                      height=25)
        date.place(relx=0.13, rely=0.00, anchor=customtkinter.NW)
        get_time()
        # Starting tkinter main GUI loop
        mainloop()  # commanding mainloop for starting main loop

        #t.sleep(0.5) # Slows down the transitions

    def exit(self, machine):
        State.exit(self, machine)

        gui_out1.value=False
        gui_out2.value=False
        redLED.value=False
        print("gui_out1 = ", gui_out1.value)
        print("gui_out2 = ", gui_out2.value)
        print("redLED = ", redLED.value)


    def pressed(self, machine):             # Former mechansm to change states, reserved for a power button

        #if switch_1.is_pressed:
            #machine.go_to_state('xx')
        #if switch_2.is_pressed:
            #machine.go_to_state('xx')
        pass

########################################
# Utilize a Focus Timer like an interval timer return to the Home state when finished
class FocusTimer(State):

    # Declare global FocusTimer state variables

    #Intitalize global FocusTimer variables

    def __init__(self):
        super().__init__()

    @property
    def name(self):
        return 'FocusTimer'

    def enter(self, machine):
        State.enter(self, machine)
        print('#### Focus Timer State ####')                                   # Print "Home State" to the serial monitor

        # customtkinter Focus GUI
        customtkinter.set_appearance_mode("light")     # Modes: system (default), light, dark
        customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
        # Define the tkinter window instance
        win = customtkinter.CTk()                  # create CTk window like you do with the Tk window
        win.title("Focus Timer")                                        # title for window
        win.geometry('320x240')                                         # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
        win.eval('tk::PlaceWindow . center')                            # Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
        #win.attributes('-fullscreen', True)                            # uncomment to use fullscreen
        # Window frame for the profile buttons
        win.frame = customtkinter.CTkFrame(master=win, width=320, height=180, corner_radius=8)
        win.frame.place(relx=0.5, rely=0.62, anchor=customtkinter.CENTER)

        def SW1ON():
            redLED.value=True                                         # Sets GPIO output
            print("redLED = ", redLED.value)
            t.sleep(0.1)
            # Haptic placeholder
            # Sound placeholder
            #win.quit()
            #win.destroy()                                               # Closes GUI window

        def SW2ON():
            gui_out2.value=True                                         # Sets GPIO output
            print("redLED = ", redLED.value)
            t.sleep(0.1)
            # Haptic placeholder
            # Sound placeholder
            #win.quit()
            #win.destroy()                                               # Closes GUI window

        def SW3ON():
            redLED.value=True                                         # Sets GPIO output
            print("redLED = ", redLED.value)
            t.sleep(0.1)
            # Haptic placeholder
            # Sound placeholder
            win.quit()
            win.destroy()                                               # Closes GUI window
            machine.go_to_state('Home')

        def button_function():
            print("button pressed")
        # Focus Timer tkinter Label
        focuslabel = customtkinter.StringVar(value="Focus\n" + "Timer\n" + "-Focusing-")
        fkslabel = customtkinter.CTkLabel(master=win, textvariable=focuslabel, width=120, height=25,
                                          fg_color=("white", "black"), corner_radius=4)
        fkslabel.place(relx=0.82, rely=0.109, anchor=customtkinter.CENTER)
        # Define the tkinter switch instances
        SW1Button = customtkinter.CTkButton(master=win, text="Start", command=SW1ON)
        SW1Button.place(relx=0.55, rely=0.7, anchor=customtkinter.SW)
        SW2Button = customtkinter.CTkButton(master=win, text="Stop", command=SW2ON)
        SW2Button.place(relx=0.55, rely=0.9, anchor=customtkinter.W)
        SW3Button = customtkinter.CTkButton(master=win, text="Reset", command=button_function)
        SW3Button.place(relx=0.45, rely=0.9, anchor=customtkinter.E)
        SW4Button = customtkinter.CTkButton(master=win, text="Home", command=SW3ON)
        SW4Button.place(relx=0.45, rely=0.7, anchor=customtkinter.SE)
        # Starting tkinter main GUI loop
        mainloop()  # commanding mainloop for starting main loop

        #t.sleep(0.5) # Slows down the transitions

    def exit(self, machine):
        State.exit(self, machine)

        gui_out1.value=False
        gui_out2.value=False
        redLED.value=False
        print("gui_out1 = ", gui_out1.value)
        print("gui_out2 = ", gui_out2.value)
        print("redLED = ", redLED.value)


    def pressed(self, machine):             # Former mechansm to change states, reserved for a power button

        #if switch_1.is_pressed:
            #machine.go_to_state('xx')
        #if switch_2.is_pressed:
            #machine.go_to_state('xx')
        pass


########################################
# The "Profile 1" state. Implement at a later date. Any button press in this state causes a transition to the "Home" state.
class EEIntern(State):

    # Declare global variables for the Profile1 state

    #Intitalize the global Profile1 variables

    def __init__(self):
        super().__init__()


    @property
    def name(self):
        return 'EEIntern'

    def enter(self, machine):
        State.enter(self, machine)

        print('#### EE Intern / Profile1 State ####')

        # customtkinter GUI for Profile1
        customtkinter.set_appearance_mode("light")     # Modes: system (default), light, dark
        customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
        win = customtkinter.CTk()                     # create CTk window like you do with the Tk window
        # Define the tkinter window instance
        win.title("EE Intern Profile")                                  # title for window
        win.geometry('320x240')                                         # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
        win.eval('tk::PlaceWindow . center')                            # Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
        #win.attributes('-fullscreen', True)                            # uncomment to use fullscreen
        # Window frame for the profile buttons
        win.frame = customtkinter.CTkFrame(master=win, width=320, height=180, corner_radius=8)
        win.frame.place(relx=0.5, rely=0.62, anchor=customtkinter.CENTER)

        def SW1ON():
            gui_out1.value=True                                         # Sets GPIO output
            print("gui_out1 = ", gui_out1.value)
            # Haptic placeholder
            # Sound placeholder
            t.sleep(0.1)
            win.quit()
            win.destroy()                                               # Closes GUI window
            machine.go_to_state('Timecard')

        def SW2ON():
            gui_out2.value=True                                         # Sets GPIO output
            print("gui_out2 = ", gui_out2.value)
            # Haptic placeholder
            # Sound placeholder
            t.sleep(0.1)
            win.quit()
            win.destroy()                                               # Closes GUI window
            machine.go_to_state('EEProject')

        # Profile1 tkinter Label
        Intern_label = customtkinter.StringVar(value="Engineering\n" + "Intern")
        label = customtkinter.CTkLabel(master=win, textvariable=Intern_label, width=120, height=25,
                                       fg_color=("white", "black"), corner_radius=4)
        label.place(relx=0.82, rely=0.07, anchor=customtkinter.CENTER)
        # Define the tkinter switch instances
        SW1Button = customtkinter.CTkButton(master=win, text="Timecard", command=SW1ON)
        SW1Button.place(relx=0.55, rely=0.8, anchor=customtkinter.W)
        SW2Button = customtkinter.CTkButton(master=win, text="Intern Project", command=SW2ON)
        SW2Button.place(relx=0.45, rely=0.8, anchor=customtkinter.E)
        # Start tkinter main GUI loop
        mainloop()  # commanding mainloop for starting main loop

        #t.sleep(0.5) # Slows down the transitions

    def exit(self, machine):
        State.exit(self, machine)

        gui_out1.value=False
        gui_out2.value=False
        print("gui_out1 = ", gui_out1.value)
        print("gui_out2 = ", gui_out2.value)

    def pressed(self, machine):             # Former mechansm to change states, reserved for a power button

        #if switch_1.is_pressed:
            #machine.go_to_state('xx')
        #if switch_2.is_pressed:
            #machine.go_to_state('xx')
        pass

########################################
# The "Task #1, Profile 1" state. Begin tracking task 1 in this state
class Timecard(State):

    # Declare global variables for the Task1, Profile1 state
    global stamp1                                                       # Determined that global class variables don't need to be declared in the local methods
    global time_zone_in, time_zone_out
    global timestamp_in, timestamp_out
    global delta_time

    # Intitalize the global variables within "Tracking2"
    time_zone_in = None                                                 # These are global variables to the "enter" method in the "Timecard" class
    timestamp_in = None
    time_zone_out = 0
    timestamp_out = 0
    delta_time = 0
    # Components of the "time in" stamp
    today = date.today()
    timestamp_in = datetime.now(tz=tz.tzlocal())
    time_zone_in = timestamp_in.tzname()    # Stores the timezone from datetime


    def __init__(self):
        super().__init__()


    @property
    def name(self):
        return 'Timecard'

    def enter(self, machine):
        State.enter(self, machine)
        print('#### EE Timecard / Task1 State ####')
        #Initialize variables for "enter", should these be global in the class?
        today = date.today()
        timestamp_in = datetime.now(tz=tz.tzlocal())

        # "time in" stamp
        print('Logging a START time to .csv file')
         # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
        with open("/home/pi/Desktop/ltb_f22_release/P1_t1.csv", "a") as f:

            redLED.value = True    # turn on LED to indicate writing entries
            print("Time zone 'in':",time_zone_in) #Prints data about to be written to the SD card
            print(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            f.write("%s," % (time_zone_in))    #
            f.write(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            redLED.value = False  # turn off LED to indicate we're done

        # customtkinter GUI for Profile1, Task1
        customtkinter.set_appearance_mode("light")  # Modes: system (default), light, dark
        customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, gree
        win = customtkinter.CTk()  # create CTk window like you do with the Tk window
        # Define the tkinter window instance
        win.title("EE Intern Timecard")  # title for window
        win.geometry('320x240')  # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
        win.eval('tk::PlaceWindow . center')  # Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
        # win.attributes('-fullscreen', True)                            # uncomment to use fullscreen
        # Window frame for the profile buttons
        win.frame = customtkinter.CTkFrame(master=win, width=320, height=180, corner_radius=8)
        win.frame.place(relx=0.5, rely=0.62, anchor=customtkinter.CENTER)

        def SW1ON():
            gui_out1.value=True                                              # Sets GPIO output for testing
            print("gui_out1 = ", gui_out1.value)
            # Components of the "time out" stamp
            timestamp_out = datetime.now(tz=tz.tzlocal())
            time_zone_out = timestamp_out.tzname()    # Stores the timezone from datetime
            delta_time = relativedelta(timestamp_out,timestamp_in)
            stamp = "Intern Timecard Logged: %d:%d:%02d" %(delta_time.hours,delta_time.minutes,delta_time.seconds)


            print('Logging a STOP time to .csv\n')
            # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
            with open("/home/pi/Desktop/ltb_f22_release/P1_t1.csv", "a") as f:
                redLED.value = True    # turn on LED to indicate writing entries
                print("Time zone 'out':",time_zone_out) #Prints data about to be written to the SD card
                print(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                print("The time tracked is:", str(delta_time.hours) + ":" + str(delta_time.minutes) + ":" + str(delta_time.seconds))
                print('\n') # Prints a blank line
                f.write("%s," % (time_zone_out))
                f.write(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                f.write("%d:%d:%02d\r\n" % (delta_time.hours,delta_time.minutes,delta_time.seconds))
                redLED.value = False  # turn off LED to indicate we're done

            # Flash a tnkinter label representing the time tracked
            trackLabel.config(text = stamp)                                 # "stamp1" value is retrieved from the global variable declared in the "enter" method
            print("stamp = ", stamp)
            win.update()
            t.sleep(4)                                                      # NOTE:  "time.sleep()" doesn't work well with tkinter windows. Instead try a tkinter "event loop"
            # Haptic placeholder
            # Sound placeholder

            win.quit()
            win.destroy()                                               # Closes GUI window
            machine.go_to_state('EEIntern')

        def SW2ON():
            gui_out2.value=True                                         # Sets GPIO output for testing
            print("gui_out2 = ", gui_out2.value)
            # Components of the "time out" stamp
            timestamp_out = datetime.now(tz=tz.tzlocal())
            time_zone_out = timestamp_out.tzname()    # Stores the timezone from datetime
            delta_time = relativedelta(timestamp_out,timestamp_in)
            stamp = "Intern Timecard Logged: %d:%d:%02d" %(delta_time.hours,delta_time.minutes,delta_time.seconds)


            print('Logging a STOP time to .csv\n')
            # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
            with open("/home/pi/Desktop/ltb_f22_release/P1_t1.csv", "a") as f:
                redLED.value = True    # turn on LED to indicate writing entries
                print("Time zone 'out':",time_zone_out) #Prints data about to be written to the SD card
                print(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                print("The time tracked is:", str(delta_time.hours) + ":" + str(delta_time.minutes) + ":" + str(delta_time.seconds))
                print('\n') # Prints a blank line
                f.write("%s," % (time_zone_out))
                f.write(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                f.write("%d:%d:%02d\r\n" % (delta_time.hours,delta_time.minutes,delta_time.seconds))
                redLED.value = False  # turn off LED to indicate we're done

            # Flash a tnkinter label representing the time tracked
            trackLabel.config(text = stamp)                                 # "stamp1" value is retrieved from the global variable declared in the "enter" method
            print("timestamp = ", stamp)
            win.update()
            t.sleep(4)                                                      # NOTE:  "time.sleep()" doesn't work well with tkinter windows. Instead try a tkinter "event loop"
            # Haptic placeholder
            # Sound placeholder

            win.quit()
            win.destroy()                                               # Closes GUI window
            machine.go_to_state('Home')

        # customtkinter Timecard Label
        p1t1label = customtkinter.StringVar(value="Timecard\n" + "-Tracking-")
        label = customtkinter.CTkLabel(master=win, textvariable=p1t1label, width=120, height=25,
                                       fg_color=("white", "black"), corner_radius=4)
        label.place(relx=0.82, rely=0.06, anchor=customtkinter.CENTER)
        # Tracked time Label
        trackLabel = Label(win, text="", foreground="black")
        trackLabel.pack(side=LEFT, anchor=CENTER)
        # Define the tkinter switch instances
        SW1Button = customtkinter.CTkButton(master=win, text="Stop", command=SW1ON)
        SW1Button.place(relx=0.55, rely=0.8, anchor=customtkinter.W)
        SW2Button = customtkinter.CTkButton(master=win, text="Home", command=SW2ON)
        SW2Button.place(relx=0.45, rely=0.8, anchor=customtkinter.E)
        # Start tkinter GUI main loop
        mainloop()  # commanding mainloop for starting main loop

        #t.sleep(0.5) # Slows down the transitions


    def exit(self, machine):
        State.exit(self, machine)

        gui_out1.value=False
        gui_out2.value=False
        redLED.value=False
        print("gui_out1 = ", gui_out1.value)
        print("gui_out2 = ", gui_out2.value)
        print("red LED = ", redLED.value)


    def pressed(self, machine):             # Former mechansm to change states, reserved for a power button

        #if switch_1.is_pressed:
            #machine.go_to_state('xx')
        #if switch_2.is_pressed:
            #machine.go_to_state('xx')
        pass

########################################
# The "Task #2, Profile 1" state. Begin tracking task 1 in this state
class EEProject(State):

    # Declare global variables for the Task2, Profile1 state
    global stamp1                                                       # Determined that global class variables don't need to be declared in the local methods
    global time_zone_in, time_zone_out
    global timestamp_in, timestamp_out
    global delta_time

    # Intitalize the global variables within Task2, Profile1
    time_zone_in = None                                                 # These are global variables to the "enter" method in the "Timecard" class
    timestamp_in = None
    time_zone_out = 0
    timestamp_out = 0
    delta_time = 0
    # Components of the "time in" stamp
    today = date.today()
    timestamp_in = datetime.now(tz=tz.tzlocal())
    time_zone_in = timestamp_in.tzname()                                # Stores the timezone from datetime


    def __init__(self):
        super().__init__()

    @property
    def name(self):
        return 'EEProject'

    def enter(self, machine):
        State.enter(self, machine)
        print('#### EE Intern Project / Task2 State ####')
        #Initialize variables for "enter", should these be global in the class?
        today = date.today()
        timestamp_in = datetime.now(tz=tz.tzlocal())

        # "time in" stamp
        print('Logging a START time to .csv file')
         # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
        with open("/home/pi/Desktop/ltb_f22_release/P1_t2.csv", "a") as f:

            redLED.value = True    # turn on LED to indicate writing entries
            print("Time zone 'in':",time_zone_in) #Prints data about to be written to the SD card
            print(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            f.write("%s," % (time_zone_in))    #
            f.write(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            redLED.value = False  # turn off LED to indicate we're done


        # customtkinter GUI for Profile1, Task2
        customtkinter.set_appearance_mode("light")  # Modes: system (default), light, dark
        customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, gree
        win = customtkinter.CTk()  # create CTk window like you do with the Tk window
        # Define the tkinter window instance
        win.title("EE Intern Project")  # title for window
        win.geometry('320x240')  # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
        win.eval('tk::PlaceWindow . center')  # Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
        # win.attributes('-fullscreen', True)                            # uncomment to use fullscreen
        # Window frame for the profile buttons
        win.frame = customtkinter.CTkFrame(master=win, width=320, height=180, corner_radius=8)
        win.frame.place(relx=0.5, rely=0.62, anchor=customtkinter.CENTER)

        # uncomment to use fullscreen

        def SW1ON():
            gui_out1.value=True                                              # Sets GPIO output for testing
            print("gui_out1 = ", gui_out1.value)
            # Components of the "time out" stamp
            timestamp_out = datetime.now(tz=tz.tzlocal())
            time_zone_out = timestamp_out.tzname()    # Stores the timezone from datetime
            delta_time = relativedelta(timestamp_out,timestamp_in)
            stamp = "EE Intern Project Logged: %d:%d:%02d" %(delta_time.hours,delta_time.minutes,delta_time.seconds)

            print('Logging a STOP time to .csv\n')
            # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
            with open("/home/pi/Desktop/ltb_f22_release/P1_t2.csv", "a") as f:
                redLED.value = True                                     # turn on LED to indicate writing entries
                print("Time zone 'out':",time_zone_out)                 # Prints data about to be written to the SD card
                print(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                print("The time tracked is:", str(delta_time.hours) + ":" + str(delta_time.minutes) + ":" + str(delta_time.seconds))
                print('\n') # Prints a blank line
                f.write("%s," % (time_zone_out))
                f.write(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                f.write("%d:%d:%02d\r\n" % (delta_time.hours,delta_time.minutes,delta_time.seconds))
                redLED.value = False  # turn off LED to indicate we're done

            # Flash a tnkinter label representing the time tracked
            trackLabel.config(text = stamp)                             # "stamp1" value is retrieved from the global variable declared in the "enter" method
            print("stamp = ", stamp)
            win.update()
            t.sleep(4)                                                  # NOTE:  "time.sleep()" doesn't work well with tkinter windows. Instead try a tkinter "event loop"
            # Haptic placeholder
            # Sound placeholder

            win.quit()
            win.destroy()                                               # Closes GUI window
            machine.go_to_state('EEIntern')

        def SW2ON():
            gui_out2.value=True                                         # Sets GPIO output for testing
            print("gui_out2 = ", gui_out2.value)
            # Components of the "time out" stamp
            timestamp_out = datetime.now(tz=tz.tzlocal())
            time_zone_out = timestamp_out.tzname()    # Stores the timezone from datetime
            delta_time = relativedelta(timestamp_out,timestamp_in)
            stamp = "EE Intern Project Logged: %d:%d:%02d" %(delta_time.hours,delta_time.minutes,delta_time.seconds)

            print('Logging a STOP time to .csv\n')
            # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
            with open("/home/pi/Desktop/ltb_f22_release/P1_t2.csv", "a") as f:
                redLED.value = True                                         # turn on LED to indicate writing entries
                print("Time zone 'out':",time_zone_out)                     # Prints data about to be written to the SD card
                print(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                print("The time tracked is:", str(delta_time.hours) + ":" + str(delta_time.minutes) + ":" + str(delta_time.seconds))
                print('\n')                                                 # Prints a blank line
                f.write("%s," % (time_zone_out))
                f.write(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                f.write("%d:%d:%02d\r\n" % (delta_time.hours,delta_time.minutes,delta_time.seconds))
                redLED.value = False                                        # turn off LED to indicate we're done

            # Flash a tnkinter label representing the time tracked
            trackLabel.config(text = stamp)                                 # "stamp1" value is retrieved from the global variable declared in the "enter" method
            print("timestamp = ", stamp)
            win.update()
            t.sleep(4)
            # Haptic placeholder
            # Sound placeholder
            t.sleep(0.1)
            win.quit()
            win.destroy()                                                    # Closes GUI window
            machine.go_to_state('Home')

        # tkinter Label
        p1t2label = customtkinter.StringVar(value="Intern Project\n" + "-Tracking-")
        label = customtkinter.CTkLabel(master=win, textvariable=p1t2label, width=120, height=25,
                                       fg_color=("white", "black"), corner_radius=4)
        label.place(relx=0.82, rely=0.07, anchor=customtkinter.CENTER)
        # Tracked time Label
        trackLabel = Label(win, text="", foreground="black")
        trackLabel.pack(side=LEFT, anchor=CENTER)
        # Define the tkinter switch instances
        SW1Button= customtkinter.CTkButton(master=win, text="Stop", command=SW1ON)
        SW1Button.place(relx=0.55, rely=0.8, anchor=customtkinter.W)
        SW2Button = customtkinter.CTkButton(master=win, text="Home", command=SW2ON)
        SW2Button.place(relx=0.45, rely=0.8, anchor=customtkinter.E)
        # Start tkinter GUI main loop
        mainloop()  # commanding mainloop for starting main loop

    def exit(self, machine):
        State.exit(self, machine)

        gui_out1.value=False
        gui_out2.value=False
        redLED.value=False
        print("gui_out1 = ", gui_out1.value)
        print("gui_out2 = ", gui_out2.value)
        print("red LED = ", redLED.value)

    def pressed(self, machine):             # Former mechansm to change states, reserved for a power button

        #if switch_1.is_pressed:
            #machine.go_to_state('xx')
        #if switch_2.is_pressed:
            #machine.go_to_state('xx')
        pass

#######################################
# The "Profile 2" state
class EEE193B(State):

    # Declare global variables for the Profile2 state

    #Intitalize the global Profile2 variables

    def __init__(self):
        super().__init__()


    @property
    def name(self):
        return 'EEE193B'

    def enter(self, machine):
        State.enter(self, machine)

        print('#### CSUS Senior Project / Profile2 State ####')

        # customtkinter Profile2 GUI
        customtkinter.set_appearance_mode("light")                       # Modes: system (default), light, dark
        customtkinter.set_default_color_theme("blue")                    # Themes: blue (default), dark-blue, green
        win = customtkinter.CTk()                                        # create CTk window like you do with the Tk window
        # Define the tkinter window instance
        win.title("193B Senior Project")                                 # title for window
        win.geometry('320x240')                                          # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
        win.eval('tk::PlaceWindow . center')                             # Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
        # win.attributes('-fullscreen', True)                            # uncomment to use fullscreen
        # Window frame for the profile buttons
        win.frame = customtkinter.CTkFrame(master=win, width=320, height=180, corner_radius=8)
        win.frame.place(relx=0.5, rely=0.62, anchor=customtkinter.CENTER)

        def SW1ON():
            gui_out1.value = True  # Sets GPIO output
            print("gui_out1 = ", gui_out1.value)
            # Haptic placeholder
            # Sound placeholder
            t.sleep(0.1)
            win.quit()
            win.destroy()  # Closes GUI window
            machine.go_to_state('Assignments')

        def SW2ON():
            gui_out2.value=True                                         # Sets GPIO output
            print("gui_out2 = ", gui_out2.value)
            # Haptic placeholder
            # Sound placeholder
            t.sleep(0.1)
            win.quit()
            win.destroy()                                               # Closes GUI window
            machine.go_to_state('Development')

        #customtkinter Label
        EEE193B_label = customtkinter.StringVar(value="Senior Project\n" + "193B\n" + "-Profile2-")
        label = customtkinter.CTkLabel(master=win, textvariable=EEE193B_label, width=120, height=50,
                                   fg_color=("white", "black"), corner_radius=4)
        label.place(relx=0.82, rely=0.099, anchor=customtkinter.CENTER)
        # Define the customtkinter switch instances
        SW1Button = customtkinter.CTkButton(master=win, text="Assignments", command=SW1ON)
        SW1Button.place(relx=0.55, rely=0.8, anchor=customtkinter.W)
        SW2Button = customtkinter.CTkButton(master=win, text="Development", command=SW2ON)
        SW2Button.place(relx=0.45, rely=0.8, anchor=customtkinter.E)
        # Start tkinter main GUI loop
        mainloop()  # commanding mainloop for starting main loop


    def exit(self, machine):
        State.exit(self, machine)

        gui_out1.value=False
        gui_out2.value=False
        redLED.value=False
        print("gui_out1 = ", gui_out1.value)
        print("gui_out2 = ", gui_out2.value)
        print("red LED = ", redLED.value)

    def pressed(self, machine):             # Former mechansm to change states, reserved for a power button

        #if switch_1.is_pressed:
            #machine.go_to_state('xx')
        #if switch_2.is_pressed:
            #machine.go_to_state('xx')
        pass

########################################
# The "Task #1, Profile 2" state. Begin tracking the time for Assignments when entering this state
class Assignments(State):

    # Declare global variables for the Task1, Profile2 state
    global stamp1                                                       # Determined that global class variables don't need to be declared in the local methods
    global time_zone_in, time_zone_out
    global timestamp_in, timestamp_out
    global delta_time

    # Intitalize the global variables within Task1, Profile2
    time_zone_in = None                                                 # These are global variables to the "enter" method in the "Timecard" class
    timestamp_in = None
    time_zone_out = 0
    timestamp_out = 0
    delta_time = 0
    # Components of the "time in" stamp
    today = date.today()
    timestamp_in = datetime.now(tz=tz.tzlocal())
    time_zone_in = timestamp_in.tzname()                                # Stores the timezone from datetime


    def __init__(self):
        super().__init__()

    @property
    def name(self):
        return 'Assignments'

    def enter(self, machine):
        State.enter(self, machine)
        print('#### EEE-193B Assignments / Task1 State ####')

        #Initialize variables for "enter", should these be global in the class?
        today = date.today()
        timestamp_in = datetime.now(tz=tz.tzlocal())

        # "time in" stamp
        print('Logging a START time to .csv file')
         # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
        with open("/home/pi/Desktop/ltb_f22_release/P2_t1.csv", "a") as f:

            redLED.value = True                                          # turn on LED to indicate writing entries
            print("Time zone 'in':",time_zone_in)                        #Prints data about to be written to the SD card
            print(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            f.write("%s," % (time_zone_in))    #
            f.write(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            redLED.value = False                                         # turn off LED to indicate we're done

        # customtkinter Home Screen GUI
        customtkinter.set_appearance_mode("light")                       # Modes: system (default), light, dark
        customtkinter.set_default_color_theme("blue")                    # Themes: blue (default), dark-blue, green
        win = customtkinter.CTk()                                        # create CTk window like you do with the Tk window
        # Define the tkinter window instance
        win.title("193B Assignments")                                    # title for window
        win.geometry('320x240')                                          # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
        win.eval('tk::PlaceWindow . center')                             # Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
        # win.attributes('-fullscreen', True)                            # uncomment to use fullscreen
        # Window frame for the profile buttons
        win.frame = customtkinter.CTkFrame(master=win, width=320, height=180, corner_radius=8)
        win.frame.place(relx=0.5, rely=0.62, anchor=customtkinter.CENTER)

        def SW1ON():
            gui_out1.value=True                                          # Sets GPIO output for testing
            print("gui_out1 = ", gui_out1.value)
            # Components of the "time out" stamp
            timestamp_out = datetime.now(tz=tz.tzlocal())
            time_zone_out = timestamp_out.tzname()                       # Stores the timezone from datetime
            delta_time = relativedelta(timestamp_out,timestamp_in)
            stamp = "193B Assignments Logged: %d:%d:%02d" %(delta_time.hours,delta_time.minutes,delta_time.seconds)

            print('Logging a STOP time to .csv\n')
            # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
            with open("/home/pi/Desktop/ltb_f22_release/P2_t1.csv", "a") as f:
                redLED.value = True                                     # turn on LED to indicate writing entries
                print("Time zone 'out':",time_zone_out)                 # Prints data about to be written to the SD card
                print(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                print("The time tracked is:", str(delta_time.hours) + ":" + str(delta_time.minutes) + ":" + str(delta_time.seconds))
                print('\n') # Prints a blank line
                f.write("%s," % (time_zone_out))
                f.write(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                f.write("%d:%d:%02d\r\n" % (delta_time.hours,delta_time.minutes,delta_time.seconds))
                redLED.value = False  # turn off LED to indicate we're done

            # Flash a tnkinter label representing the time tracked
            trackLabel.config(text = stamp)                             # "stamp1" value is retrieved from the global variable declared in the "enter" method
            print("stamp = ", stamp)
            win.update()
            t.sleep(4)                                                  # NOTE:  "time.sleep()" doesn't work well with tkinter windows. Instead try a tkinter "event loop"
            # Haptic placeholder
            # Sound placeholder

            win.quit()
            win.destroy()                                               # Closes GUI window
            machine.go_to_state('EEE193B')

        def SW2ON():
            gui_out2.value=True                                         # Sets GPIO output for testing
            print("gui_out2 = ", gui_out2.value)
            # Components of the "time out" stamp
            timestamp_out = datetime.now(tz=tz.tzlocal())
            time_zone_out = timestamp_out.tzname()                      # Stores the timezone from datetime
            delta_time = relativedelta(timestamp_out,timestamp_in)
            stamp = "EEE193B Assignmets Logged: %d:%d:%02d" %(delta_time.hours,delta_time.minutes,delta_time.seconds)


            print('Logging a STOP time to .csv\n')
            # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
            with open("/home/pi/Desktop/ltb_f22_release/P2_t1.csv", "a") as f:
                redLED.value = True                                     # turn on LED to indicate writing entries
                print("Time zone 'out':",time_zone_out)                 #Prints data about to be written to the SD card
                print(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                print("The time tracked is:", str(delta_time.hours) + ":" + str(delta_time.minutes) + ":" + str(delta_time.seconds))
                print('\n') # Prints a blank line
                f.write("%s," % (time_zone_out))
                f.write(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                f.write("%d:%d:%02d\r\n" % (delta_time.hours,delta_time.minutes,delta_time.seconds))
                redLED.value = False  # turn off LED to indicate we're done

            # Flash a tnkinter label representing the time tracked
            trackLabel.config(text = stamp)                             # "stamp1" value is retrieved from the global variable declared in the "enter" method
            print("timestamp = ", stamp)
            win.update()
            t.sleep(4)
            # Haptic placeholder
            # Sound placeholder
            t.sleep(0.1)
            win.quit()
            win.destroy()                                               # Closes GUI window
            machine.go_to_state('Home')

        # Profile2 customtkinter Label
        p2t1label = customtkinter.StringVar(value="Senior Project\n" + "Assignment\n" + "-Tracking-")
        label = customtkinter.CTkLabel(master=win, textvariable=p2t1label, width=120, height=50,
                                       fg_color=("white", "black"), corner_radius=4)
        label.place(relx=0.82, rely=0.109, anchor=customtkinter.CENTER)
        # Tracked time Label
        trackLabel = Label(win, text="", foreground="black")
        trackLabel.pack(side=LEFT, anchor=CENTER)        # Define the tkinter switch instances
        SW1Button = customtkinter.CTkButton(master=win, text="Stop", command=SW1ON)
        SW1Button.place(relx=0.55, rely=0.8, anchor=customtkinter.W)
        SW2Button = customtkinter.CTkButton(master=win, text="Home", command=SW2ON)
        SW2Button.place(relx=0.45, rely=0.8, anchor=customtkinter.E)
        # Start tkinter GUI main loop
        mainloop()  # commanding mainloop for starting main loop

    def exit(self, machine):
        State.exit(self, machine)

        gui_out1.value=False
        gui_out2.value=False
        redLED.value=False
        print("gui_out1 = ", gui_out1.value)
        print("gui_out2 = ", gui_out2.value)
        print("red LED = ", redLED.value)

    def pressed(self, machine):             # Former mechansm to change states, reserved for a power button

        #if switch_1.is_pressed:
            #machine.go_to_state('xx')
        #if switch_2.is_pressed:
            #machine.go_to_state('xx')
        pass

########################################
# The "Task #2, Profile 2" state. Begin tracking the time for Developmet upon entering this state
class Development(State):

    # Declare global variables for the Task2, Profile2 state
    global stamp1                                                       # Determined that global class variables don't need to be declared in the local methods
    global time_zone_in, time_zone_out
    global timestamp_in, timestamp_out
    global delta_time

    # Intitalize the global variables within Task2, Profile2
    time_zone_in = None                                                 # These are global variables to the "enter" method in the "Timecard" class
    timestamp_in = None
    time_zone_out = 0
    timestamp_out = 0
    delta_time = 0
    # Components of the "time in" stamp
    today = date.today()
    timestamp_in = datetime.now(tz=tz.tzlocal())
    time_zone_in = timestamp_in.tzname()                                # Stores the timezone from datetime


    def __init__(self):
        super().__init__()

    @property
    def name(self):
        return 'Development'

    def enter(self, machine):
        State.enter(self, machine)
        print('#### Senior Design Development / Task2 State ####')

        #Initialize variables for "enter", should these be global in the class?
        today = date.today()
        timestamp_in = datetime.now(tz=tz.tzlocal())

        # "time in" stamp
        print('Logging a START time to .csv file')
        # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
        with open("/home/pi/Desktop/ltb_f22_release/P2_t2.csv", "a") as f:

            redLED.value = True                                     # turn on LED to indicate writing entries
            print("Time zone 'in':",time_zone_in)                   #Prints data about to be written to the SD card
            print(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            f.write("%s," % (time_zone_in))    #
            f.write(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            redLED.value = False                                # turn off LED to indicate we're done

        # customtkinter Home Screen GUI
        customtkinter.set_appearance_mode("light")              # Modes: system (default), light, dark
        customtkinter.set_default_color_theme("blue")           # Themes: blue (default), dark-blue, green
        win = customtkinter.CTk()                               # create CTk window like you do with the Tk window
        # Define the tkinter window instance
        win.title("193B Project Development")                   # title for window
        win.geometry('320x240')                                 # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
        win.eval('tk::PlaceWindow . center')                    # Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
        # win.attributes('-fullscreen', True)                   # uncomment to use fullscreen
        # Window frame for the profile buttons
        win.frame = customtkinter.CTkFrame(master=win, width=320, height=180, corner_radius=8)
        win.frame.place(relx=0.5, rely=0.62, anchor=customtkinter.CENTER)


        def SW1ON():
            gui_out1.value=True                                              # Sets GPIO output for testing
            print("gui_out1 = ", gui_out1.value)
            # Components of the "time out" stamp
            timestamp_out = datetime.now(tz=tz.tzlocal())
            time_zone_out = timestamp_out.tzname()    # Stores the timezone from datetime
            delta_time = relativedelta(timestamp_out,timestamp_in)
            stamp = "EEE193B Development Logged: %d:%d:%02d" %(delta_time.hours,delta_time.minutes,delta_time.seconds)

            print('Logging a STOP time to .csv\n')
            # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
            with open("/home/pi/Desktop/ltb_f22_release/P2_t2.csv", "a") as f:
                redLED.value = True    # turn on LED to indicate writing entries
                print("Time zone 'out':",time_zone_out) #Prints data about to be written to the SD card
                print(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                print("The time tracked is:", str(delta_time.hours) + ":" + str(delta_time.minutes) + ":" + str(delta_time.seconds))
                print('\n') # Prints a blank line
                f.write("%s," % (time_zone_out))
                f.write(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                f.write("%d:%d:%02d\r\n" % (delta_time.hours,delta_time.minutes,delta_time.seconds))
                redLED.value = False  # turn off LED to indicate we're done

            # Flash a tnkinter label representing the time tracked
            trackLabel.config(text = stamp)                             # "stamp1" value is retrieved from the global variable declared in the "enter" method
            print("stamp = ", stamp)
            win.update()
            t.sleep(4)                                                  # NOTE:  "time.sleep()" doesn't work well with tkinter windows. Instead try a tkinter "event loop"
            # Haptic placeholder
            # Sound placeholder

            win.quit()
            win.destroy()                                               # Closes GUI window
            machine.go_to_state('EEE193B')

        def SW2ON():
            gui_out2.value=True                                         # Sets GPIO output for testing
            print("gui_out2 = ", gui_out2.value)
            # Components of the "time out" stamp
            timestamp_out = datetime.now(tz=tz.tzlocal())
            time_zone_out = timestamp_out.tzname()    # Stores the timezone from datetime
            delta_time = relativedelta(timestamp_out,timestamp_in)
            stamp = "EEE193B Development Logged: %d:%d:%02d" %(delta_time.hours,delta_time.minutes,delta_time.seconds)


            print('Logging a STOP time to .csv\n')
            # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
            with open("/home/pi/Desktop/ltb_f22_release/P2_t2.csv", "a") as f:
                redLED.value = True    # turn on LED to indicate writing entries
                print("Time zone 'out':",time_zone_out) #Prints data about to be written to the SD card
                print(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                print("The time tracked is:", str(delta_time.hours) + ":" + str(delta_time.minutes) + ":" + str(delta_time.seconds))
                print('\n') # Prints a blank line
                f.write("%s," % (time_zone_out))
                f.write(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                f.write("%d:%d:%02d\r\n" % (delta_time.hours,delta_time.minutes,delta_time.seconds))
                redLED.value = False  # turn off LED to indicate we're done

            # Flash a tnkinter label representing the time tracked
            trackLabel.config(text = stamp)                             # "stamp1" value is retrieved from the global variable declared in the "enter" method
            print("timestamp = ", stamp)
            win.update()
            t.sleep(4)
            # Haptic placeholder
            # Sound placeholder
            t.sleep(0.1)
            win.quit()
            win.destroy()                                               # Closes GUI window
            machine.go_to_state('Home')

        # Profile2 Task2 customtkinter Label
        p2t2label = customtkinter.StringVar(value="Senior Project\n" + "Development\n" + "-Tracking-")
        label = customtkinter.CTkLabel(master=win, textvariable=p2t2label, width=120, height=25,
                                       fg_color=("white", "black"), corner_radius=4)
        label.place(relx=0.82, rely=0.109, anchor=customtkinter.CENTER)
        # Tracked time Label
        trackLabel = Label(win, text="", foreground="black")
        trackLabel.pack(side=LEFT, anchor=CENTER)
        # Define the tkinter switch instances
        SW1Button = customtkinter.CTkButton(master=win, text="Stop", command=SW1ON)
        SW1Button.place(relx=0.55, rely=0.8, anchor=customtkinter.W)
        SW2Button = customtkinter.CTkButton(master=win, text="Home", command=SW2ON)
        SW2Button.place(relx=0.45, rely=0.8, anchor=customtkinter.E)
        # Start tkinter GUI main loop
        mainloop()  # commanding mainloop for starting main loop

    def exit(self, machine):
        State.exit(self, machine)

        gui_out1.value=False
        gui_out2.value=False
        redLED.value=False
        print("gui_out1 = ", gui_out1.value)
        print("gui_out2 = ", gui_out2.value)
        print("red LED = ", redLED.value)

    def pressed(self, machine):                          # Former mechansm to change states, reserved for a power button

        #if switch_1.is_pressed:
            #machine.go_to_state('xx')
        #if switch_2.is_pressed:
            #machine.go_to_state('xx')
        pass

################################################################################
# Create the state machine
LTB_state_machine = StateMachine()                                      # Defines the state machine
LTB_state_machine.add_state(Home())                                     # Adds the listed states to the machine (Except for the class, "State"
LTB_state_machine.add_state(FocusTimer())
LTB_state_machine.add_state(EEIntern())
LTB_state_machine.add_state(Timecard())
LTB_state_machine.add_state(EEProject())
LTB_state_machine.add_state(EEE193B())
LTB_state_machine.add_state(Assignments())
LTB_state_machine.add_state(Development())

LTB_state_machine.go_to_state('Home')                                   #Starts the state machine in the "Home" state

while True:
    pass
    #switch_1.value                                                      #Checks the switch 1 state each time the loop executes, necessary for hardware button state changes
    #switch_2.value                                                      #Checks the switch 1 state each time the loop executes, necessary for hardware button state changes
    #LTB_state_machine.pressed()                                         #Transitions to the StateMachine attrubute, "pressed"
