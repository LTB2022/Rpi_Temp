import tkinter
import tkinter.messagebox
import customtkinter
import time
import sys

# Set inital appearance and window----------------------------------------------------------
customtkinter.set_appearance_mode("light")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

app = customtkinter.CTk()  # create CTk window like you do with the Tk window
app.geometry("320x240")

def __init__(app):
    super().__init__()

def button_function():
    print("button pressed")

# Frame for the profie buttons----------------------------------------------------------------
# Placed up front to avoid any text crossover
app.frame = customtkinter.CTkFrame(master=app,
                                   width=320,
                                   height=180,
                                   corner_radius=8)
app.frame.place(relx=0.5, rely=0.62, anchor=tkinter.CENTER)

# Clock function, global display-------------------------------------------------------------------------------
def get_time():
    time_Var = time.strftime("%I:%M %p")
    date_Var = time.strftime("%Y-%m-%d")
    clock.configure(text= time_Var)
    date.configure(text= date_Var)
    clock.after(200, get_time)

datetxt = customtkinter.CTkLabel(master=app, text="Date:")
datetxt.place(relx=-0.15, rely=-0.01, anchor=tkinter.NW)
date = customtkinter.CTkLabel(master=app,
                              width=60,
                              height=25)
date.place(relx=0.13, rely=0.00, anchor=tkinter.NW)

clkText= customtkinter.CTkLabel(master=app, text="Time:")
clkText.place(relx=-0.15, rely=0.08, anchor=tkinter.NW)
clock = customtkinter.CTkLabel(master=app,
                               width=60,
                               height=25)
clock.place(relx=0.13, rely=0.09, anchor=tkinter.NW)
get_time()

# Little Time Buddy Label--------------------------------------------------------------------------------------
LTB_label = tkinter.StringVar(value="LTB\n" +
                             "Litte Time Buddy")
label = customtkinter.CTkLabel(master=app,
                               textvariable=LTB_label,
                               width=120,
                               height=25,
                               fg_color=("white", "black"),
                               corner_radius=4,
                               )
label.place(relx=0.82, rely=0.06, anchor=tkinter.CENTER)
#--------------------------------------------------------------------------------------------------------------
# Focus Button
button = customtkinter.CTkButton(master=app, text="Focus",
                                 width=120,
                                 height=25,
                                 text_font=("Ubuntu", -12),
                                 corner_radius=4,
                                 command=button_function)
button.place(relx=0.63, rely=0.14, anchor=customtkinter.NW)

# Profile Buttons
button = customtkinter.CTkButton(master=app, text="EE Intern", command=button_function)
button.place(relx=0.55, rely=0.8, anchor=customtkinter.W)

button = customtkinter.CTkButton(master=app, text="CSUS 193B", command=button_function)
button.place(relx=0.45, rely=0.8, anchor=customtkinter.E)
#--------------------------------------------------------------------------------------------------------------
app.mainloop()
