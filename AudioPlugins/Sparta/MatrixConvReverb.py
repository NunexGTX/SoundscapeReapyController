import base64
from pathlib import Path
from reapy import reascript_api as RPR
from ..RiReverbs import RiReverbs

class MatrixConvReverb(RiReverbs):
    plugin_name  = "VST: sparta_matrixconv (AALTO) (64ch)"
    _PRESET_NAME = "AmbisonicReverbConvolve"