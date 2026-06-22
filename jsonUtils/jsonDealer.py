from abc import abstractmethod
from TrackDiscJockey.ControllerWorkspace import ControllerWorkspace

class jsonDealer(ControllerWorkspace):

    def __init__(self):
        pass

    @abstractmethod
    def _ReadJson(self):
        pass