import reapy
from abc import abstractmethod
from pathlib import Path
from .AudioPluginController import AudioPluginController
from .SoundEffects.ReverbRIR import ReverbRIR
from .Sparta.MultiConvReverb import MultiConvReverb

class RiReverbs(AudioPluginController):
    _RIR_DIR = Path(__file__).parent / "RiRs"
    _param_defaults = [False]
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

    def __init__(self, TrackFX: reapy.FX, rir_preset: str, ambisonic: bool, params=_param_defaults):
        super().__init__(TrackFX)
        self._ambisonic = ambisonic
        self._checkInitialParams(params)
        self._load_rir_preset(rir_preset)
        self._setInitialParams(params)

    def _checkInitialParams(self, params):
        if len(params) != 1 or not isinstance(params[0], bool):
            raise ValueError("params must be [apply_reverb: bool]")

    def _setInitialParams(self, params):
        self.updateSoundEffectParams(params)

    def updateSoundEffectParams(self, params: list):
        self.setApplyReverb(params[0])

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
    def create(cls, ambisonic: bool, TrackFX: reapy.FX, rir_preset: str, params=None):
        RiReverb = MultiConvReverb if ambisonic else ReverbRIR
        return RiReverb(TrackFX, rir_preset, ambisonic) if params is None else RiReverb(TrackFX, rir_preset, ambisonic, params)
