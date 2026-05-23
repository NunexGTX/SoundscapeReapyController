from abc import abstractmethod
import reapy
from ..AudioPluginController import AudioPluginController

class SoundEffect(AudioPluginController):
    effectParamsList = None  # subclasses must declare this dict

    @classmethod
    def add_to_track(cls, track: reapy.Track, *args, **kwargs) -> 'SoundEffect':
        fx = track.add_fx(cls.plugin_name)
        return cls(fx, *args, **kwargs)

    def remove_from_track(self):
        self.TrackFX.delete()

    @abstractmethod
    def updateSoundEffectParams(self, params: list):
        pass
