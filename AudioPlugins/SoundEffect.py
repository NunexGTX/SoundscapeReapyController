from abc import abstractmethod
#from TrackDiscJockey.SoundTrack import SoundTrack #Avoid circular import, it was only used for a variable type check
from .AudioPluginController import AudioPluginController

class SoundEffect(AudioPluginController):
    effectParamsList = None  # subclasses must declare this dict

    @classmethod
    def add_to_track(cls, soundtrack, initial_params: list = None) -> 'SoundEffect':
        track = soundtrack.Track
        fx = track.add_fx(cls.plugin_name)
        return cls(fx, initial_params)

    def remove_from_track(self):
        self.TrackFX.delete()

    @abstractmethod
    def updateSoundEffectParams(self, params: list):
        pass
