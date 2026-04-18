import reapy
import time

#Let's start with an hello world print test to check if reapy is working and connecting to reaper as intended
reapy.print("Hello World!") #This hello world happears as a pop up window message on the DAW, ALT+TAB and go check it

#To control the project and its tracks we first have to open the project here in the script
#USING REAPY API
project = reapy.Project() #Gets an object with the current reaper's opened project

project.time_selection.start = 33.1

toggle_time = 1 #Time to play and pause in seconds

while True:
    project.play()
    time.sleep(toggle_time)
    project.pause()
    time.sleep(toggle_time)