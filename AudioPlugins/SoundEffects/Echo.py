import reapy
from .SoundEffect import SoundEffect

class Echo(SoundEffect):
    plugin_name = "VST: ReaDelay (Cockos)"

    effectParamsList = {
        "wet":         0,
        "dry":         1,
        "tap_enabled": 2,
        "delay_ms":    3,
        "feedback":    5,
    }

    _param_defaults = [False, 500, 0.5, 1.0, 1.0]
    # [apply_echo, delay_ms, decay_ratio, dry_mix, wet_mix]

    def __init__(self, TrackFX: reapy.FX, params=_param_defaults):
        super().__init__(TrackFX)
        try:
            self._checkInitialParams(params)
        except ValueError as e:
            print(e)
        self._setInitialParams(params)

    def _checkInitialParams(self, params):
        apply_echo, delay_ms, decay_ratio, dry_mix, wet_mix = params
        if not isinstance(apply_echo, bool):
            raise ValueError(f"apply_echo must be bool, got {type(apply_echo)}")
        if not 0 <= delay_ms <= 2000:
            raise ValueError(f"delay_ms must be 0–2000, got {delay_ms}")
        if not 0.0 <= decay_ratio <= 1.0:
            raise ValueError(f"decay_ratio must be 0.0–1.0, got {decay_ratio}")
        if not 0.0 <= dry_mix <= 1.0:
            raise ValueError(f"dry_mix must be 0.0–1.0, got {dry_mix}")
        if not 0.0 <= wet_mix <= 1.0:
            raise ValueError(f"wet_mix must be 0.0–1.0, got {wet_mix}")

    def _setInitialParams(self, params):
        self.TrackFX.params[2] = 1.0  # Tap 1 always enabled
        self.updateSoundEffectParams(params)

    def updateSoundEffectParams(self, params: list):
        apply_echo, delay_ms, decay_ratio, dry_mix, wet_mix = params
        if not isinstance(apply_echo, bool):
            apply_echo = str(apply_echo).lower() == 'true'
        self.setApplyEcho(apply_echo)
        self.setDelay(float(delay_ms))
        self.setDecayRatio(float(decay_ratio))
        self.setDryMix(float(dry_mix))
        self.setWetMix(float(wet_mix))

    def setApplyEcho(self, enabled: bool):
        self.TrackFX.is_enabled = enabled

    def setDelay(self, delay_ms: float):
        if not 0 <= delay_ms <= 10000:
            raise ValueError(f"delay_ms must be 0–10000, got {delay_ms}")
        self.TrackFX.params[3] = self._param_val_calc(delay_ms, 0, 10000)

    def setDecayRatio(self, ratio: float):
        if not 0.0 <= ratio <= 1.0:
            raise ValueError(f"decay_ratio must be 0.0–1.0, got {ratio}")
        self.TrackFX.params[5] = self._param_val_calc(ratio,0,1) #more than 1 and audio starts to clip

    def setDryMix(self, value: float):
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"dry_mix must be 0.0–1.0, got {value}")
        self.TrackFX.params[1] = self._param_double_val_calc(value,0,1)

    def setWetMix(self, value: float):
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"wet_mix must be 0.0–1.0, got {value}")
        self.TrackFX.params[0] = self._param_double_val_calc(value,0,1)
