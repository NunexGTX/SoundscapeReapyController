import reapy
from ..AudioPluginController import AudioPluginController

class AmbisonicDECoder(AudioPluginController):
    plugin_name = "VST: sparta_ambiDEC (AALTO) (64ch)"

    _param_defaults = [1]

    __inputOrder_range = (1,10)

    def __init__(self,TrackFX: reapy.FX, ambisonic_order: int = 1,params = _param_defaults):
        super().__init__(TrackFX)
        try:
            self._checkInitialParams(params)
        except ValueError as e:
            print(e)
        self.__setInputOrder(ambisonic_order)
        
    def _setInitialParams(self,params):
        self.__setInputOrder(params[0])

    def __setInputOrder(self,inputOrder_val):
        self.TrackFX.params[0] = self._param_val_calc(inputOrder_val,self.__inputOrder_range[0],self.__inputOrder_range[1])

    '''Check functions'''
    def _checkInitialParams(self, params):
        if not self.__inputOrder_range[0] <= params[0] <= self.__inputOrder_range[1]:
            raise ValueError(f"The Input Order of the ambisonic output must be between the values {self.__outputOrder_range[0]} and {self.__outputOrder_range[1]}")