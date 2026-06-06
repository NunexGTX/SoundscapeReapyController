from abc import abstractmethod
import reapy
from .AudioPluginController import AudioPluginController

class SoundEffect(AudioPluginController):
    effectParamsList = None  # subclasses must declare this dict

    @classmethod
    def add_to_track(cls, track: reapy.Track, initial_params: list = None) -> 'SoundEffect':
        fx = track.add_fx(cls.plugin_name)
        return cls(fx, initial_params)

    def remove_from_track(self):
        self.TrackFX.delete()

    @abstractmethod
    def updateSoundEffectParams(self, params: list):
        pass
