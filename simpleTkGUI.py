# File name: simpleTkGUI.py
# Attempting to use this working example as inspiration for the ltb
# The code is being tested and debugged, 2022-10-09, Connor Sheeran

# This code has been written by Robu.in
# visit https://robu.in for more information
# https://robu.in/developing-simple-gui-using-tkinter-to-control-gpios-of-raspberry-pi/

import tkinter as Tk   # importing Tkinter Library
# import tkFont
import RPi.GPIO as GPIO   # importing GPIO library

GPIO.setmode(GPIO.BOARD)  # setting up the GPIO pins
GPIO.setup(37, GPIO.OUT)  # setting pin37 as output pin
GPIO.output(37, GPIO.LOW)  # setting pin37 as LOW initially
GPIO.setup(38, GPIO.OUT)  # setting pin38 as output pin
GPIO.output(38, GPIO.LOW)  # setting pin38 as LOW initially

win = Tk()  # setting up window from Tk() naming win

# myFont = tkFont.Font(family='Helvetica', size=36, weight='bold')  # setting up font naming myfont

def led1ON():  # defining function led1ON
    print("LED1 button pressed")  # to be printed on terminal
    if GPIO.input(37) :
        GPIO.output(37, GPIO.LOW)  # setting pin37 to low
        led1Button["text"] = "LED 1 ON"  # text for led1Button

    else:
        GPIO.output(37, GPIO.HIGH)  # setting pin37 to high
        led1Button["text"] = "LED 1 OFF"  # text for led1Button

def led2ON():
    print("LED2 button pressed")
    if GPIO.input(38) :
        GPIO.output(38, GPIO.LOW)  # setting pin38 to low
        led2Button["text"] = "LED 2 ON"  # text for led2Button
    else:
        GPIO.output(38, GPIO.HIGH)  # setting pin38 to high
        led2Button["text"] = "LED 2 OFF"  # text for led2Button

def exitProgram():
    print("Exit Button pressed")
    GPIO.cleanup()  # Quitting program
    win.quit()

win.title("My GUI")  # title for window
win.geometry('800x300')  # Dimensions of the window

exitButton = Button(win, text="Exit", font=myFont, command=exitProgram, height=2 , width=6)  # setting button naming exitbutton 
exitButton.pack(side=BOTTOM)  # button position for exitbutton #commanding to button to exitProgram

led1Button = Button(win, text="LED 1 ON", font=myFont, command=led1ON, height=2, width=8)  # setting button naming led1Button
led1Button.place(x=37, y=50)  # button position for led1Button #commanding to button to led1ON function

led2Button = Button(win, text="LED 2 ON", font=myFont, command=led2ON, height=2, width=8)  # setting button naming led2Button
led2Button.place(x=520, y=50)  # button position for led2Button #commanding to button to led2ON function

mainloop()  # commanding mainloop for starting main loop