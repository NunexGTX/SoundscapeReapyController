import os
import json
from pathlib import Path

class SoundscapeReapyControllerConfig:
    __config_json_location = "../configs/config.json"
    __soundscape_reapy_controller_dir_flag = "{REAPY_CONTROLLER_DIR}"

    __config_default = {'ReapyTemplateProjectPath': '{REAPY_CONTROLLER_DIR}/SoundscapeReaper.RPP', 
                        'SoundsLocation': '{REAPY_CONTROLLER_DIR}/SoundscapeReaper.RPP', 
                        'SoundscapeVRUnityCommunicationPort': 6337, 
                        'EncoderAmbisonicTrackName': 'EncoderAmbisonicAudio', 
                        'EncoderMonoAudioTrackName': 'EncoderMonoAudio'}

    def __init__(self):
        self.__ReadConfig()

    def __ReadConfig(self):
        config_json = self._resolve_config_dir()

        try:
            with open(config_json,'r') as f:
                config_data = json.load(f)

            if "config" in config_data and isinstance(config_data["config"], list) and len(config_data["config"]) > 0:
                self.__config = config_data["config"][0]  # read configuration entry
            else:
                print("Warning: No 'config' section or empty list found in config.json. Using default values.")
                self.__config = self.__config_default # Initialize with an empty dictionary if no config is found

        except FileNotFoundError:
            print(f"Error: Config file not found at {config_json}.  Using default values.")
            self.__config = self.__config_default # Initialize with an empty dictionary if the file doesn't exist
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in {config_json}. Using default values.")
            self.__config = self.__config_default #Initialize with an empty dictionary if the json is read as invalid

        print(self.__config)

        self.ReapyTemplateProjectPath = self.__reapy_template_project_path()
        self.SoundsLocation = self.__sounds_location()
        self.SoundscapeVRUnityCommunicationPort = self.__soundscape_vr_unity_communication_port()
        self.EncoderMonoAudioTrackName = self.__encoder_mono_audio_track_name()
        self.EncoderAmbisonicTrackName = self.__encoder_ambisonic_track_name()
        
    def __reapy_template_project_path(self):
        """Returns the path to the Reapy template project."""
        path = self.__config["ReapyTemplateProjectPath"]
        if self.__soundscape_reapy_controller_dir_flag in path:
            return path.replace(self.__soundscape_reapy_controller_dir_flag, self._get_reapy_controller_dir())
        else:
            return path

    def __sounds_location(self):
        """Returns the location of the sounds."""
        path = self.__config["SoundsLocation"]
        if self.__soundscape_reapy_controller_dir_flag in path:
            return path.replace(self.__soundscape_reapy_controller_dir_flag, self._get_reapy_controller_dir())
        else:
            return path

    def __soundscape_vr_unity_communication_port(self):
        """Returns the communication port for SoundscapeVR Unity."""
        return self.__config["SoundscapeVRUnityCommunicationPort"]

    def __encoder_ambisonic_track_name(self):
        """Returns the name of the encoder ambisonic track."""
        return self.__config["EncoderAmbisonicTrackName"]

    def __encoder_mono_audio_track_name(self):
        """Returns the name of the encoder mono audio track."""
        return self.__config["EncoderMonoAudioTrackName"]
    
    def _get_reapy_controller_dir(self):
        '''Gets the reapy controller project dir. Should be the root of this project, which is on the previous directory relative to this classe's python file'''
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def _resolve_config_dir(self):
        return (Path(__file__).parent / self.__config_json_location).resolve()
    
#For Debug
if __name__ == '__main__':
    srcc = SoundscapeReapyControllerConfig()