import reapy
from abc import abstractmethod
from pathlib import Path
from .SoundEffect import SoundEffect
from .SoundEffects.ReverbRIR import ReverbRIR
from .Sparta.MultiConvReverb import MultiConvReverb

class RiReverbs(SoundEffect):
    _RIR_DIR = Path(__file__).parent / "RiRs"
    _param_defaults = [False, False, "Cinema_Room"]  # [apply_reverb, ambisonic, rir_preset]
    effectParamsList = {}

    _RIR_MAP = {
        "Cinema_Room": {
            "stereo":    "Casa_do_Cinema_Manoel_de_Oliveira-Stereo_Binaural_IR_Pos5_N19_Cin.wav",
            "ambisonic": "Casa_do_Cinema_Manoel_de_Oliveira-Ambisonics_B_IR_Pos5_N19_Cin.wav",
        },
        "Parliment": {
            "stereo":    "Assembleia_da_Republica-Stereo_Binaural_IR_SCALED_S1_Pos5.wav",
            "ambisonic": "Assembleia_da_Republica-Ambisonics_B_IR_SCALED_S1_Pos5_(ACN-SN3D-1).wav",
        },
    }

    _SUBDIRS = {
        False: "Stereo",
        True:  "Ambisonic/1stOrder",
    }

    def __init__(self, TrackFX: reapy.FX, params=_param_defaults):
        super().__init__(TrackFX)
        self._checkInitialParams(params)
        self.updateSoundEffectParams(params)

    def _checkInitialParams(self, params):
        if len(params) != 3:
            raise ValueError("params must be [apply_reverb: bool, ambisonic: bool, rir_preset: str]")
        if not isinstance(params[0], bool):
            raise ValueError(f"apply_reverb must be bool, got {type(params[0])}")
        if not isinstance(params[1], bool):
            raise ValueError(f"ambisonic must be bool, got {type(params[1])}")
        if params[2] not in self._RIR_MAP:
            raise ValueError(f"Unknown rir_preset '{params[2]}'. Available: {list(self._RIR_MAP)}")

    def _setInitialParams(self, params):
        self.updateSoundEffectParams(params)

    def updateSoundEffectParams(self, params: list):
        apply_reverb, ambisonic, rir_preset = params
        self._ambisonic = ambisonic
        self.setRirPreset(rir_preset)
        self.setApplyReverb(apply_reverb)

    def setRirPreset(self, rir_preset: str):
        self._load_rir_preset(rir_preset)

    def setApplyReverb(self, enabled: bool):
        self.TrackFX.is_enabled = enabled

    def _get_rir_path(self, rir_preset: str) -> Path:
        if rir_preset not in self._RIR_MAP:
            raise ValueError(
                f"Unknown RIR preset '{rir_preset}'. Available: {list(self._RIR_MAP)}"
            )
        rir_type = "ambisonic" if self._ambisonic else "stereo"
        return self._RIR_DIR / self._SUBDIRS[self._ambisonic] / self._RIR_MAP[rir_preset][rir_type]

    @abstractmethod
    def _patch_chunk_paths(self, chunk_bytes: bytes, path_map: dict) -> bytes:
        pass

    @abstractmethod
    def _load_rir_preset(self, rir_preset: str):
        pass

    @classmethod
    def add_to_track(cls, track: reapy.Track, params=_param_defaults) -> 'RiReverbs':
        _, ambisonic, _ = params
        SubClass = MultiConvReverb if ambisonic else ReverbRIR
        fx = track.add_fx(SubClass.plugin_name)
        return SubClass(fx, params)

    @classmethod
    def create(cls, TrackFX: reapy.FX, params=_param_defaults) -> 'RiReverbs':
        _, ambisonic, _ = params
        SubClass = MultiConvReverb if ambisonic else ReverbRIR
        return SubClass(TrackFX, params)
