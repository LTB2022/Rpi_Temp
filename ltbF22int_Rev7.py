# Little Time Buddy-Integration with Capacitive TFT Screen-Release Code Rev. 6
# 2022-10-22
# CSheeran
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
import time
import sys
import RPi.GPIO as GPIO

import busio
import adafruit_drv2605
import board
###############################################################################

# Set to false to disable testing/tracing code
TESTING = True

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

######################################################################################
# Haptic Feedback Pins
b = gpiozero.Buzzer(12)
i2c = busio.I2C(board.SCL, board.SDA)
drv = adafruit_drv2605.DRV2605(i2c)
drv.sequence[0] = adafruit_drv2605.Effect(47)

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

def ViBu_LTB(choice):# function to call the buzzer and vibration motor. This called from the class StateMachine/function go_to_state
    b.on()
    drv.play()
    t.sleep(.1)
    b.off()
    drv.stop()

################################################################################
# State Machine, Manages states

class StateMachine():                         # Question: Why is the argument named "object?"

    def __init__(self):                             # Needed constructor
        self.state = None
        self.states = {}


    def add_state(self, state):                     # "add state" attribute, adds states to the machine
        self.states[state.name] = state

    def go_to_state(self, state_name):              # "go to state" attribute, facilittes transition to other states. Prints confirmation when "Testing = True"
        #----this activates the buzzer and vibration motor everytime the program changes states
        ViBu_LTB(state_name)
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
        win = Tk()  # setting up window from Tk() naming win
        myFont = font.Font(family='Helvetica', size=18)  # setting up font naming myfont
        labelFont = font.Font(family='Helvetica', size=20, weight='bold')  # setting up font naming myfont
        # Define the tkinter window instance
        win.title("ltb Home")                                           # title for window
        win.geometry('400x300')                                         # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
        win.eval('tk::PlaceWindow . center')                            # Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
        #win.attributes('-fullscreen', True)                            # uncomment to use fullscreen


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
            clock.config(text= time_Var)
            date.config(text= date_Var)
            clock.after(200, get_time)

        # Home Label
        homeLabel = Label(win, text="Little Time Buddy - Home", foreground="black", font=labelFont)
        homeLabel.pack(side=TOP, anchor=N)
        # Define the tkinter switch instances
        SW1Button = Button(win, text="EE Intern", font=myFont, command=SW1ON, height=2, width=8)  # setting button naming led1Button
        SW1Button.pack(side=LEFT, anchor=W)
        SW2Button = Button(win, text="CSUS 193B", font=myFont, command=SW2ON, height=2, width=8)  # setting button naming led2Button
        SW2Button.pack(side=RIGHT, anchor=E)
        # Focus Button
        Fbtn = Button(win, text="Focus",font= myFont, command=focusON, height=2, width=8)
        Fbtn.pack(side=BOTTOM, anchor=S)
        # Display Parameters for the Clock
        clock = Label(win, font= ("Calibri",10), bg="white", fg="black")
        clock.pack(side=BOTTOM, anchor=SE)
        clkText= Label(text="Time:",font= ("Calibri",10), bg="white", fg="black")
        clkText.pack(side=BOTTOM, anchor=SE)
        # Display Parameters for the Date
        date = Label(win, font= ("Calibri",10), bg="white", fg="black")
        date.pack(side=BOTTOM, anchor=SW)
        dteText= Label(text="Date:",font= ("Calibri",10), bg="white", fg="black")
        dteText.pack(side=BOTTOM, anchor=SW)
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

        # tkinter Home Screen GUI
        win = Tk()  # setting up window from Tk() naming win
        myFont = font.Font(family='Helvetica', size=18)  # setting up font naming myfont
        labelFont = font.Font(family='Helvetica', size=20, weight='bold')  # setting up font naming myfont
        # Define the tkinter window instance
        win.title("Focus Timer")                                           # title for window
        win.geometry('400x300')                                         # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
        win.eval('tk::PlaceWindow . center')                            # Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
        #win.attributes('-fullscreen', True)                            # uncomment to use fullscreen


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

        # Focus Timer tkinter Label
        focusLabel = Label(win, text="Focus Timer", foreground="black", font=labelFont)
        focusLabel.pack(side=TOP, anchor=N)
        # Define the tkinter switch instances
        SW1Button = Button(win, text="Start", font=myFont, command=SW1ON, height=2, width=8)  # setting button naming led1Button
        SW1Button.pack(side=LEFT, anchor=W)
        SW2Button = Button(win, text="Stop", font=myFont, command=SW2ON, height=2, width=8)  # setting button naming led2Button
        SW2Button.pack(side=RIGHT, anchor=E)
        SW3Button = Button(win, text=" Exit", font=myFont, command=SW3ON, height=2, width=8)  # setting button naming led2Button
        SW3Button.pack(side=BOTTOM, anchor=E)

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

        # tkinter Home Screen GUI
        win = Tk()  # setting up window from Tk() naming win
        myFont = font.Font(family='Helvetica', size=18)  # setting up font naming myfont
        labelFont = font.Font(family='Helvetica', size=20, weight='bold')  # setting up font naming myfont
        # Define the tkinter window instance
        win.title("EE Intern Profile")                                     # title for window
        win.geometry('400x300')                                         # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
        win.eval('tk::PlaceWindow . center')                            # Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
        #win.attributes('-fullscreen', True)                            # uncomment to use fullscreen


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
        profile1Label = Label(win, text="Engineering Intern Profile", foreground="black", font=labelFont)
        profile1Label.pack(side=TOP, anchor=N)
        # Define the tkinter switch instances
        SW1Button = Button(win, text="Timecard", font=myFont, command=SW1ON, height=2, width=8)  # setting button naming led1Button
        SW1Button.pack(side=LEFT, anchor=W)
        SW2Button = Button(win, text="Intern Project", font=myFont, command=SW2ON, height=2, width=11)  # setting button naming led2Button
        SW2Button.pack(side=RIGHT, anchor=E)
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

        # tkinter Home Screen GUI
        win = Tk()  # setting up window from Tk() naming win
        myFont = font.Font(family='Helvetica', size=18)                      # setting up font named myfont
        labelFont = font.Font(family='Helvetica', size=20, weight='bold')    # setting up font for the Label widget
        # Define the tkinter window instance
        win.title("Intern Timecard")                                         # title for window
        win.geometry('400x300')                                              # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
        win.eval('tk::PlaceWindow . center')                                 # Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
        #win.attributes('-fullscreen', True)                                 # uncomment to use fullscreen

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

        # tkinter Label
        p1t1Label = Label(win, text="Tracking Timecard", foreground="black", font=labelFont)
        p1t1Label.pack(side=TOP, anchor=N)
        # Tracked time Label
        trackLabel = Label(win, text="", foreground="black", font=myFont)
        trackLabel.pack(side=TOP, anchor=N)
        # Define the tkinter switch instances
        SW1Button = Button(win, text="Stop", font=myFont, command=SW1ON, height=2, width=8)  # setting button naming led1Button
        SW1Button.pack(side=LEFT, anchor=W)
        SW2Button = Button(win, text="Home", font=myFont, command=SW2ON, height=2, width=8)  # setting button naming led2Button
        SW2Button.pack(side=RIGHT, anchor=E)
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

        # tkinter Home Screen GUI
        win = Tk()  # setting up window from Tk() naming win
        myFont = font.Font(family='Helvetica', size=18)                      # setting up font naming myfont
        labelFont = font.Font(family='Helvetica', size=20, weight='bold')  # setting up font naming myfont
        # Define the tkinter window instance
        win.title("Intern Project")                                                            # title for window
        win.geometry('400x300')                                                             # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
        win.eval('tk::PlaceWindow . center')                                                # Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
        #win.attributes('-fullscreen', True)                                                # uncomment to use fullscreen

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
            stamp = "EE Intern Project Logged: %d:%d:%02d" %(delta_time.hours,delta_time.minutes,delta_time.seconds)

            print('Logging a STOP time to .csv\n')
            # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
            with open("/home/pi/Desktop/ltb_f22_release/P1_t2.csv", "a") as f:
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
            t.sleep(4)
            # Haptic placeholder
            # Sound placeholder
            t.sleep(0.1)
            win.quit()
            win.destroy()                                               # Closes GUI window
            machine.go_to_state('Home')

        # tkinter Label
        p1t2Label = Label(win, text="Intern Project Tracking", foreground="black", font=labelFont)
        p1t2Label.pack(side=TOP, anchor=N)
        # Tracked time Label
        trackLabel = Label(win, text="", foreground="black", font=myFont)
        trackLabel.pack(side=TOP, anchor=N)
        # Define the tkinter switch instances
        SW1Button = Button(win, text="Stop", font=myFont, command=SW1ON, height=2, width=8)  # setting button naming led1Button
        SW1Button.pack(side=LEFT, anchor=W)
        SW2Button = Button(win, text="H", font=myFont, command=SW2ON, height=2, width=8)  # setting button naming led2Button
        SW2Button.pack(side=RIGHT, anchor=E)
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

        # tkinter Home Screen GUI
        win = Tk()  # setting up window from Tk() naming win
        myFont = font.Font(family='Helvetica', size=18)  # setting up font naming myfont
        labelFont = font.Font(family='Helvetica', size=20, weight='bold')  # setting up font naming myfont
        # Define the tkinter window instance
        win.title("CSUS Senior Project Profile")                        # title for window
        win.geometry('400x300')                                         # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
        win.eval('tk::PlaceWindow . center')                            # Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
        #win.attributes('-fullscreen', True)                            # uncomment to use fullscreen


        def SW1ON():
            gui_out1.value=True                                         # Sets GPIO output
            print("gui_out1 = ", gui_out1.value)
            # Haptic placeholder
            # Sound placeholder
            t.sleep(0.1)
            win.quit()
            win.destroy()                                               # Closes GUI window
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

        # tkinter Label
        p1t2Label = Label(win, text="Senior Project Profile", foreground="black", font=labelFont)
        p1t2Label.pack(side=TOP, anchor=N)
        # Define the tkinter switch instances
        SW1Button = Button(win, text="Assignments", font=myFont, command=SW1ON, height=2, width=8)  # setting button naming led1Button
        SW1Button.pack(side=LEFT, anchor=W)
        SW2Button = Button(win, text="Development", font=myFont, command=SW2ON, height=2, width=11)  # setting button naming led2Button
        SW2Button.pack(side=RIGHT, anchor=E)
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

            redLED.value = True    # turn on LED to indicate writing entries
            print("Time zone 'in':",time_zone_in) #Prints data about to be written to the SD card
            print(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            f.write("%s," % (time_zone_in))    #
            f.write(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            redLED.value = False  # turn off LED to indicate we're done

        # tkinter Home Screen GUI
        win = Tk()  # setting up window from Tk() naming win
        myFont = font.Font(family='Helvetica', size=18)                      # setting up font naming myfont
        labelFont = font.Font(family='Helvetica', size=20, weight='bold')  # setting up font naming myfont
        # Define the tkinter window instance
        win.title("EEE-193B Assignments")                                                            # title for window
        win.geometry('400x300')                                                             # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
        win.eval('tk::PlaceWindow . center')                                                # Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
        #win.attributes('-fullscreen', True)                                                # uncomment to use fullscreen


        def SW1ON():
            gui_out1.value=True                                              # Sets GPIO output for testing
            print("gui_out1 = ", gui_out1.value)
            # Components of the "time out" stamp
            timestamp_out = datetime.now(tz=tz.tzlocal())
            time_zone_out = timestamp_out.tzname()    # Stores the timezone from datetime
            delta_time = relativedelta(timestamp_out,timestamp_in)
            stamp = "193B Assignments Logged: %d:%d:%02d" %(delta_time.hours,delta_time.minutes,delta_time.seconds)

            print('Logging a STOP time to .csv\n')
            # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
            with open("/home/pi/Desktop/ltb_f22_release/P2_t1.csv", "a") as f:
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
            machine.go_to_state('EEE193B')

        def SW2ON():
            gui_out2.value=True                                         # Sets GPIO output for testing
            print("gui_out2 = ", gui_out2.value)
            # Components of the "time out" stamp
            timestamp_out = datetime.now(tz=tz.tzlocal())
            time_zone_out = timestamp_out.tzname()    # Stores the timezone from datetime
            delta_time = relativedelta(timestamp_out,timestamp_in)
            stamp = "EEE193B Assignmets Logged: %d:%d:%02d" %(delta_time.hours,delta_time.minutes,delta_time.seconds)


            print('Logging a STOP time to .csv\n')
            # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
            with open("/home/pi/Desktop/ltb_f22_release/P2_t1.csv", "a") as f:
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
            t.sleep(4)
            # Haptic placeholder
            # Sound placeholder
            t.sleep(0.1)
            win.quit()
            win.destroy()                                               # Closes GUI window
            machine.go_to_state('Home')

        # Profile1 tkinter Label
        p2t1Label = Label(win, text="Senior Project Assignments", foreground="black", font=labelFont)
        p2t1Label.pack(side=TOP, anchor=N)
        # Tracked time Label
        trackLabel = Label(win, text="", foreground="black", font=myFont)
        trackLabel.pack(side=TOP, anchor=N)
        # Define the tkinter switch instances
        SW1Button = Button(win, text="Stop", font=myFont, command=SW1ON, height=2, width=8)  # setting button naming led1Button
        SW1Button.pack(side=LEFT, anchor=W)
        SW2Button = Button(win, text="Home", font=myFont, command=SW2ON, height=2, width=8)  # setting button naming led2Button
        SW2Button.pack(side=RIGHT, anchor=E)
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

            redLED.value = True    # turn on LED to indicate writing entries
            print("Time zone 'in':",time_zone_in) #Prints data about to be written to the SD card
            print(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            f.write("%s," % (time_zone_in))    #
            f.write(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            redLED.value = False  # turn off LED to indicate we're done

        # tkinter Home Screen GUI
        win = Tk()  # setting up window from Tk() naming win
        myFont = font.Font(family='Helvetica', size=18)                      # setting up font naming myfont
        labelFont = font.Font(family='Helvetica', size=20, weight='bold')  # setting up font naming myfont
        # Define the tkinter window instance
        win.title("EEE-193B Development")                                                            # title for window
        win.geometry('400x300')                                                             # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
        win.eval('tk::PlaceWindow . center')                                                # Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
        #win.attributes('-fullscreen', True)                                                # uncomment to use fullscreen

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
            trackLabel.config(text = stamp)                                 # "stamp1" value is retrieved from the global variable declared in the "enter" method
            print("stamp = ", stamp)
            win.update()
            t.sleep(4)                                                      # NOTE:  "time.sleep()" doesn't work well with tkinter windows. Instead try a tkinter "event loop"
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
            trackLabel.config(text = stamp)                                 # "stamp1" value is retrieved from the global variable declared in the "enter" method
            print("timestamp = ", stamp)
            win.update()
            t.sleep(4)
            # Haptic placeholder
            # Sound placeholder
            t.sleep(0.1)
            win.quit()
            win.destroy()                                               # Closes GUI window
            machine.go_to_state('Home')

        # Profile1 tkinter Label
        p2t2Label = Label(win, text="Senior Project Development", foreground="black", font=labelFont)
        p2t2Label.pack(side=TOP, anchor=N)
        # Tracked time Label
        trackLabel = Label(win, text="", foreground="black", font=myFont)
        trackLabel.pack(side=TOP, anchor=N)
        # Define the tkinter switch instances
        SW1Button = Button(win, text="Stop", font=myFont, command=SW1ON, height=2, width=8)  # setting button naming led1Button
        SW1Button.pack(side=LEFT, anchor=W)
        SW2Button = Button(win, text="Home", font=myFont, command=SW2ON, height=2, width=8)  # setting button naming led2Button
        SW2Button.pack(side=RIGHT, anchor=E)
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