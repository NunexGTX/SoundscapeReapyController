import json
import hashlib
from pathlib import Path
from .jsonDealer import jsonDealer

class SoundscapeReapyControllerConfig(jsonDealer):
    _json_location = "../configs/config.json"

    __config_default = {
            "ReapyTemplateProjectPath": "{REAPY_CONTROLLER_DIR}/SoundscapeReaper.RPP",
            "SoundsLocation": "{REAPY_CONTROLLER_DIR}/Sounds",
            "SoundscapeVRUnityCommunicationPort": 6337,
            "LogCommunications": True,
            "BinauralRotationUpdate": False,
            "EncoderAmbisonicTrackName": "EncoderAmbisonic1stOrderAudio",
            "EncoderMonoAudioTrackName": "EncoderMonoAudio",
            "DecoderAmbisonicTrackName": "DecoderAmbisonic",
            "DecoderBinauralTrackName": "DecoderBinaural",
            "AmbisonicOrder": 5,
            "TrackChannels": 38,
            "InvertAzimuth": False,
            "InvertElev": False,
            "MaxInfiniteSoundscapeMinutesTime": 40,
            "MuteBinauralDecoder": False,
            "MuteAmbisonicDecoder": False,
            "measure_delay": False,
            "save_delay_measure": False
        }

    def __init__(self):
        super().__init__()
        self._ReadJson()

    def _ReadJson(self):
        self.config_json = self._resolve_config_dir()
        try:
            with open(self.config_json,'r') as f:
                config_data = json.load(f)

            if "config" in config_data and isinstance(config_data["config"], list) and len(config_data["config"]) > 0:
                self.__config = config_data["config"][0]  # read configuration entry
            else:
                print("Warning: No 'config' section or empty list found in config.json. Using default values.")
                self.__config = self.__config_default # Initialize with an empty dictionary if no config is found

        except FileNotFoundError:
            print(f"Error: Config file not found at {self.config_json}.  Using default values.")
            self.__config = self.__config_default
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in {self.config_json}. Using default values.")
            self.__config = self.__config_default
        except Exception as e:
            print(f"Error: Failed to read config from {self.config_json} ({e}). Using default values.")
            self.__config = self.__config_default

        try:
            self._apply_config()
        except Exception as e:
            print(f"Error: Failed to apply config values ({e}). Falling back to defaults.")
            self.__config = self.__config_default
            self._apply_config()

    def _apply_config(self):
        self.ReapyTemplateProjectPath = self.__reapy_template_project_path()
        self.SoundsLocation = self.__sounds_location()
        self.SoundscapeVRUnityCommunicationPort = self.__soundscape_vr_unity_communication_port()
        self.LogCommunications = self.__log_communications()
        self.BinauralRotationUpdate = self.__binaural_rotation_update()
        self.EncoderMonoAudioTrackName = self.__encoder_mono_audio_track_name()
        self.EncoderAmbisonicTrackName = self.__encoder_ambisonic_track_name()
        self.DecoderAmbisonicTrackName = self.__decoder_ambisonic_track_name()
        self.DecoderBinauralTrackName = self.__decoder_binaural_track_name()
        self.AmbisonicOrder = self.__ambisonic_order()
        self.TrackChannels = self.__track_channels()
        self.InvertAzimuth = self.__azim_invert()
        self.InvertElevation = self.__elev_invert()
        self.MaxInfiniteSoundscapeMinutesTime = self.__max_inifinite_soundscape_minutes_time()
        self.MuteBinauralDecoder = self.__mute_binaural_decoder()
        self.MuteAmbisonicDecoder = self.__mute_ambisonic_decoder()
        self.MeasureDelay = self.__measure_delay()
        self.SaveDelayMeasure = self.__save_delay_measure()
        
    def __reapy_template_project_path(self):
        """Returns the path to the Reapy template project."""
        path = self.__config["ReapyTemplateProjectPath"]
        return self._get_project_file_path(path)

    def __sounds_location(self):
        """Returns the location of the sounds."""
        path = self.__config["SoundsLocation"]
        return self._get_project_file_path(path)

    def __soundscape_vr_unity_communication_port(self):
        """Returns the communication port for SoundscapeVR Unity."""
        return self.__config["SoundscapeVRUnityCommunicationPort"]
    
    def __log_communications(self):
        return bool(self.__config["LogCommunications"])
    
    def __binaural_rotation_update(self):
        return bool(self.__config["BinauralRotationUpdate"])

    def __encoder_ambisonic_track_name(self):
        """Returns the name of the encoder ambisonic track."""
        return self.__config["EncoderAmbisonicTrackName"]

    def __encoder_mono_audio_track_name(self):
        """Returns the name of the encoder mono audio track."""
        return self.__config["EncoderMonoAudioTrackName"]
    
    def __decoder_ambisonic_track_name(self):
        return self.__config["DecoderAmbisonicTrackName"]
    
    def __decoder_binaural_track_name(self):
        return self.__config["DecoderBinauralTrackName"]
    
    def __ambisonic_order(self):
        return int(min(max(self.__config["AmbisonicOrder"],1),10))
    
    def __track_channels(self):
        return int(min(max(self.__config["TrackChannels"],1),128))
    
    def __azim_invert(self):
        return bool(self.__config["InvertAzimuth"])
    
    def __elev_invert(self):
        return bool(self.__config["InvertElev"])
    
    def __max_inifinite_soundscape_minutes_time(self):
        return int(self.__config["MaxInfiniteSoundscapeMinutesTime"])
    
    def __mute_binaural_decoder(self):
        return self.__config["MuteBinauralDecoder"]
    
    def __mute_ambisonic_decoder(self):
        return self.__config["MuteAmbisonicDecoder"]
    
    def __measure_delay(self):
        return bool(self.__config["measure_delay"])
    
    def __save_delay_measure(self):
        return bool(self.__config["save_delay_measure"])
    
#For Debug
if __name__ == '__main__':
    srcc = SoundscapeReapyControllerConfig()
    print(srcc.SoundsLocation)