import math
import reapy
from ..SoundEffect import SoundEffect

class Occlusion(SoundEffect):
    plugin_name = "VST: ReaEQ (Cockos)"

    effectParamsList = {
        "gain_low":    1,
        "gain_low_mid": 4,
        "gain_mid":    7,
        "gain_high":  10,
        "global_gain": 15,
    }

    _PLUGIN_GAIN_RANGE = (-150, 12)  # actual ReaEQ gain slider range, used for reapy normalization
    _GAIN_RANGE = (-150, 0)          # our working range: attenuate only, no boost
    _FREQ_RANGE = (20, 22050)  # ReaEQ frequency slider range in Hz (log-scale)

    _param_defaults = [False, False, 1.0, 1.0, 1.0, 1.0]
    # [apply_occlusion, frequency_dependent, general_occlusion, low_freq, mid_freq, high_freq]

    def __init__(self, TrackFX: reapy.FX, params=_param_defaults):
        super().__init__(TrackFX)
        self._general_occlusion = 1.0
        self._low_freq = 1.0
        self._mid_freq = 1.0
        self._high_freq = 1.0
        self._frequency_dependent = False
        try:
            self._checkInitialParams(params)
        except ValueError as e:
            print(e)
        self._initFixedParams()
        self._setInitialParams(params)

    def _checkInitialParams(self, params):
        apply_occ, freq_dep, general, low, mid, high = params
        if not isinstance(apply_occ, bool):
            raise ValueError(f"apply_occlusion must be bool, got {type(apply_occ)}")
        if not isinstance(freq_dep, bool):
            raise ValueError(f"frequency_dependent must be bool, got {type(freq_dep)}")
        for name, val in [("general_occlusion", general), ("low_freq", low), ("mid_freq", mid), ("high_freq", high)]:
            if not 0.0 <= val <= 1.0:
                raise ValueError(f"{name} must be 0.0–1.0, got {val}")

    def _log_freq_normalize(self, freq: float) -> float:
        f_min, f_max = self._FREQ_RANGE
        return math.log10(freq / f_min) / math.log10(f_max / f_min)

    def _initFixedParams(self):
        self.TrackFX.params[0] = self._log_freq_normalize(800)               # Band 1 → 800 Hz (Low Shelf)
        self.TrackFX.params[3] = self._log_freq_normalize(800)               # Band 2 parked at 800 Hz
        self.TrackFX.params[4] = self._param_val_calc(0, *self._PLUGIN_GAIN_RANGE)  # Band 2 gain locked at 0 dB
        self.TrackFX.params[6] = self._log_freq_normalize(2000)              # Band 3 → 2000 Hz (Mid Peak)
        self.TrackFX.params[9] = self._log_freq_normalize(8000)              # Band 4 → 8000 Hz (High Shelf)

    def _setInitialParams(self, params):
        self.updateSoundEffectParams(params)

    def updateSoundEffectParams(self, params: list):
        apply_occ, freq_dep, general, low, mid, high = params
        if not isinstance(apply_occ, bool):
            apply_occ = str(apply_occ).lower() == 'true'
        if not isinstance(freq_dep, bool):
            freq_dep = str(freq_dep).lower() == 'true'
        self.setApplyOcclusion(apply_occ)
        self.setFrequencyDependent(freq_dep)
        self.setGeneralOcclusion(float(general))
        self.setLowFreq(float(low))
        self.setMidFreq(float(mid))
        self.setHighFreq(float(high))

    def _applyBands(self):
        attenuation_range = abs(self._GAIN_RANGE[0])  # 150
        db = (self._general_occlusion - 1.0) * attenuation_range
        self.TrackFX.params[15] = self._param_val_calc(db, *self._PLUGIN_GAIN_RANGE)

        if self._frequency_dependent:
            for idx, freq in [(1, self._low_freq),(4,self._low_freq), (7, self._mid_freq), (10, self._high_freq)]:
                combined = self._general_occlusion * freq
                db = (combined - 1.0) * attenuation_range
                self.TrackFX.params[idx] = self._param_val_calc(db, *self._PLUGIN_GAIN_RANGE)
        else:
            zero_db = self._param_val_calc(0, *self._PLUGIN_GAIN_RANGE)
            for idx in [1, 7, 10]:
                self.TrackFX.params[idx] = zero_db

    def setApplyOcclusion(self, enabled: bool):
        self.TrackFX.is_enabled = enabled

    def setFrequencyDependent(self, enabled: bool):
        self._frequency_dependent = enabled
        self._applyBands()

    def setGeneralOcclusion(self, value: float):
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"general_occlusion must be 0.0–1.0, got {value}")
        self._general_occlusion = value
        self._applyBands()

    def setLowFreq(self, value: float):
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"low_freq must be 0.0–1.0, got {value}")
        self._low_freq = value
        self._applyBands()

    def setMidFreq(self, value: float):
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"mid_freq must be 0.0–1.0, got {value}")
        self._mid_freq = value
        self._applyBands()

    def setHighFreq(self, value: float):
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"high_freq must be 0.0–1.0, got {value}")
        self._high_freq = value
        self._applyBands()
