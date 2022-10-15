# Little Time Buddy-Integration with Capacitive TFT Screen-Release Code Rev. 4
# 2022-10-09
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
gui_out2 = gpiozero.DigitalOutputDevice(24, active_high=True, initial_value=False)  # GUI button 2 is o the right side of the screen, DEMO yellow wire
recordLED = gpiozero.DigitalOutputDevice(36, active_high=True, initial_value=False)  # illuinate a red LED to indicate the timestamp operation

#################################################################################################
# Setting up the Real Time Clock and set the initial time

# Creates object I2C that connects the I2C module to pins SCL and SDA
#myI2C = busio.I2C(board.SCL, board.SDA)
# Creates an object that can access the RTC and communicate that information along using I2C.
#rtc = adafruit_pcf8523.PCF8523(myI2C)

################################################################################
#Python datetime function
now = datetime.now(tz=tz.tzlocal())    #Use the actual time set in the Pi
print("Current device time:", now)     # uncomment for debugging
print('\n')


################################################################################
# Creates a file and writes name inside a text file along the path.
#with open("/home/pi/Desktop/Python_ltb/stamp.csv", "a") as f:
    #f.write("Date, Time In, Time Out , Total, Voice Note\r\n")
#print("Logging column names into the filesystem\n")

################################################################################
# Support functions

# Code tracing feature located in the "pressed" method of the "StateMachine" Class
def log(s):
    """Print the argument if testing/tracing is enabled."""
    if TESTING:
        print(s)

################################################################################
# Global Variables

# Profile and Task Names created by user in the desktop application
# Import these from a .csv file
# Assign each of these to the class GUI Labels and buttons

#HomeName=userHome
#P1Name=userP1
#P1t1Name=userP1t1
#P1t21Name=userP1t1
#P2Name=userP2
#P2t1Name=userP2t1
#P2t2Name=userP2t2


################################################################################
# State Machine, Manages states

class StateMachine(object):                         # Question: Why is the argument named "object?"

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

# Abstract parent state class: I'm not 100% sure that this state is the "parent class" for the states below.
# So far "StateMachine" appears to be the parent class
# some clarification is needed to indentify how a class is called by "super().__init__()" (aka "Inheritance") & @property

class State(object):


    def __init__(self):         # Constructor. Sets variables for the class, in this instance only, "self". Note machine variable below in the "enter" attribute

        @property
        def name(self):             # Attribute. Only the name is returned in states below. The State object shouldn't be called and returns nothing
            return ''

    def enter(self, machine):   # Class Attribute. Does what is commanded when the state is entered
        pass

    def exit(self, machine):    # Class Attribute. Does what is commanded when exiting the state
        pass

    def pressed(self, machine): # Class Attribute. Has never been observed to be called
        pass


########################################
# This state is active when powered on and other states return here
class Home(State):

    # Declare global variables for the Home State
    global gui_btn1, gui_btn2                                           # Create variables to store if a button is pressed in GUI
    global gui_out1, gui_out2
    global win

    #Intitalize the global variables within "Home"
    gui_btn1 = False
    gui_btn2 = False


    def __init__(self):
        super().__init__()                                              # Child class inheritance


    @property
    def name(self):
        return 'Home'

    def enter(self, machine):
        global gui_btn1, gui_btn2
        global gui_out1, gui_out2
        global win

        State.enter(self, machine)
        print('#### Home State ####')                                   # Print "Home State" to the serial monitor

        # tkinter Home Screen GUI
        win = Tk()  # setting up window from Tk() naming win
        myFont = font.Font(family='Helvetica', size=18, weight='bold')  # setting up font naming myfont
        # Define the tkinter window instance
        win.title("ltb Home")                                           # title for window
        win.geometry('400x300')                                         # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
        win.eval('tk::PlaceWindow . center')                            # Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
        #win.attributes('-fullscreen', True)                            # uncomment to use fullscreen


        def SW1ON():
            global gui_btn1, gui_out1
            gui_btn1=True                                               # GUI button 1 was pressed, sets boolean
            gui_out1.value=True                                         # Sets GPIO output

            t.sleep(5)
            print("gui_btn1 = ", gui_btn1)
            print("gui_out1 = ", gui_out1.value)
            win.quit()
            win.destroy()                                               # This was previously win.quit(), quit() doesn't close the window

        def SW2ON():
            global gui_btn1, gui_out2
            gui_btn2=True                                               # GUI button 1 was pressed, sets the boolean
            gui_out2.value=True                                         # Sets GPIO output

            t.sleep(5)
            print("gui_btn2 = ", gui_btn2)                              # check the boolean values set
            print("gui_out2 = ", gui_out2.value)
            win.quit()
            win.destroy()                                               # This was previously win.quit(), but doesn't close the window

        # Define the tkinter switch instances
        SW1Button = Button(win, text="EE Intern", font=myFont, command=SW1ON, height=2, width=8)  # setting button naming led1Button
        #SW1Button.place(x=37, y=50)                                    # button position for led1Button #commanding to button to led1ON function
        SW1Button.pack(side=LEFT, anchor=W)

        SW2Button = Button(win, text="CSUS 193B", font=myFont, command=SW2ON, height=2, width=8)  # setting button naming led2Button
        #SW2Button.place(x=520, y=50)                                   # button position for led2Button #commanding to button to led2ON function
        SW2Button.pack(side=RIGHT, anchor=E)

        # Focus Button
        Fbtn = tk.Button(win, text="Focus",font= ("Calibri",10), bg="white", fg="black")
        Fbtn.pack(side=TOP, anchor=E)

        mainloop()  # commanding mainloop for starting main loop

        t.sleep(2)

    def exit(self, machine):

        State.exit(self, machine)

        # Haptic placeholder
        # Sound placeholder

        #GUI shutdown when leaving this state
        print("Exiting Home State")
        gui_out1.value=False                                            # Clears GPIO output pin 15
        print("gui_out1 =", gui_out1.value)
        gui_out2.value=False                                            # Clears GPIO output pin 15
        print("gui_out2 =", gui_out2.value)
        gui_btn1=False                                                  # Clears Home State variable value
        print("gui_btn1 =", gui_btn1)
        gui_btn2=False                                                  # Clears Home State variable value
        print("gui_btn2 =", gui_btn2)



    def pressed(self, machine):             # pressed is the mechanism needed to switch between states

        if switch_1.is_pressed:
            machine.go_to_state('Profile1')
        if switch_2.is_pressed:
            machine.go_to_state('Profile2')


