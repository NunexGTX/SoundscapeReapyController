from reapy import Track
from AudioPlugins.SoundEffects.SoundEffect import SoundEffect
import mutagen #To get audio file time
from jsonUtils.AudioData import AudioData
from uuid import UUID

class SoundTrack:
    
    def __init__(self, audioData: AudioData, soundUUID: UUID, track: Track, delay: int, loop: bool):
        self.AudioData = audioData
        self.SoundUUID = soundUUID
        self.AudioID = audioData.sound_id
        self.Track = track
        self.ambisonic = audioData.ambisonic
        self.SoundEffects = []
        self.muteState = True
        self.audio_duration_seconds = track.items[0].length #There should only be 1 audio file in each track
        self.positionalRot = (0.0, 0.0)   # azim, elevation — center by default
        self.distanceRadius = 1.0          # 1m = 0dB reference
        self.VolumeGain = 0.0 #Volume factor
        self.currentVolumeDB = 0.0
        self.ambiSourceIndex = None
        self.delay = delay
        self.loop = loop

    def mute(self):
        self.muteState = True
        self.Track.mute()

    def unmute(self):
        self.muteState = False
        self.Track.unmute()

    def newSoundEffect(self, soundFX: SoundEffect):
        self.SoundEffects.append(soundFX)

    def deleteSoundEffect(self, soundFX: SoundEffect):
        soundFX.remove_from_track()
        self.SoundEffects.remove(soundFX)

