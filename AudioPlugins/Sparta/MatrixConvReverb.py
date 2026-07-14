import base64
import reapy
from pathlib import Path
from reapy import reascript_api as RPR
from ..RiReverbs import RiReverbs

class MatrixConvReverb(RiReverbs):
    plugin_name  = "VST: sparta_matrixconv (AALTO) (64ch)"
    _PRESET_NAME = "AmbisonicReverbConvolve"

    _WET_INDEX   = 3

    @classmethod
    def add_to_track(cls, track: reapy.Track, params=RiReverbs._param_defaults) -> 'MatrixConvReverb':
        fx = track.add_fx(cls.plugin_name)
        return cls(fx, params)