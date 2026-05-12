import json
from pathlib import Path
from .AudioData import AudioData
from .SoundscapeReapyControllerConfig import SoundscapeReapyControllerConfig
from .jsonDealer import jsonDealer

class AudiosData(jsonDealer):
    __audios_json_file_name = "audios.json"
    __ambisonic_type_name = "ambisonic"
    AudiosInfo = []

    def __init__(self, reapy_config: SoundscapeReapyControllerConfig):
        self.__audios_json = Path(reapy_config.SoundsLocation+"/"+self.__audios_json_file_name) #This directory will also have the audios.json
        self._ReadJson()

    def _ReadJson(self):
        try:
            with open(self.__audios_json,'r') as f:
                audios_data = json.load(f)
            
            if "sounds" in audios_data and isinstance(audios_data["sounds"], list) and len(audios_data["sounds"]) > 0:
                sounds = audios_data["sounds"]  # read the dictionary in the sounds array
                for sound in sounds:
                    ambisonic = True if sound["type"] == self.__ambisonic_type_name else False
                    audioData = AudioData(sound["id"],sound["name"],ambisonic,sound["fileName"])
                    self.AudiosInfo.append(audioData)
            else:
                print("Warning: sounds.json doesn't seem to have sound entries")

        except FileNotFoundError:
            print(f"Error: {self.__audios_json_file_name} file not found at {self.__audios_json}.  Using default values.")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in {self.__audios_json}. Using default values.")

    def GetAudioFileInfo(self,id: str) -> AudioData:
        AudioInfo = next((audio for audio in self.AudiosInfo if audio.sound_id == id), None)
        if AudioInfo is None:
            raise ValueError(f"Audio with id:{id} was not recognized")
        return AudioInfo

if __name__ == '__main__':
    srcc = SoundscapeReapyControllerConfig()
    ad = AudiosData(srcc)
    print(ad.AudiosInfo)
    print()
    print(ad.GetAudiFileInfo("stones"))


    