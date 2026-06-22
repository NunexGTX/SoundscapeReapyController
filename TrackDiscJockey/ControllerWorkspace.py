from abc import ABC, abstractmethod
import os
from pathlib import Path

class ControllerWorkspace(ABC):
    _soundscape_reapy_controller_dir_flag = "{REAPY_CONTROLLER_DIR}"

    def __init__(self):
        pass

    @classmethod
    def _get_project_file_path(cls, relative_path):
        if cls._soundscape_reapy_controller_dir_flag in relative_path:
            return str(Path(relative_path.replace(cls._soundscape_reapy_controller_dir_flag, cls._get_reapy_controller_dir())))
        else:
            return str(Path(relative_path))

    @staticmethod
    def _get_reapy_controller_dir():
        '''Gets the reapy controller project dir. Should be the root of this project, which is on the previous directory relative to this classe's python file'''
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def _resolve_config_dir(self):
        return (Path(__file__).parent / self._json_location).resolve() 