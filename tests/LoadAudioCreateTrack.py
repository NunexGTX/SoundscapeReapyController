from reapy import reascript_api as RPR
import Reapy.Tracks as ReaperTracks
import reapy

#reapy.open_project()
project = reapy.Project()

#Put the cursor at 0 and insert the sound
project.cursor_position = 0
#RPR.InsertMedia("~/ReapyControler/Sounds/thunders2.wav",1) #creates a track which its name is the same as the sound file name

#Try to adjust the insert sound's lenght
Track0 = ReaperTracks.getTrack_byIndex(project,0)
Track0.items[0].length = 1000