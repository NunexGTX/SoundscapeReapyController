import reapy
from ..SoundEffect import SoundEffect

class HighLowPassFilter(SoundEffect):
    plugin_name = "JS: RBJ Highpass/Lowpass Filters"

    effectParamsList = {
        "hpf": 0,
        "lpf": 1,
    }

    _param_defaults = [False, 0.0, 22000.0]
    # [apply_filter, highPassVal, lowPassVal]

    def __init__(self, TrackFX: reapy.FX, params=_param_defaults):
        super().__init__(TrackFX)
        self._hp_freq = 0.0
        self._lp_freq = 22000.0
        try:
            self._checkInitialParams(params)
        except ValueError as e:
            print(e)
        self._setInitialParams(params)

    def _checkInitialParams(self, params):
        pass

    def _setInitialParams(self, params):
        self.updateSoundEffectParams(params)

    def updateSoundEffectParams(self, params: list):
        apply_filter, hp_val, lp_val = params
        if not isinstance(apply_filter, bool):
            apply_filter = str(apply_filter).lower() == 'true'
        self.setApplyFilter(apply_filter)
        self.setHighPassFreq(float(hp_val))
        self.setLowPassFreq(float(lp_val))

    def setApplyFilter(self, enabled: bool):
        self.TrackFX.is_enabled = enabled

    def setHighPassFreq(self, freq: float):
        freq = max(0.0, min(freq, 1000.0))
        self._hp_freq = freq
        self.TrackFX.params[0] = freq

    def setLowPassFreq(self, freq: float):
        freq = max(1000.0, min(freq, 22000.0))
        self._lp_freq = freq
        self.TrackFX.params[1] = freq
