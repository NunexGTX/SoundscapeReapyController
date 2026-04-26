import reapy
import Reapy.Tracks as reapyTracks
import Reapy.FX as reapyFX
from Sparta.Ambisonic import AmbisonicENCoder

#To adjust the speaker adjustment in sparta's ambiENC we can modify its variable's value
#The manual sliders for those are actually shown inside the VST's window if you press the "UI" button
project = reapy.Project()
reapyTracks.showProjectTracks(project) #Take note of the relevant track

print(reapy.Track(2,project).fxs[0].name) #Take note of the fx name, we'll use this for gathering the Sparta's ambisonic vst
print()

print("--- Starting Ambisonic Control Test ---")
print()

ambisonic = AmbisonicENCoder(reapyFX.getFX_byName(AmbisonicENCoder.ambisonic_plugin_name,2),5)

#Set speaker example positions
ambisonic.SpeakersPositions([(180,90),(180,90),(180,90),(180,90),(180,90)])