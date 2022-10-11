# Little Time Buddy-Integration with Capacitive TFT Screen-Release Code Rev. 0
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
TESTING = False

################################################################################
# Setup hardware

# Input Pins
switch_1 = gpiozero.Button(5, pull_up=False)
switch_2 = gpiozero.Button(6, pull_up=False)


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

    def pressed1(self):                              # "button pressed" attribute. Accessed at the end of each loop, applies a pause and prints confirmaiton if setup.
        if self.state:
            log('Updating %s' % (self.state.name))
            self.state.pressed(self)
            #print("'StateMachine' Class occurrence")  # Use this print statement to understand how the states transition here to update the state in the serial monitor
            t.sleep(.50)                             # Critial pause needed to prevent the serial monitor from being "flooded" with data and crashing

    def pressed2(self):                              # "button pressed" attribute. Accessed at the end of each loop, applies a pause and prints confirmaiton if setup.
        if self.state:
            log('Updating %s' % (self.state.name))
            self.state.pressed(self)
            t.sleep(.50)                             # Critial pause needed to prevent the serial monitor from being "flooded" with data and crashing


################################################################################
# States in the form of classes/individual modules

class State(object):            # Question: Why is the argument named "object?"


    def __init__(self):                               # Constructor. Sets variables for the class, in this instance only, "self". Note machine variable below in the "enter" attribute

        @property
        def name(self):                               # Attribute. Only the name is returned in states below. The State object shouldn't be called and returns nothing
            return ''

    def enter(self, machine):                         # Class Attribute. Does what is commanded when the state is entered
        pass

    def exit(self, machine):                          # Class Attribute. Does what is commanded when exiting the state
        pass

    def pressed1(self, machine):                      # Pressed is never called

    def pressed2(self, machine): 


########################################
# This state is active when powered on and other states return here
class Home(State):

    #tkinter Home GUI
    win = Tk()  # setting up window from Tk() naming win
    myFont = font.Font(family='Helvetica', size=18, weight='bold')  # setting up font naming myfont

    # Define the tkinter window instance
    win.title("ltb Home")                                           # title for window
    win.geometry('400x300')                                         # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
    win.eval('tk::PlaceWindow . center')                            # Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
    win.attributes('-fullscreen', True)
    # Define the tkinter SW1 instance
    SW1Button = Button(win, text="SW 1 OFF", font=myFont, command=SW1ON, height=2, width=8)  # setting button naming led1Button
    #SW1Button.place(x=37, y=50)                                    # button position for led1Button #commanding to button to led1ON function
    SW1Button.pack(side=LEFT, anchor=W)

    SW2Button = Button(win, text="SW 2 OFF", font=myFont, command=SW2ON, height=2, width=8)  # setting button naming led2Button
    #SW2Button.place(x=520, y=50)                                   # button position for led2Button #commanding to button to led2ON function
    SW2Button.pack(side=RIGHT, anchor=E)


    def __init__(self):
        super().__init__()          # Child class inheritance


    @property
    def name(self):
        return 'Home'

    def enter(self, machine):
        State.enter(self, machine)

        print('#### Home State ####')  # Print "Home State" to the serial monitor
        
        t.sleep(2)

    def exit(self, machine):
        State.exit(self, machine)

        # Haptic placeholder
        # Sound placeholder 

        #GUI shutdown when leaving this state
        print("Exit Button pressed")
        GPIO.cleanup()  # Quitting program
        win.destroy()  # This was previously win.quit(), but doesn't close the window

    def pressed1(self, machine):
        if switch_1.is_pressed:                                         #
            machine.go_to_state('Profile 1')

    def pressed2(self, machine):
        if switch_2.is_pressed:
            machine.go_to_state('Profile 2')


