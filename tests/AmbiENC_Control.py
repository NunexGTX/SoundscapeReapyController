import reapy
import Reapy.Tracks as reapyTracks
import Reapy.FX as reapyFX
from AudioPlugins.Sparta.AmbisonicENCoder import AmbisonicENCoder

#To adjust the speaker adjustment in sparta's ambiENC we can modify its variable's value
#The manual sliders for those are actually shown inside the VST's window if you press the "UI" button
project = reapy.Project()
reapyTracks.showProjectTracks(project) #Take note of the relevant track

ambisonicENCBUSTrack = project._get_track_by_name("EncoderMonoAudio")

print(ambisonicENCBUSTrack.fxs[0].name) #Take note of the fx name, we'll use this for gathering the Sparta's ambisonic vst
print()

print("--- Starting Ambisonic Control Test ---")
print()

ambisonicENC = AmbisonicENCoder(reapyFX.getFX_byName(project,AmbisonicENCoder.plugin_name,ambisonicENCBUSTrack),5)

#Set speaker example positions
ambisonicENC.SpeakersPositions([(180,90),(180,90),(180,90),(180,90),(180,90)])