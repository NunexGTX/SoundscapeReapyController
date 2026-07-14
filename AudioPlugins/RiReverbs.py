import json
import reapy
from TrackDiscJockey.SoundTrack import SoundTrack
from abc import abstractmethod
from pathlib import Path
from .SoundEffect import SoundEffect

class RiReverbs(SoundEffect):
    #_RIR_DIR = Path(__file__).parent.parent / "RiRs"
    _param_defaults = [False, "Cinema_Room"]  # [apply_reverb, rir_preset]
    effectParamsList = {}

    _JSON_PATH = Path(__file__).parent.parent / "configs" / "RiReverb.json"

    _RIR_MAP = {
        #Controller Preset : Plugin Preset name
        "Cinema_Room": "CinemaRoomReverb",
        "Parliment":   "ParlimentReverb",
        "Auditorium":  "GulkbenkianReverb",
    }

    try:
        with open(_JSON_PATH) as _f:
            _json_data = json.load(_f)
        if _json_data.get("use_json") and _json_data.get("reverbsRiR"):
            _RIR_MAP = _json_data["reverbsRiR"]
    except Exception as _e:
        print(f"[RiReverbs] Could not load {_JSON_PATH}: {_e}. Using hardcoded presets.")

    def __init__(self, TrackFX: reapy.FX, params=_param_defaults):
        super().__init__(TrackFX)
        self._checkInitialParams(params)
        self.updateSoundEffectParams(params)

    def _checkInitialParams(self, params):
        if len(params) != 2:
            raise ValueError("params must be [apply_reverb: bool, rir_preset: str]")
        if params[1] not in self._RIR_MAP:
            raise ValueError(f"Unknown rir_preset '{params[1]}'. Available: {list(self._RIR_MAP)}")

    def _setInitialParams(self, params):
        self.updateSoundEffectParams(params)

    def updateSoundEffectParams(self, params: list):
        apply_reverb, rir_preset, set_wet = params
        self.setRirPreset(str(rir_preset))
        self.setApplyReverb(bool(apply_reverb))
        self.setWet(float(set_wet))

    def setRirPreset(self, rir_preset: str):
        self.TrackFX.preset = self._RIR_MAP[rir_preset]
        if self.TrackFX.preset != self._RIR_MAP[rir_preset]:
            print(f"[RiReverbs] Could not load preset '{self._RIR_MAP[rir_preset]}'. Create it first in REAPER's FX.")

    def setApplyReverb(self, enabled: bool):
        self.TrackFX.is_enabled = enabled

    @classmethod
    def add_to_track(cls, soundtrack: SoundTrack, params=_param_defaults) -> 'RiReverbs':
        if soundtrack.ambisonic:
            raise ValueError("RiReverbs cannot be applied to ambisonic tracks")
        from .Sparta.MatrixConvReverb import MatrixConvReverb
        SubClass = MatrixConvReverb
        fx = soundtrack.Track.add_fx(SubClass.plugin_name)
        return SubClass(fx, params)
