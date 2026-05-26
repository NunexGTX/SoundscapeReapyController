from abc import ABC, abstractmethod
import os
from pathlib import Path

class jsonDealer(ABC):

    def __init__(self):
        pass

    def _get_reapy_controller_dir(self):
        '''Gets the reapy controller project dir. Should be the root of this project, which is on the previous directory relative to this classe's python file'''
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def _resolve_config_dir(self):
        return (Path(__file__).parent / self._json_location).resolve() 
    
    @abstractmethod
    def _ReadJson(self):
        pass