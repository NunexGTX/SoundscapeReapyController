import base64
from pathlib import Path
from reapy import reascript_api as RPR
from ..RiReverbs import RiReverbs

class ReverbRIR(RiReverbs):
    plugin_name  = "VST: ReaVerb (Cockos)"
    _PRESET_NAME = "RiReverb"
