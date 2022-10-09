#integrate simpleTkGuI & digiclock

# File name: simpleTkGUI.py
# Attempting to use this working example as inspiration for the ltb
# The code is being tested and debugged, 2022-10-09, Connor Sheeran
# This code successfully displays a GUI on the Raspberry PiTFT screen using a Pi400 (not yet PiZero W).
# The GUI interacts well with the screen buttons and externial GPIO outputs

# This code was initially inspired by:
# https://robu.in/developing-simple-gui-using-tkinter-to-control-gpios-of-raspberry-pi/


import tkinter as tk
from tkinter import *
from tkinter import Tk, Label, Button, font
import time
import sys
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)  # setting up the GPIO pins
# Setting up LED1
GPIO.setup(13, GPIO.OUT)  # setting pin13 as output pin NOT GPIO 13
GPIO.output(13, GPIO.LOW)  # setting pin13 as LOW initially
# Setting up LED2
GPIO.setup(15, GPIO.OUT)  # setting pin23 as output pin NOT GPIO 155
GPIO.output(15, GPIO.LOW)  # setting pin23 as LOW initially

win = Tk()  # setting up window from Tk() naming win
myFont = font.Font(family='Helvetica', size=18, weight='bold')  # setting up font naming myfont
# Define the tkinter window instance
win.title("ltb Home")  # title for window
win.geometry('400x300')  # Dimensions of the window, 320x240 is the dimensions of the adafruit PiTFT capacitive screen
win.eval('tk::PlaceWindow . center')  #Place the window in the center of the screen, Q: is the Raspberry Screen setup correctly?
win.attributes('-fullscreen', True)

#root.config(bg="white")

# Clock function, global display
def get_time():
    time_Var = time.strftime("%I:%M %p")
    date_Var = time.strftime("%Y-%m-%d")
    clock.config(text= time_Var)
    date.config(text= date_Var)
    clock.after(200, get_time)

def SW1ON():  # defining function led1ON
    print("SW1 button pressed")  # to be printed on terminal
    if GPIO.input(13) :
        GPIO.output(13, GPIO.LOW)  # setting pin13 to low
        SW1Button["text"] = "SW 1 OFF"  # text for led1Button
    else:
        GPIO.output(13, GPIO.HIGH)  # setting pin13 to high
        SW1Button["text"] = "SW 1 ON"  # text for led1Button

def SW2ON():
    print("SW2 button pressed")
    if GPIO.input(15) :
        GPIO.output(15, GPIO.LOW)  # setting pin15 to low
        SW2Button["text"] = "SW 2 OFF"  # text for led2Button
    else:
        GPIO.output(15, GPIO.HIGH)  # setting pin15 to high
        SW2Button["text"] = "SW 2 ON"  # text for led2Button

def exitProgram():
    print("Exit Button pressed")
    GPIO.cleanup()  # Quitting program
    win.destroy()  # This was previously win.quit(), but doesn't close the window

# Display Parameters for the Clock
clock = Label(win, font= ("Calibri",10), bg="white", fg="black")
clock.place(x=34, y=20)
clkText= Label(text="Time:",font= ("Calibri",10), bg="white", fg="black")
clkText.place(x=2, y=20)

date = Label(win, font= ("Calibri",10), bg="white", fg="black")
date.place(x=34, y=2)
dteText= Label(text="Date:",font= ("Calibri",10), bg="white", fg="black")
dteText.place(x=2, y=2)
get_time()

# Define the tkinter button instance(s)
# Focus Button
Fbtn = tk.Button(win, text="Focus",font= ("Calibri",10), bg="white", fg="black")
Fbtn.place(x=260, y=2)

exitButton = Button(win, text="Exit", font=myFont, command=exitProgram, height=2 , width=6)  # setting button naming exitbutton
exitButton.pack(side=BOTTOM, anchor=SE)  # button position for exitbutton #commanding to button to exitProgram

SW1Button = Button(win, text="SW 1 OFF", font=myFont, command=SW1ON, height=2, width=8)  # setting button naming led1Button
#SW1Button.place(x=37, y=50)  # button position for led1Button #commanding to button to led1ON function
SW1Button.pack(side=LEFT, anchor=W)

SW2Button = Button(win, text="SW 2 OFF", font=myFont, command=SW2ON, height=2, width=8)  # setting button naming led2Button
#SW2Button.place(x=520, y=50)  # button position for led2Button #commanding to button to led2ON function
SW2Button.pack(side=RIGHT, anchor=E)


mainloop()  # commanding mainloop for starting main loop
