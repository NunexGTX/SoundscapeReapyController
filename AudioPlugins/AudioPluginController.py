from abc import ABC, abstractmethod
import reapy

class AudioPluginController(ABC):
    sliderVals = (0,1) #This represents in between which values each parameter must be

    '''Abstract Variables'''
    @property
    @abstractmethod
    def plugin_name(self) -> str:
        pass

    @property
    @abstractmethod
    def _param_defaults(self) -> list:
        pass
    
    '''Constructor'''
    def __init__(self, TrackFX: reapy.FX):
        self.TrackFX = TrackFX

    '''Abstract Methods'''
    @abstractmethod
    def _checkInitialParams(self,params):
        pass

    @abstractmethod
    def _setInitialParams(self,params):
        pass
    
    '''Common Methods'''    
    def _param_val_calc(self,x,min_val,max_val):
        #This uses the formula : (x-xmin)/(xmax-xmin) to rescale the values from 0 to 1
        return (x-min_val)/(max_val-min_val)

    

