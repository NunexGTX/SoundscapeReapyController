import reapy
import reapy_samples.reaperShowTracks as reapt_showTracks
from Sparta.Ambisonic import Ambisonic

#To adjust the speaker adjustment in sparta's ambiENC we can modify its variable's value
#The manual sliders for those are actually shown inside the VST's window if you press the "UI" button
project = reapy.Project()
reapt_showTracks.showProjectTracks(project) #Take note of the relevant track

print(reapy.Track(2,project).fxs[0].name) #Take not of the fx name, we'll use this for gathering the Sparta's ambisonic vst
print()

print("--- Starting Ambisonic Control Test ---")
print()

ambisonic = Ambisonic(Ambisonic.ambisonicFX(2),5)

#Set speaker example positions
ambisonic.SpeakersPositions([(180,90),(180,90),(180,90),(180,90),(180,90)])