########################################
# The "Focus Timer" state. Begin the focus timer here
class FocusTimer(State):

    # Declare global variables for the Focus Timer State
    global gui_btn1, gui_btn2                                       # Create variables to store if a button is pressed in GUI
    global gui_out1, gui_out2
    global win

    # Intitalize the global variables within "Focus Timer"
    gui_btn1 = False
    gui_btn2 = False

    def __init__(self):
        super().__init__()
        self.State = State()


    @property
    def name(self):
        return 'Focus Timer'

    def enter(self, machine):
        global win
        global gui_btn1, gui_out1
        global gui_btn1, gui_out2

        State.enter(self, machine)
        print('#### Focus Timer State ####')  # Print "Home State" to the serial monitor

        # tkinter Home Screen GUI
        win = Tk()  # setting up window from Tk() naming win
        myFont = font.Font(family='Helvetica', size=18, weight='bold')  # setting up font naming myfont
        # Define the tkinter window instance
        win.title("Focus Timer")                                           # title for window
        win.geometry('400x300')                                         # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
        win.eval('tk::PlaceWindow . center')                            # Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
        #win.attributes('-fullscreen', True)                            # uncomment to use fullscreen


        def SW1ON():
            global gui_btn1, gui_out1
            gui_btn1=True                                               # GUI button 1 was pressed, sets Home State variable to True
            gui_out1.value=True                                         # Sets GPIO output

            t.sleep(5)
            print("gui_btn1 = ", gui_btn1)
            print("gui_out1 = ", gui_out1.value)
            win.quit()
            win.destroy()                                               # Close the GUI window

        def SW2ON():
            global gui_btn1, gui_out2
            gui_btn2=True                                               # GUI button 1 was pressed, sets Home State variable to True
            gui_out2.value=True                                         # Sets GPIO output

            t.sleep(5)
            print("gui_btn2 = ", gui_btn2)
            print("gui_out2 = ", gui_out2.value)
            win.quit()
            win.destroy()                                               # Close the GUI window

        # Define the tkinter switch instances
        SW1Button = Button(win, text="Pause", font=myFont, command=SW1ON, height=2, width=8)  # setting button naming led1Button
        #SW1Button.place(x=37, y=50)                                    # button position for led1Button #commanding to button to led1ON function
        SW1Button.pack(side=LEFT, anchor=W)

        SW2Button = Button(win, text="Exit", font=myFont, command=SW2ON, height=2, width=8)  # setting button naming led2Button
        #SW2Button.place(x=520, y=50)                                   # button position for led2Button #commanding to button to led2ON function
        SW2Button.pack(side=RIGHT, anchor=E)


        mainloop()  # commanding mainloop for starting main loop

        t.sleep(2)

    def exit(self, machine):
        State.exit(self, machine)

        # Haptic placeholder
        # Sound placeholder

        #GUI shutdown when leaving this state
        print("Exiting Focus Timer State")
        gui_out1.value=False                                            # Clears GPIO output pin 15
        print("gui_out1 =", gui_out1.value)
        gui_out2.value=False                                            # Clears GPIO output pin 15
        print("gui_out2 =", gui_out2.value)
        gui_btn1=False                                                  # Clears Home State variable value
        print("gui_btn1 =", gui_btn1)
        gui_btn2=False                                                  # Clears Home State variable value
        print("gui_btn2 =", gui_btn2)

    def pressed(self, machine):

        if switch_1.is_pressed:
            machine.go_to_state('Home')                                 # ** NEED TO ADD A PAUSE STATE
        if switch_2.is_pressed:
            machine.go_to_state('Home')


########################################
# The "Profile 1" state. Either choose to track a task or use a focus timer.
class Profile1(State):

    # Declare global variables for the Profile 1 State
    global gui_btn1, gui_btn2                                            # Create variables to store if a button is pressed in GUI
    global gui_out1, gui_out2
    global recordLED
    global win

    # Intitalize the global variables within "Profile1"
    gui_btn1 = False
    gui_btn2 = False

    def __init__(self):
        super().__init__()
        self.State = State()


    @property
    def name(self):
        return 'Profile1'

    def enter(self, machine):
        global win
        global gui_btn1, gui_out1
        global gui_btn1, gui_out2
        global recordLED

        recordLED.value=True                                            # THIS DOES NOT WORK
        t.sleep(2)
        recordLED.value=False

        State.enter(self, machine)
        print('#### Profile 1 State ####')

        # tkinter Home Screen GUI
        win = Tk()  # setting up window from Tk() naming win
        myFont = font.Font(family='Helvetica', size=18, weight='bold')  # setting up font naming myfont
        # Define the tkinter window instance
        win.title("EE Intern Profile")                                     # title for window
        win.geometry('400x300')                                         # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
        win.eval('tk::PlaceWindow . center')                            # Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
        #win.attributes('-fullscreen', True)                            # uncomment to use fullscreen


        def SW1ON():
            global gui_btn1, gui_out1
            gui_btn1=True                                               # GUI button 1 was pressed, sets Home State variable to True
            gui_out1.value=True                                         # Sets GPIO output

            t.sleep(5)
            print("gui_btn1 = ", gui_btn1)
            print("gui_out1 = ", gui_out1.value)
            win.quit()
            win.destroy()                                               # Close the GUI window

        def SW2ON():
            global gui_btn1, gui_out2
            gui_btn2=True                                               # GUI button 1 was pressed, sets Home State variable to True
            gui_out2.value=True                                         # Sets GPIO output

            t.sleep(5)
            print("gui_btn2 = ", gui_btn2)
            print("gui_out2 = ", gui_out2.value)
            win.quit()
            win.destroy()                                               # Close the GUI window

        # Define the tkinter switch instances
        SW1Button = Button(win, text="Timecard", font=myFont, command=SW1ON, height=2, width=8)  # setting button naming led1Button
        #SW1Button.place(x=37, y=50)                                    # button position for led1Button #commanding to button to led1ON function
        SW1Button.pack(side=LEFT, anchor=W)

        SW2Button = Button(win, text="Intern Project", font=myFont, command=SW2ON, height=2, width=8)  # setting button naming led2Button
        #SW2Button.place(x=520, y=50)                                   # button position for led2Button #commanding to button to led2ON function
        SW2Button.pack(side=RIGHT, anchor=E)

        mainloop()                                                      # commanding mainloop for starting main loop

        t.sleep(2)

    def exit(self, machine):
        State.exit(self, machine)

        # Haptic placeholder
        # Sound placeholder

        #GUI shutdown when leaving this state
        print("Exiting Profile 1 State")
        gui_out1.value=False                                            # Clears GPIO output pin 15
        print("gui_out1 =", gui_out1.value)
        gui_out2.value=False                                            # Clears GPIO output pin 15
        print("gui_out2 =", gui_out2.value)
        gui_btn1=False                                                  # Clears Home State variable value
        print("gui_btn1 =", gui_btn1)
        gui_btn2=False                                                  # Clears Home State variable value
        print("gui_btn2 =", gui_btn2)

    def pressed(self, machine):

        if switch_1.is_pressed:
            machine.go_to_state('P1_Tracking1')
        if switch_2.is_pressed:
            machine.go_to_state('P2_Tracking2')


