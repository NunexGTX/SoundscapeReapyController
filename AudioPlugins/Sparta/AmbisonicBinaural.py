import reapy
from ..AudioPluginController import AudioPluginController

class AmbisonicBINaural(AudioPluginController):
    plugin_name = "VST: sparta_ambiBIN (AALTO) (64ch)"

    _param_defaults = [1]

    __inputOrder_range = (1,10)

    __rotation_range = (-180,180)

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
        
    def rotation(self,yaw: float,pitch: float,roll: float):
        self.__check_rotation_value(yaw)
        self.__check_rotation_value(pitch)
        self.__check_rotation_value(roll)
        self.__set_yaw(yaw)
        self.__set_pitch(pitch)
        self.__set_roll(roll)
        

    def __set_yaw(self,yaw: float):
        self.TrackFX.params[10] = self._param_val_calc(yaw,self.__rotation_range[0],self.__rotation_range[1])

    def __set_pitch(self, pitch: float):
        self.TrackFX.params[11] = self._param_val_calc(pitch,self.__rotation_range[0],self.__rotation_range[1])

    def __set_roll(self, roll: float):
        self.TrackFX.params[12] = self._param_val_calc(roll,self.__rotation_range[0],self.__rotation_range[1])

    def __check_rotation_value(self, rotation_value: float):
        if not self.__rotation_range[0] <= rotation_value <= self.__rotation_range[1]:
            raise ValueError(f"Rotation value of {rotation_value} is invalid. Please insert a value between {self.__rotation_range[0]} and {self.__rotation_range[1]}")