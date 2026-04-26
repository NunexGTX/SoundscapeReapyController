from reapy import reascript_api as RPR
import reapy

project = reapy.Project()
reapy.Track()

#Put the cursor at 0 and insert the sound
project.cursor_position = 0
RPR.InsertMedia("/Users/nunex/ReapyControler/Sounds/thunders2.wav",1) #creates a track which its name is the same as the sound file name