########################################
# The "Task #1, Profile 1" state. Begin tracking task 1 in this state
class P1_Tracking1(State):

    #Declare global variables for P1_Tracking1 State
    global time_zone_in, time_zone_out
    global timestamp_in, timestamp_out

    global gui_btn1, gui_btn2                                           # Create variables to store if a button is pressed in GUI
    global gui_out1, gui_out2
    global recordLED
    global win

    #Intitalize the global variables within "Tracking1"
    gui_btn1 = False
    gui_btn2 = False

    time_zone_in = None
    timestamp_in = None

    time_zone_out = 0
    timestamp_out = 0


    def __init__(self):
        super().__init__()
        self.State = State()


    @property
    def name(self):
        return 'P1_Tracking1'

    def enter(self, machine):
        global time_zone_in, time_zone_out
        global timestamp_in, timestamp_out

        global win
        global gui_btn1, gui_out1
        global gui_btn1, gui_out2
        global recordLED

        today = date.today()
        timestamp_in = datetime.now(tz=tz.tzlocal())


        State.enter(self, machine)


        # Components of the "time in" stamp
        time_zone_in = timestamp_in.tzname()    # Stores the timezone from datetime

        print('#### Profile 1, Tracking Task 1 State ####')

        print('Logging a START time to .csv file')
         # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
        with open("/home/pi/Desktop/ltb_f22_release/P1_t1.csv", "a") as f:

            recordLED.value = True    #  # THIS DOES NOT WORK
            print("Time zone 'in':",time_zone_in) #Prints data about to be written to the SD card
            print(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            f.write("%s," % (time_zone_in))    #
            f.write(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            recordLED = False  # turn off LED to indicate we're done

            # Read out all lines in the .csv file to verify the last entry
            #with open("/sd/stamp.csv", "r") as f:
            #print("Printing lines in file:")
            #line = f.readline()
            #while line != '':
            #print(line)
            #line = f.readline()

        # tkinter Home Screen GUI
        win = Tk()  # setting up window from Tk() naming win
        myFont = font.Font(family='Helvetica', size=18, weight='bold')  # setting up font naming myfont
        # Define the tkinter window instance
        win.title("Intern Timecard")                                     # title for window
        win.geometry('400x300')                                         # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
        win.eval('tk::PlaceWindow . center')                            # Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
        #win.attributes('-fullscreen', True)                            # uncomment to use fullscreen


        def SW1ON():
            global gui_btn1, gui_out1
            global recordLED
            gui_btn1=True                                               # GUI button 1 was pressed, sets Home State variable to True
            gui_out1.value=True                                         # Sets GPIO output

            global time_zone_in, time_zone_out
            global timestamp_in, timestamp_out

            today = date.today()
            timestamp_out = datetime.now(tz=tz.tzlocal())

            # Components of the "time out" stamp
            time_zone_out = timestamp_out.tzname()    # Stores the timezone from datetime
            delta_time = relativedelta(timestamp_out,timestamp_in)

            # Write the timestamp out when a button is pressed
            # Track the previous variables
            print('Time Zone of "out" timestamp:',time_zone_out)
            print('"out" timestamp:', timestamp_out)

            print('Logging a STOP time to .csv\n')
            # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
            with open("/home/pi/Desktop/ltb_f22_release/P1_t1.csv", "a") as f:
                recordLED.value = True     # THIS DOES NOT WORK
                print("Time zone 'out':",time_zone_out) #Prints data about to be written to the SD card
                print(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                print("The time tracked is:", str(delta_time.hours) + ":" + str(delta_time.minutes) + ":" + str(delta_time.seconds))
                print('\n') # Prints a blank line
                f.write("%s," % (time_zone_out))
                f.write(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                f.write("%d:%d:%02d," % (delta_time.hours,delta_time.minutes,delta_time.seconds))
                recordLED.value = False  # turn off LED to indicate we're done

            # TEST Option: Read out all lines in the .csv file to verify the last entry
            #with open("/sd/stamp.csv", "r") as f:
            #print("Printing lines in file:")
            #line = f.readline()
            #while line != '':
            #print(line)
            #line = f.readline()


            t.sleep(5)
            print("gui_btn1 = ", gui_btn1)
            print("gui_out1 = ", gui_out1.value)
            win.quit()
            win.destroy()                                               # Closes the window

        def SW2ON():
            global gui_btn1, gui_out1
            gui_btn1=True                                               # GUI button 1 was pressed, sets Home State variable to True
            gui_out1.value=True                                         # Sets GPIO output
            global recordLED
            global time_zone_in, time_zone_out
            global timestamp_in, timestamp_out

            today = date.today()
            timestamp_out = datetime.now(tz=tz.tzlocal())

            # Components of the "time out" stamp
            time_zone_out = timestamp_out.tzname()    # Stores the timezone from datetime
            delta_time = relativedelta(timestamp_out,timestamp_in)

            # Write the timestamp out when a button is pressed
            # Track the previous variables
            print('Time Zone of "out" timestamp:',time_zone_out)
            print('"out" timestamp:', timestamp_out)

            print('Logging a STOP time to .csv\n')
            # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
            with open("/home/pi/Desktop/ltb_f22_release/P1_t1.csv", "a") as f:
                recordLED.value = True     # THIS DOES NOT WORK
                print("Time zone 'out':",time_zone_out) #Prints data about to be written to the SD card
                print(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                print("The time tracked is:", str(delta_time.hours) + ":" + str(delta_time.minutes) + ":" + str(delta_time.seconds))
                print('\n') # Prints a blank line
                f.write("%s," % (time_zone_out))
                f.write(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                f.write("%d:%d:%02d," % (delta_time.hours,delta_time.minutes,delta_time.seconds))
                recordLED.value = False  # turn off LED to indicate we're done

            # TEST Option: Read out all lines in the .csv file to verify the last entry
            #with open("/sd/stamp.csv", "r") as f:
            #print("Printing lines in file:")
            #line = f.readline()
            #while line != '':
            #print(line)
            #line = f.readline()

            t.sleep(5)
            print("gui_btn2 = ", gui_btn2)
            print("gui_out2 = ", gui_out2.value)
            win.quit()
            win.destroy()                                               # Closes the window

        # Define the tkinter switch instances
        SW1Button = Button(win, text="Pause", font=myFont, command=SW1ON, height=2, width=8)  # setting button naming led1Button
        #SW1Button.place(x=37, y=50)                                    # button position for led1Button #commanding to button to led1ON function
        SW1Button.pack(side=LEFT, anchor=W)

        SW2Button = Button(win, text="Exit", font=myFont, command=SW2ON, height=2, width=8)  # setting button naming led2Button
        #SW2Button.place(x=520, y=50)                                   # button position for led2Button #commanding to button to led2ON function
        SW2Button.pack(side=RIGHT, anchor=E)


        mainloop()  # commanding mainloop for starting main loop

        t.sleep(2)


    def exit(self, machine):


        State.exit(self, machine)


        # Haptic placeholder
        # Sound placeholder

        #GUI shutdown when leaving this state
        print("Exiting P2_Tracking 2 State")
        gui_out1.value=False                                            # Clears GPIO output pin 15
        print("gui_out1 =", gui_out1.value)
        gui_out2.value=False                                            # Clears GPIO output pin 15
        print("gui_out2 =", gui_out2.value)
        gui_btn1=False                                                  # Clears Home State variable value
        print("gui_btn1 =", gui_btn1)
        gui_btn2=False                                                  # Clears Home State variable value
        print("gui_btn2 =", gui_btn2)


    def pressed(self, machine):

        if switch_1.is_pressed:
            machine.go_to_state('Home')                                 # Placeholder for a Pause Button & Pause State
        if switch_2.is_pressed:
            machine.go_to_state('Profile1')                             # Placeholder for a Stop button, return to Profile 1


########################################
# The "Task #2, Profile 1" state. Begin tracking task 1 in this state
class P1_Tracking2(State):

    #Declare global variables for P1_Tracking2 State
    global time_zone_in, time_zone_out
    global timestamp_in, timestamp_out

    global gui_btn1, gui_btn2                                           # Create variables to store if a button is pressed in GUI
    global gui_out1, gui_out2
    global recordLED
    global win

    #Intitalize the global variables within P1_Tracking2
    gui_btn1 = False
    gui_btn2 = False

    time_zone_in = None
    timestamp_in = None

    time_zone_out = 0
    timestamp_out = 0


    def __init__(self):
        super().__init__()
        self.State = State()


    @property
    def name(self):
        return 'P1_Tracking2'

    def enter(self, machine):
        global time_zone_in, time_zone_out
        global timestamp_in, timestamp_out

        today = date.today()
        timestamp_in = datetime.now(tz=tz.tzlocal())


        State.enter(self, machine)


        # Components of the "time in" stamp
        time_zone_in = timestamp_in.tzname()    # Stores the timezone from datetime

        print('#### Profile 1, Tracking Task 2 State ####')

        print('Logging a START time to .csv file')
         # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
        with open("/home/pi/Desktop/ltb_f22_release/P1_t2.csv", "a") as f:

            recordLED.value = True    # THIS DOES NOT WORK
            print("Time zone 'in':",time_zone_in) #Prints data about to be written to the SD card
            print(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            f.write("%s," % (time_zone_in))    #
            f.write(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            recordLED.value = False  # turn off LED to indicate we're done

            # Test Option: Read out all lines in the .csv file to verify the last entry
            #with open("/sd/stamp.csv", "r") as f:
            #print("Printing lines in file:")
            #line = f.readline()
            #while line != '':
            #print(line)
            #line = f.readline()

        # tkinter Home Screen GUI
        win = Tk()  # setting up window from Tk() naming win
        myFont = font.Font(family='Helvetica', size=18, weight='bold')  # setting up font naming myfont
        # Define the tkinter window instance
        win.title("EE Intern Project")                                     # title for window
        win.geometry('400x300')                                         # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
        win.eval('tk::PlaceWindow . center')                            # Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
        #win.attributes('-fullscreen', True)                            # uncomment to use fullscreen


        def SW1ON():
            global gui_btn1, gui_out1
            global recordLED
            gui_btn1=True                                               # GUI button 1 was pressed, sets Home State variable to True
            gui_out1.value=True                                         # Sets GPIO output

            global time_zone_in, time_zone_out
            global timestamp_in, timestamp_out

            today = date.today()
            timestamp_out = datetime.now(tz=tz.tzlocal())

            # Components of the "time out" stamp
            time_zone_out = timestamp_out.tzname()    # Stores the timezone from datetime
            delta_time = relativedelta(timestamp_out,timestamp_in)

            # Write the timestamp out when a button is pressed
            # Track the previous variables
            print('Time Zone of "out" timestamp:',time_zone_out)
            print('"out" timestamp:', timestamp_out)

            print('Logging a STOP time to .csv\n')
            # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
            with open("/home/pi/Desktop/ltb_f22_release/P1_t2.csv", "a") as f:
                recordLED.value = True    #  THIS DOES NOT WORK
                print("Time zone 'out':",time_zone_out) #Prints data about to be written to the SD card
                print(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                print("The time tracked is:", str(delta_time.hours) + ":" + str(delta_time.minutes) + ":" + str(delta_time.seconds))
                print('\n') # Prints a blank line
                f.write("%s," % (time_zone_out))
                f.write(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                f.write("%d:%d:%02d," % (delta_time.hours,delta_time.minutes,delta_time.seconds))
                recordLED.value = False  # turn off LED to indicate we're done

            # TEST Option: Read out all lines in the .csv file to verify the last entry
            #with open("/sd/stamp.csv", "r") as f:
            #print("Printing lines in file:")
            #line = f.readline()
            #while line != '':
            #print(line)
            #line = f.readline()


            t.sleep(5)
            print("gui_btn1 = ", gui_btn1)
            print("gui_out1 = ", gui_out1.value)
            win.quit()
            win.destroy()                                               # Closes the window

        def SW2ON():
            global gui_btn1, gui_out1
            global recordLED
            gui_btn1=True                                               # GUI button 1 was pressed, sets Home State variable to True
            gui_out1.value=True                                         # Sets GPIO output

            global time_zone_in, time_zone_out
            global timestamp_in, timestamp_out

            today = date.today()
            timestamp_out = datetime.now(tz=tz.tzlocal())

            # Components of the "time out" stamp
            time_zone_out = timestamp_out.tzname()    # Stores the timezone from datetime
            delta_time = relativedelta(timestamp_out,timestamp_in)

            # Write the timestamp out when a button is pressed
            # Track the previous variables
            print('Time Zone of "out" timestamp:',time_zone_out)
            print('"out" timestamp:', timestamp_out)

            print('Logging a STOP time to .csv\n')
            # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
            with open("/home/pi/Desktop/ltb_f22_release/P1_t1.csv", "a") as f:
                recordLED.value = True     # THIS DOES NOT WORK
                print("Time zone 'out':",time_zone_out) #Prints data about to be written to the SD card
                print(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                print("The time tracked is:", str(delta_time.hours) + ":" + str(delta_time.minutes) + ":" + str(delta_time.seconds))
                print('\n') # Prints a blank line
                f.write("%s," % (time_zone_out))
                f.write(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                f.write("%d:%d:%02d," % (delta_time.hours,delta_time.minutes,delta_time.seconds))
                recordLED.value = False  # turn off LED to indicate we're done

            # TEST Option: Read out all lines in the .csv file to verify the last entry
            #with open("/sd/stamp.csv", "r") as f:
            #print("Printing lines in file:")
            #line = f.readline()
            #while line != '':
            #print(line)
            #line = f.readline()

            t.sleep(5)
            print("gui_btn2 = ", gui_btn2)
            print("gui_out2 = ", gui_out2.value)
            win.quit()
            win.destroy()                                               # This was previously win.quit(), but doesn't close the window

        # Define the tkinter switch instances
        SW1Button = Button(win, text="Pause", font=myFont, command=SW1ON, height=2, width=8)  # setting button naming led1Button
        #SW1Button.place(x=37, y=50)                                    # button position for led1Button #commanding to button to led1ON function
        SW1Button.pack(side=LEFT, anchor=W)

        SW2Button = Button(win, text="Exit", font=myFont, command=SW2ON, height=2, width=8)  # setting button naming led2Button
        #SW2Button.place(x=520, y=50)                                   # button position for led2Button #commanding to button to led2ON function
        SW2Button.pack(side=RIGHT, anchor=E)

        mainloop()  # commanding mainloop for starting main loop

        t.sleep(2)


    def exit(self, machine):


        State.exit(self, machine)


        # Haptic placeholder
        # Sound placeholder

        #GUI shutdown when leaving this state
        print("Exiting P1_Tracking 2 State")
        gui_out1.value=False                                            # Clears GPIO output pin 15
        print("gui_out1 =", gui_out1.value)
        gui_out2.value=False                                            # Clears GPIO output pin 15
        print("gui_out2 =", gui_out2.value)
        gui_btn1=False                                                  # Clears Home State variable value
        print("gui_btn1 =", gui_btn1)
        gui_btn2=False                                                  # Clears Home State variable value
        print("gui_btn2 =", gui_btn2)

    def pressed(self, machine):

        if switch_1.is_pressed:
            machine.go_to_state('Home')     # Placeholder for a Pause Button & Pause State
        if switch_2.is_pressed:
            machine.go_to_state('Profile1')     # Placeholder for a Stop button, return to Profile 1


########################################
# The "Profile 2" state. Implement at a later date. Any button press in this state causes a transition to the "Home" state.
class Profile2(State):

    # Declare global variables for the Profile2 State
    global gui_btn1, gui_btn2                       # Create variables to store if a button is pressed in GUI
    global gui_out1, gui_out2
    global recordLED
    global win

    #Intitalize the global variables within Profile2
    gui_btn1 = False
    gui_btn2 = False

    def __init__(self):
        super().__init__()
        self.State = State()


    @property
    def name(self):
        return 'Profile2'

    def enter(self, machine):
        global win
        global gui_btn1, gui_out1
        global gui_btn1, gui_out2
        global recordLED

        recordLED.value=True                                             # THIS DOES NOT WORK
        t.sleep(2)
        recordLED.value=False

        State.enter(self, machine)
        print('#### Profile 2 State ####')
        #gui_out1.value=True                                            # Sets GPIO output High
        #gui_out2.value=True                                            # Sets GPIO output High

        # tkinter Home Screen GUI
        win = Tk()  # setting up window from Tk() naming win
        myFont = font.Font(family='Helvetica', size=18, weight='bold')  # setting up font naming myfont
        # Define the tkinter window instance
        win.title("CSUS Profile")                                     # title for window
        win.geometry('400x300')                                         # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
        win.eval('tk::PlaceWindow . center')                            # Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
        #win.attributes('-fullscreen', True)                            # uncomment to use fullscreen


        def SW1ON():
            global gui_btn1, gui_out1
            gui_btn1=True                                               # GUI button 1 was pressed, sets Home State variable to True
            gui_out1.value=True                                         # Sets GPIO output

            t.sleep(5)
            print("gui_btn1 = ", gui_btn1)
            print("gui_out1 = ", gui_out1.value)
            win.quit()
            win.destroy()                                               # Closes the GUI the window

        def SW2ON():
            global gui_btn1, gui_out2
            gui_btn2=True                                               # GUI button 1 was pressed, sets Home State variable to True
            gui_out2.value=True                                         # Sets GPIO output

            t.sleep(5)
            print("gui_btn2 = ", gui_btn2)
            print("gui_out2 = ", gui_out2.value)
            win.quit()
            win.destroy()                                               # Closes the GUI the window

        # Define the tkinter switch instances
        SW1Button = Button(win, text="Development", font=myFont, command=SW1ON, height=2, width=8)  # setting button naming led1Button
        #SW1Button.place(x=37, y=50)                                    # button position for led1Button #commanding to button to led1ON function
        SW1Button.pack(side=LEFT, anchor=W)

        SW2Button = Button(win, text="Assignments", font=myFont, command=SW2ON, height=2, width=8)  # setting button naming led2Button
        #SW2Button.place(x=520, y=50)                                   # button position for led2Button #commanding to button to led2ON function
        SW2Button.pack(side=RIGHT, anchor=E)

        mainloop()  # commanding mainloop for starting main loop

        t.sleep(2)

    def exit(self, machine):
        State.exit(self, machine)

        # Haptic placeholder
        # Sound placeholder

        #GUI shutdown when leaving this state
        print("Exiting Profile 2 State")
        gui_out1.value=False                                            # Clears GPIO output pin 15
        print("gui_out1 =", gui_out1.value)
        gui_out2.value=False                                            # Clears GPIO output pin 15
        print("gui_out2 =", gui_out2.value)
        gui_btn1=False                                                  # Clears Home State variable value
        print("gui_btn1 =", gui_btn1)
        gui_btn2=False                                                  # Clears Home State variable value
        print("gui_btn2 =", gui_btn2)

    def pressed(self, machine):
        if switch_1.is_pressed:
            machine.go_to_state('P2_Tracking1')     # Either button press returns to "Home" state, further profiles will be implemented in the future

    def pressed(self, machine):
        if switch_2.is_pressed:
            machine.go_to_state('P2_Tracking2')


########################################
# The "Task #1, Profile 2" state. Begin tracking task 1 in this state
class P2_Tracking1(State):

    #Declare global variables for Tracking1 State
    global time_zone_in, time_zone_out
    global timestamp_in, timestamp_out

    # Declare global variables for the Home State
    global gui_btn1, gui_btn2                                                                   # Create variables to store if a button is pressed in GUI
    global gui_out1, gui_out2
    global recordLED
    global win

    #Intitalize the global variables within "Tracking1"
    gui_btn1 = False
    gui_btn2 = False

    # Intitalize the global variables within "Tracking1"
    time_zone_in = None
    timestamp_in = None

    time_zone_out = 0
    timestamp_out = 0


    def __init__(self):
        super().__init__()
        self.State = State()


    @property
    def name(self):
        return 'P2_Tracking1'

    def enter(self, machine):
        global time_zone_in, time_zone_out
        global timestamp_in, timestamp_out

        global win
        global gui_btn1, gui_out1
        global gui_btn1, gui_out2
        global recordLED

        today = date.today()
        timestamp_in = datetime.now(tz=tz.tzlocal())


        State.enter(self, machine)


        # Components of the "time in" stamp
        time_zone_in = timestamp_in.tzname()                        # Stores the timezone from datetime

        print('#### Profile 2, Tracking Task 1 State ####')

        print('Logging a START time to .csv file')
         # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
        with open("/home/pi/Desktop/ltb_f22_release/P2_t1.csv", "a") as f:

            recordLED.value = True     # THIS DOES NOT WORK
            t.sleep(0.5)
            print("Time zone 'in':",time_zone_in) #Prints data about to be written to the SD card
            print(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            f.write("%s," % (time_zone_in))    #
            f.write(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            recordLED.value = False  # turn off LED to indicate we're done
            t.sleep(0.5)


            # Read out all lines in the .csv file to verify the last entry
            #with open("/sd/stamp.csv", "r") as f:
            #print("Printing lines in file:")
            #line = f.readline()
            #while line != '':
            #print(line)
            #line = f.readline()

        # tkinter Home Screen GUI
        win = Tk()  # setting up window from Tk() naming win
        myFont = font.Font(family='Helvetica', size=18, weight='bold')  # setting up font naming myfont
        # Define the tkinter window instance
        win.title("EEE 193B Development")                                     # title for window
        win.geometry('400x300')                                         # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
        win.eval('tk::PlaceWindow . center')                            # Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
        #win.attributes('-fullscreen', True)                            # uncomment to use fullscreen


        def SW1ON():
            global gui_btn1, gui_out1
            global recordLED
            gui_btn1=True                                               # GUI button 1 was pressed, sets Home State variable to True
            gui_out1.value=True                                         # Sets GPIO output

            global time_zone_in, time_zone_out
            global timestamp_in, timestamp_out

            today = date.today()
            timestamp_out = datetime.now(tz=tz.tzlocal())

            # Components of the "time out" stamp
            time_zone_out = timestamp_out.tzname()    # Stores the timezone from datetime
            delta_time = relativedelta(timestamp_out,timestamp_in)

            # Write the timestamp out when a button is pressed
            # Track the previous variables
            print('Time Zone of "out" timestamp:',time_zone_out)
            print('"out" timestamp:', timestamp_out)

            print('Logging a STOP time to .csv\n')
            # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
            with open("/home/pi/Desktop/ltb_f22_release/P2_t1.csv", "a") as f:
                recordLED.value = True     # THIS DOES NOT WORK
                t.sleep(0.5)
                print("Time zone 'out':",time_zone_out) #Prints data about to be written to the SD card
                print(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                print("The time tracked is:", str(delta_time.hours) + ":" + str(delta_time.minutes) + ":" + str(delta_time.seconds))
                print('\n') # Prints a blank line
                f.write("%s," % (time_zone_out))
                f.write(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                f.write("%d:%d:%02d," % (delta_time.hours,delta_time.minutes,delta_time.seconds))
                recordLED.value = False  # turn off LED to indicate we're done
                t.sleep(0.5)

            # TEST Option: Read out all lines in the .csv file to verify the last entry
            #with open("/sd/stamp.csv", "r") as f:
            #print("Printing lines in file:")
            #line = f.readline()
            #while line != '':
            #print(line)
            #line = f.readline()


            t.sleep(5)
            # Track the previous variables
            print('Time Zone of "out" timestamp:',time_zone_out)
            print('"out" timestamp:', timestamp_out)

            print("gui_btn1 = ", gui_btn1)
            print("gui_out1 = ", gui_out1.value)

            win.quit()
            win.destroy()                                               # Closes the GUI window

        def SW2ON():
            global gui_btn1, gui_out1
            global recordLED
            gui_btn1=True                                               # GUI button 1 was pressed, sets Home State variable to True
            gui_out1.value=True                                         # Sets GPIO output

            global time_zone_in, time_zone_out
            global timestamp_in, timestamp_out

            today = date.today()
            timestamp_out = datetime.now(tz=tz.tzlocal())

            # Components of the "time out" stamp
            time_zone_out = timestamp_out.tzname()    # Stores the timezone from datetime
            delta_time = relativedelta(timestamp_out,timestamp_in)

            # Write the timestamp out when a button is pressed
            # Track the previous variables
            print('Time Zone of "out" timestamp:',time_zone_out)
            print('"out" timestamp:', timestamp_out)

            print('Logging a STOP time to .csv\n')
            # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
            with open("/home/pi/Desktop/ltb_f22_release/P2_t1.csv", "a") as f:
                recordLED.value = True    # turn on LED to indicate writing entries
                t.sleep(0.5)
                print("Time zone 'out':",time_zone_out) #Prints data about to be written to the SD card
                print(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                print("The time tracked is:", str(delta_time.hours) + ":" + str(delta_time.minutes) + ":" + str(delta_time.seconds))
                print('\n') # Prints a blank line
                f.write("%s," % (time_zone_out))
                f.write(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                f.write("%d:%d:%02d," % (delta_time.hours,delta_time.minutes,delta_time.seconds))
                recordLED.value = False  # turn off LED to indicate we're done
                t.sleep(0.5)

            # TEST Option: Read out all lines in the .csv file to verify the last entry
            #with open("/sd/stamp.csv", "r") as f:
            #print("Printing lines in file:")
            #line = f.readline()
            #while line != '':
            #print(line)
            #line = f.readline()

            t.sleep(5)
            # Track the previous variables
            print('Time Zone of "out" timestamp:',time_zone_out)
            print('"out" timestamp:', timestamp_out)

            print("gui_btn2 = ", gui_btn2)
            print("gui_out2 = ", gui_out2.value)

            win.quit()
            win.destroy()                                               # Closes the GUI window

        # Define the tkinter switch instances
        SW1Button = Button(win, text="Pause", font=myFont, command=SW1ON, height=2, width=8)  # setting button naming led1Button
        #SW1Button.place(x=37, y=50)                                    # button position for led1Button #commanding to button to led1ON function
        SW1Button.pack(side=LEFT, anchor=W)

        SW2Button = Button(win, text="Exit", font=myFont, command=SW2ON, height=2, width=8)  # setting button naming led2Button
        #SW2Button.place(x=520, y=50)                                   # button position for led2Button #commanding to button to led2ON function
        SW2Button.pack(side=RIGHT, anchor=E)

        mainloop()  # commanding mainloop for starting main loop

        t.sleep(2)


    def exit(self, machine):


        State.exit(self, machine)


        # Haptic placeholder
        # Sound placeholder

        #GUI shutdown when leaving this state
        print("Exiting P2_Tracking 1 State")
        gui_out1.value=False                                            # Clears GPIO output pin 15
        print("gui_out1 =", gui_out1.value)
        gui_out2.value=False                                            # Clears GPIO output pin 15
        print("gui_out2 =", gui_out2.value)
        gui_btn1=False                                                  # Clears Home State variable value
        print("gui_btn1 =", gui_btn1)
        gui_btn2=False                                                  # Clears Home State variable value
        print("gui_btn2 =", gui_btn2)                                                                         # Clears Home State variable value

    def pressed(self, machine):

        if switch_1.is_pressed:
            machine.go_to_state('Home')                                                         # Placeholder for a Pause Button & Pause State
        if switch_2.is_pressed:
            machine.go_to_state('Profile2')                                                    # Placeholder for a Stop button, return to Profile 2


########################################
# The "Task #2, Profile 2" state. Begin tracking task 1 in this state
class P2_Tracking2(State):

    #Declare global variables for Tracking1 State
    global time_zone_in, time_zone_out
    global timestamp_in, timestamp_out

    # Declare global variables for the Home State
    global gui_btn1, gui_btn2                                                                   # Create variables to store if a button is pressed in GUI
    global gui_out1, gui_out2
    global recordLED
    global win

    #Intitalize the global variables within "Tracking1"
    gui_btn1 = False
    gui_btn2 = False

    # Intitalize the global variables within "Tracking1"
    time_zone_in = None
    timestamp_in = None

    time_zone_out = 0
    timestamp_out = 0


    def __init__(self):
        super().__init__()
        self.State = State()


    @property
    def name(self):
        return 'P2_Tracking2'

    def enter(self, machine):
        global time_zone_in, time_zone_out
        global timestamp_in, timestamp_out

        today = date.today()
        timestamp_in = datetime.now(tz=tz.tzlocal())


        State.enter(self, machine)


        # Components of the "time in" stamp
        time_zone_in = timestamp_in.tzname()    # Stores the timezone from datetime

        print('#### Profile 2, Tracking Task 2 [State] ####')

        print('Logging a START time to .csv file')
         # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
        with open("/home/pi/Desktop/ltb_f22_release/P2_t2.csv", "a") as f:

            recordLED.value=True     # THIS DOES NOT WORK
            t.sleep(0.5)
            print("Time zone 'in':",time_zone_in) #Prints data about to be written to the SD card
            print(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            f.write("%s," % (time_zone_in))    #
            f.write(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            recordLED.value=False  # turn off LED to indicate we're done
            t.sleep(0.5)

            # Read out all lines in the .csv file to verify the last entry
            #with open("/sd/stamp.csv", "r") as f:
            #print("Printing lines in file:")
            #line = f.readline()
            #while line != '':
            #print(line)
            #line = f.readline()

        # tkinter Home Screen GUI
        win = Tk()  # setting up window from Tk() naming win
        myFont = font.Font(family='Helvetica', size=18, weight='bold')                      # setting up font naming myfont
        # Define the tkinter window instance
        win.title("EEE 193B Assignments")                                                            # title for window
        win.geometry('400x300')                                                             # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
        win.eval('tk::PlaceWindow . center')                                                # Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
        #win.attributes('-fullscreen', True)                                                # uncomment to use fullscreen


        def SW1ON():
            global gui_btn1, gui_out1
            global recordLED
            gui_btn1=True                                               # GUI button 1 was pressed, sets Home State variable to True
            gui_out1.value=True                                         # Sets GPIO output

            global time_zone_in, time_zone_out
            global timestamp_in, timestamp_out

            today = date.today()
            timestamp_out = datetime.now(tz=tz.tzlocal())

            # Components of the "time out" stamp
            time_zone_out = timestamp_out.tzname()    # Stores the timezone from datetime
            delta_time = relativedelta(timestamp_out,timestamp_in)

            # Write the timestamp out when a button is pressed
            # Track the previous variables
            print('Time Zone of "out" timestamp:',time_zone_out)
            print('"out" timestamp:', timestamp_out)

            print('Logging a STOP time to .csv\n')
            # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
            with open("/home/pi/Desktop/ltb_f22_release/P2_t2.csv", "a") as f:
                recordLED.valu =True     # THIS DOES NOT WORK
                t.sleep(0.5)
                print("Time zone 'out':",time_zone_out) #Prints data about to be written to the SD card
                print(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                print("The time tracked is:", str(delta_time.hours) + ":" + str(delta_time.minutes) + ":" + str(delta_time.seconds))
                print('\n') # Prints a blank line
                f.write("%s," % (time_zone_out))
                f.write(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                f.write("%d:%d:%02d," % (delta_time.hours,delta_time.minutes,delta_time.seconds))
                recordLED.value=False  # turn off LED to indicate we're done
                t.sleep(0.5)

            # TEST Option: Read out all lines in the .csv file to verify the last entry
            #with open("/sd/stamp.csv", "r") as f:
            #print("Printing lines in file:")
            #line = f.readline()
            #while line != '':
            #print(line)
            #line = f.readline()


            t.sleep(5)
            # Track the previous variables
            print('Time Zone of "out" timestamp:',time_zone_out)
            print('"out" timestamp:', timestamp_out)

            print("gui_btn1 = ", gui_btn1)
            print("gui_out1 = ", gui_out1.value)

            win.quit()
            win.destroy()                                               # Closes the GUI window

        def SW2ON():
            global gui_btn1, gui_out1
            global recordLED
            gui_btn1=True                                               # GUI button 1 was pressed, sets Home State variable to True
            gui_out1.value=True                                         # Sets GPIO output

            global time_zone_in, time_zone_out
            global timestamp_in, timestamp_out

            today = date.today()
            timestamp_out = datetime.now(tz=tz.tzlocal())

            # Components of the "time out" stamp
            time_zone_out = timestamp_out.tzname()    # Stores the timezone from datetime
            delta_time = relativedelta(timestamp_out,timestamp_in)

            # Write the timestamp out when a button is pressed
            # Track the previous variables
            print('Time Zone of "out" timestamp:',time_zone_out)
            print('"out" timestamp:', timestamp_out)

            print('Logging a STOP time to .csv\n')
            # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
            with open("/home/pi/Desktop/ltb_f22_release/P2_t2.csv", "a") as f:
                recordLED.value=True     # THIS DOES NOT WORK
                t.sleep(0.5)
                print("Time zone 'out':",time_zone_out) #Prints data about to be written to the SD card
                print(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                print("The time tracked is:", str(delta_time.hours) + ":" + str(delta_time.minutes) + ":" + str(delta_time.seconds))
                print('\n') # Prints a blank line
                f.write("%s," % (time_zone_out))
                f.write(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
                f.write("%d:%d:%02d," % (delta_time.hours,delta_time.minutes,delta_time.seconds))
                recordLED.value=False  # turn off LED to indicate we're done
                t.sleep(0.5)

            # TEST Option: Read out all lines in the .csv file to verify the last entry
            #with open("/sd/stamp.csv", "r") as f:
            #print("Printing lines in file:")
            #line = f.readline()
            #while line != '':
            #print(line)
            #line = f.readline()

            t.sleep(5)
            # Track the previous variables
            print('Time Zone of "out" timestamp:',time_zone_out)
            print('"out" timestamp:', timestamp_out)

            print("gui_btn2 = ", gui_btn2)
            print("gui_out2 = ", gui_out2)

            win.quit()
            win.destroy()                                               # Closes the GUI window

        # Define the tkinter switch instances
        SW1Button = Button(win, text="Pause", font=myFont, command=SW1ON, height=2, width=8)  # setting button naming led1Button
        #SW1Button.place(x=37, y=50)                                    # button position for led1Button #commanding to button to led1ON function
        SW1Button.pack(side=LEFT, anchor=W)

        SW2Button = Button(win, text="Exit", font=myFont, command=SW2ON, height=2, width=8)  # setting button naming led2Button
        #SW2Button.place(x=520, y=50)                                   # button position for led2Button #commanding to button to led2ON function
        SW2Button.pack(side=RIGHT, anchor=E)

        mainloop()  # commanding mainloop for starting main loop

        t.sleep(2)


    def exit(self, machine):


        State.exit(self, machine)


        # Haptic placeholder
        # Sound placeholder

        #GUI shutdown when leaving this state
        print("Exiting P2_Tracking 2 State")
        gui_out1.value=False                                            # Clears GPIO output
        print("gui_out1 =", gui_out1.value)
        gui_out2.value=False                                            # Clears GPIO output
        print("gui_out2 =", gui_out2.value)
        gui_btn1=False                                                  # Clears Home State variable value
        print("gui_btn1 =", gui_btn1)
        gui_btn2=False                                                  # Clears Home State variable value
        print("gui_btn2 =", gui_btn2)


    def pressed(self, machine):

        if switch_1.is_pressed:
            machine.go_to_state('Home')                                 # Placeholder for a Pause Button & Pause State
        if switch_2.is_pressed:
            machine.go_to_state('Profile2')                            # Placeholder for a Stop button, return to Profile 2


################################################################################
# Create the state machine

LTB_state_machine = StateMachine()                                      # Defines the state machine
LTB_state_machine.add_state(Home())                                     # Adds the listed states to the machine (Except for the class, "State"
LTB_state_machine.add_state(FocusTimer())
LTB_state_machine.add_state(Profile1())
LTB_state_machine.add_state(P1_Tracking1())
LTB_state_machine.add_state(P1_Tracking2())
LTB_state_machine.add_state(Profile2())
LTB_state_machine.add_state(P2_Tracking1())
LTB_state_machine.add_state(P2_Tracking2())

LTB_state_machine.go_to_state('Home')                                   #Starts the state machine in the "Home" state

while True:
    switch_1.value                                                      #Checks the switch 1 state each time the loop executes, necessary for button state changes
    switch_2.value                                                      #Checks the switch 1 state each time the loop executes, necessary for button state changes
    LTB_state_machine.pressed()                                         #Transitions to the StateMachine attrubute, "pressed". Doesn't do much there other than report the current state