import reapy
import Reapy.Tracks as reaTracks
import Reapy.Volume as vol
from reapy import reascript_api as RPR

project = reapy.Project()

#Set project to start at 0:00
project.cursor_position = 0

#Set project loop
projectTimeSelection = reapy.TimeSelection(project)
projectTimeSelection.loop()

#Start playing
project.play()

#mute/unmute tracks
project.mute_all_tracks(True)

reaTracks.getTrack_byName(project,"EncoderMonoAudio").unmute()
reaTracks.getTrack_byName(project,"EncoderAmbisonicAudio").unmute()
reaTracks.getTrack_byName(project,"DecoderBinaural").unmute()
reaTracks.getTrack_byName(project,"DecoderAmbisonic").unmute()

track0 = reaTracks.getTrack_byIndex(project,0)
track0.unmute()

#Adjust track volume
track0RPR = RPR.GetTrack(0,track0.index)
RPR.SetMediaTrackInfo_Value(track0RPR,"D_VOL",vol.dBToLinear(6))