from abc import ABC, abstractmethod
import reapy
from reapy import reascript_api as RPR
import re
import base64

class AudioPluginController(ABC):
    sliderVals = (0,1) #This represents in between which values each parameter must be

    _wet_range = (0,1)

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
    
    def _param_double_val_calc(self,x,min_val,max_val):
        #Used for parameters that go from 0 to 2 (like db parameters less than 1 are negatives more than 1 are positives)
        return self._param_val_calc(x,min_val,max_val)*2

    def _param_val_calc_discrete(self,x,min_val,max_val):
        #Grid-aligned normalization for DISCRETE integer params (values min_val..max_val).
        #_param_val_calc gives (x-min)/(max-min), which lands each integer exactly on the
        #plugin's floor() decode boundary. Hosts that quantize to a coarse grid (REAPER 7.17
        #snaps to 1/128) nudge that boundary value just below the floor() threshold, so it
        #resolves one step low. (x-min+1)/count sits ON the 1/count grid (nothing to snap)
        #and still floor-decodes to x via min + floor(norm*(count-1)).
        count = max_val-min_val+1
        return (x-min_val+1)/count
    
    def setWet(self, wet: float):
        self.TrackFX.params[self._WET_INDEX] = self._param_val_calc(wet, self._wet_range[0], self._wet_range[1])

    