########################################
# The "Focus Timer" state. Begin the focus timer here
class FocusTimer(State):

    def __init__(self):
        super().__init__()
        self.State = State()


    @property
    def name(self):
        return 'Focus Timer 1'

    def enter(self, machine):
        State.enter(self, machine)

        print('#### Focus Timer 1 State ####')

        t.sleep(2)

    def exit(self, machine):
        State.exit(self, machine)

        # Haptic placeholder
        # Sound placeholder 

    def pressed1(self, machine):
        if switch_1.is_pressed:                   # Either button press results in a transition to the "Home" state
            machine.go_to_state('Home')

    def pressed2(self, machine):
        if switch_2.is_pressed:                   # Question: Perhaps a transition to "Profile1" is more appropriate?
            machine.go_to_state('Home')


########################################
# The "Profile 1" state. Either choose to track a task or use a focus timer.
class Profile1(State):


    def __init__(self):
        super().__init__()
        self.State = State()


    @property
    def name(self):
        return 'Profile 1'

    def enter(self, machine):
        State.enter(self, machine)

        print('#### Profile 1 State ####')

        t.sleep(3)

    def exit(self, machine):
        State.exit(self, machine)

        # Haptic placeholder
        # Sound placeholder 

    def pressed1(self, machine):
        if switch_1.is_pressed:
            machine.go_to_state('P1_Tracking1')

    def pressed2(self, machine):
        if switch_2.is_pressed:
            machine.go_to_state('P2_Tracking2')


