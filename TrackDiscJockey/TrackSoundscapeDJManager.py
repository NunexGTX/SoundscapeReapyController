import reapy
from ..jsonUtils.SoundscapeReapyControllerConfig import SoundscapeReapyControllerConfig

class TrackSoundscapeDJManager:

    def __init__(self,project: reapy.Project, reapy_controller_config: SoundscapeReapyControllerConfig, ):
        self.__project = project
        self.__reapy_controller_config = reapy_controller_config