########################################
# The "Task #1, Profile 1" state. Begin tracking task 1 in this state
class P1_Tracking1(State):

    #Declare global variables for Tracking1 State
    global time_zone_in, time_zone_out
    global timestamp_in, timestamp_out

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
        return 'Tracking1'

    def enter(self, machine):
        global time_zone_in, time_zone_out
        global timestamp_in, timestamp_out

        today = date.today()
        timestamp_in = datetime.now(tz=tz.tzlocal())


        State.enter(self, machine)


        # Components of the "time in" stamp
        time_zone_in = timestamp_in.tzname()    # Stores the timezone from datetime

        print('#### Tracking Task 1 State ####')

        print('Logging a START time to .csv file')
         # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
        with open("/home/pi/Desktop/LTB_Code_Release/Tracking_1.csv", "a") as f:

            #led.value = True    # turn on LED to indicate writing entries
            print("Time zone 'in':",time_zone_in) #Prints data about to be written to the SD card
            print(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            f.write("%s," % (time_zone_in))    #
            f.write(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            #led.value = False  # turn off LED to indicate we're done

            # Read out all lines in the .csv file to verify the last entry
            #with open("/sd/stamp.csv", "r") as f:
            #print("Printing lines in file:")
            #line = f.readline()
            #while line != '':
            #print(line)
            #line = f.readline()
            t.sleep(3)


    def exit(self, machine):

        global time_zone_in, time_zone_out
        global timestamp_in, timestamp_out

        today = date.today()
        timestamp_out = datetime.now(tz=tz.tzlocal())

        # Track the previous variables
        print('Time Zone of "out" timestamp:',time_zone_out)
        print('"out" timestamp:', timestamp_out)


        State.exit(self, machine)


        # Components of the "time out" stamp
        time_zone_out = timestamp_out.tzname()    # Stores the timezone from datetime
        delta_time = relativedelta(timestamp_out,timestamp_in)

        print('Logging a STOP time to .csv\n')
        # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
        with open("/home/pi/Desktop/LTB_Code_Release/Tracking_1.csv", "a") as f:
            #led.value = True    # turn on LED to indicate writing entries
            print("Time zone 'out':",time_zone_out) #Prints data about to be written to the SD card
            print(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
            print("The time tracked is:", str(delta_time.hours) + ":" + str(delta_time.minutes) + ":" + str(delta_time.seconds))
            print('\n') # Prints a blank line
            f.write("%s," % (time_zone_out))
            f.write(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
            f.write("%d:%d:%02d," % (delta_time.hours,delta_time.minutes,delta_time.seconds))
            #led.value = False  # turn off LED to indicate we're done

            # TEST Option: Read out all lines in the .csv file to verify the last entry
            #with open("/sd/stamp.csv", "r") as f:
            #print("Printing lines in file:")
            #line = f.readline()
            #while line != '':
            #print(line)
            #line = f.readline()

        # Haptic placeholder
        # Sound placeholder 

    def pressed1(self, machine):
        if switch_1.is_pressed:
            machine.go_to_state('Voice Note')

     def pressed2(self, machine):
        if switch_2.is_pressed:
            machine.go_to_state('Voice Note')


########################################
# The "Task #2, Profile 1" state. Begin tracking task 1 in this state
class P1_Tracking2(State):

    #Declare global variables for Tracking1 State
    global time_zone_in, time_zone_out
    global timestamp_in, timestamp_out

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
        return 'Tracking1'

    def enter(self, machine):
        global time_zone_in, time_zone_out
        global timestamp_in, timestamp_out

        today = date.today()
        timestamp_in = datetime.now(tz=tz.tzlocal())


        State.enter(self, machine)


        # Components of the "time in" stamp
        time_zone_in = timestamp_in.tzname()    # Stores the timezone from datetime

        print('#### Tracking Task 1 State ####')

        print('Logging a START time to .csv file')
         # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
        with open("/home/pi/Desktop/LTB_Code_Release/Tracking_1.csv", "a") as f:

            #led.value = True    # turn on LED to indicate writing entries
            print("Time zone 'in':",time_zone_in) #Prints data about to be written to the SD card
            print(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            f.write("%s," % (time_zone_in))    #
            f.write(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            #led.value = False  # turn off LED to indicate we're done

            # Test Option: Read out all lines in the .csv file to verify the last entry
            #with open("/sd/stamp.csv", "r") as f:
            #print("Printing lines in file:")
            #line = f.readline()
            #while line != '':
            #print(line)
            #line = f.readline()
            t.sleep(3)

    def exit(self, machine):

        global time_zone_in, time_zone_out
        global timestamp_in, timestamp_out

        today = date.today()
        timestamp_out = datetime.now(tz=tz.tzlocal())

        # Track the previous variables
        print('Time Zone of "out" timestamp:',time_zone_out)
        print('"out" timestamp:', timestamp_out)


        State.exit(self, machine)


        # Components of the "time out" stamp
        time_zone_out = timestamp_out.tzname()    # Stores the timezone from datetime
        delta_time = relativedelta(timestamp_out,timestamp_in)

        print('Logging a STOP time to .csv\n')
        # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
        with open("/home/pi/Desktop/LTB_Code_Release/Tracking_1.csv", "a") as f:
            #led.value = True    # turn on LED to indicate writing entries
            print("Time zone 'out':",time_zone_out) #Prints data about to be written to the SD card
            print(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
            print("The time tracked is:", str(delta_time.hours) + ":" + str(delta_time.minutes) + ":" + str(delta_time.seconds))
            print('\n') # Prints a blank line
            f.write("%s," % (time_zone_out))
            f.write(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
            f.write("%d:%d:%02d," % (delta_time.hours,delta_time.minutes,delta_time.seconds))
            #led.value = False  # turn off LED to indicate we're done

            # Test Option: Read out all lines in the .csv file to verify the last entry
            #with open("/sd/stamp.csv", "r") as f:
            #print("Printing lines in file:")
            #line = f.readline()
            #while line != '':
            #print(line)
            #line = f.readline()

        # Haptic placeholder
        # Sound placeholder 

    def pressed1(self, machine):
        if switch_1.is_pressed:
            machine.go_to_state('Voice Note')

     def pressed2(self, machine):
        if switch_2.is_pressed:
            machine.go_to_state('Voice Note')


########################################
# The "Profile 2" state. Implement at a later date. Any button press in this state causes a transition to the "Home" state.
class Profile2(State):


    def __init__(self):
        super().__init__()
        self.State = State()


    @property
    def name(self):
        return 'Profile 2'

    def enter(self, machine):
        State.enter(self, machine)

        print('#### Profile 2 State ####')

        t.sleep(2)

    def exit(self, machine):
        State.exit(self, machine)

        # Haptic placeholder
        # Sound placeholder 

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
        return 'Tracking1'

    def enter(self, machine):
        global time_zone_in, time_zone_out
        global timestamp_in, timestamp_out

        today = date.today()
        timestamp_in = datetime.now(tz=tz.tzlocal())


        State.enter(self, machine)


        # Components of the "time in" stamp
        time_zone_in = timestamp_in.tzname()    # Stores the timezone from datetime

        print('#### Tracking Task 1 State ####')

        print('Logging a START time to .csv file')
         # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
        with open("/home/pi/Desktop/LTB_Code_Release/Tracking_1.csv", "a") as f:

            #led.value = True    # turn on LED to indicate writing entries
            print("Time zone 'in':",time_zone_in) #Prints data about to be written to the SD card
            print(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            f.write("%s," % (time_zone_in))    #
            f.write(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            #led.value = False  # turn off LED to indicate we're done

            # Read out all lines in the .csv file to verify the last entry
            #with open("/sd/stamp.csv", "r") as f:
            #print("Printing lines in file:")
            #line = f.readline()
            #while line != '':
            #print(line)
            #line = f.readline()
            t.sleep(3)


    def exit(self, machine):

        global time_zone_in, time_zone_out
        global timestamp_in, timestamp_out

        today = date.today()
        timestamp_out = datetime.now(tz=tz.tzlocal())

        # Track the previous variables
        print('Time Zone of "out" timestamp:',time_zone_out)
        print('"out" timestamp:', timestamp_out)


        State.exit(self, machine)


        # Components of the "time out" stamp
        time_zone_out = timestamp_out.tzname()    # Stores the timezone from datetime
        delta_time = relativedelta(timestamp_out,timestamp_in)

        print('Logging a STOP time to .csv\n')
        # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
        with open("/home/pi/Desktop/LTB_Code_Release/Tracking_1.csv", "a") as f:
            #led.value = True    # turn on LED to indicate writing entries
            print("Time zone 'out':",time_zone_out) #Prints data about to be written to the SD card
            print(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
            print("The time tracked is:", str(delta_time.hours) + ":" + str(delta_time.minutes) + ":" + str(delta_time.seconds))
            print('\n') # Prints a blank line
            f.write("%s," % (time_zone_out))
            f.write(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
            f.write("%d:%d:%02d," % (delta_time.hours,delta_time.minutes,delta_time.seconds))
            #led.value = False  # turn off LED to indicate we're done

            # Read out all lines in the .csv file to verify the last entry
            #with open("/sd/stamp.csv", "r") as f:
            #print("Printing lines in file:")
            #line = f.readline()
            #while line != '':
            #print(line)
            #line = f.readline()

        # Haptic placeholder
        # Sound placeholder 

    def pressed1(self, machine):
        if switch_1.is_pressed:
            machine.go_to_state('Voice Note')

     def pressed2(self, machine):
        if switch_2.is_pressed:
            machine.go_to_state('Voice Note')


########################################
# The "Task #2, Profile 2" state. Begin tracking task 1 in this state
class P2_Tracking2(State):

    #Declare global variables for Tracking1 State
    global time_zone_in, time_zone_out
    global timestamp_in, timestamp_out

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
        return 'Tracking1'

    def enter(self, machine):
        global time_zone_in, time_zone_out
        global timestamp_in, timestamp_out

        today = date.today()
        timestamp_in = datetime.now(tz=tz.tzlocal())


        State.enter(self, machine)


        # Components of the "time in" stamp
        time_zone_in = timestamp_in.tzname()    # Stores the timezone from datetime

        print('#### Tracking Task 1 State ####')

        print('Logging a START time to .csv file')
         # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
        with open("/home/pi/Desktop/LTB_Code_Release/Tracking_1.csv", "a") as f:

            #led.value = True    # turn on LED to indicate writing entries
            print("Time zone 'in':",time_zone_in) #Prints data about to be written to the SD card
            print(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            f.write("%s," % (time_zone_in))    #
            f.write(str(today) + '_' + str(timestamp_in.hour) + ':' + str(timestamp_in.minute) + ":" + str(timestamp_in.second) + ",")
            #led.value = False  # turn off LED to indicate we're done

            # Read out all lines in the .csv file to verify the last entry
            #with open("/sd/stamp.csv", "r") as f:
            #print("Printing lines in file:")
            #line = f.readline()
            #while line != '':
            #print(line)
            #line = f.readline()
            t.sleep(3)


    def exit(self, machine):

        global time_zone_in, time_zone_out
        global timestamp_in, timestamp_out

        today = date.today()
        timestamp_out = datetime.now(tz=tz.tzlocal())

        # Track the previous variables
        print('Time Zone of "out" timestamp:',time_zone_out)
        print('"out" timestamp:', timestamp_out)


        State.exit(self, machine)


        # Components of the "time out" stamp
        time_zone_out = timestamp_out.tzname()    # Stores the timezone from datetime
        delta_time = relativedelta(timestamp_out,timestamp_in)

        print('Logging a STOP time to .csv\n')
        # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
        with open("/home/pi/Desktop/LTB_Code_Release/Tracking_1.csv", "a") as f:
            #led.value = True    # turn on LED to indicate writing entries
            print("Time zone 'out':",time_zone_out) #Prints data about to be written to the SD card
            print(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
            print("The time tracked is:", str(delta_time.hours) + ":" + str(delta_time.minutes) + ":" + str(delta_time.seconds))
            print('\n') # Prints a blank line
            f.write("%s," % (time_zone_out))
            f.write(str(today) + '_' + str(timestamp_out.hour) + ':' + str(timestamp_out.minute) + ":" + str(timestamp_out.second) + ",")
            f.write("%d:%d:%02d," % (delta_time.hours,delta_time.minutes,delta_time.seconds))
            #led.value = False  # turn off LED to indicate we're done

            # Test Option: Read out all lines in the .csv file to verify the last entry
            #with open("/sd/stamp.csv", "r") as f:
            #print("Printing lines in file:")
            #line = f.readline()
            #while line != '':
            #print(line)
            #line = f.readline()

        # Haptic placeholder
        # Sound placeholder 

    def pressed1(self, machine):
        if switch_1.is_pressed:
            machine.go_to_state('Voice Note')

     def pressed2(self, machine):
        if switch_2.is_pressed:
            machine.go_to_state('Voice Note')


################################################################################
# Create the state machine

LTB_state_machine = StateMachine()          # Defines the state machine
LTB_state_machine.add_state(Home())         # Adds the listed states to the machine (Except for the class, "State"
LTB_state_machine.add_state(FocusTimer())
LTB_state_machine.add_state(Profile1())
LTB_state_machine.add_state(P1_Tracking1())
LTB_state_machine.add_state(P1_Tracking2())
LTB_state_machine.add_state(Profile2())
LTB_state_machine.add_state(P2_Tracking1())
LTB_state_machine.add_state(P2_Tracking2())

LTB_state_machine.go_to_state('Home')   #Starts the state machine in the "Home" state

while True:
    switch_1.value               #Checks the switch 1 state each time the loop executes, necessary for button state changes
    switch_2.value               #Checks the switch 1 state each time the loop executes, necessary for button state changes
    LTB_state_machine.pressed()  #Transitions to the StateMachine attrubute, "pressed". Doesn't do much there other than report the current state
