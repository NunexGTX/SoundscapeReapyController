from dataclasses import dataclass

@dataclass
class AudioData:
    sound_id: str
    sound_name: str
    ambisonic: bool = False #Default to mono/stereo audio
    fileName: str = "necessaryTestAudio.mp3"
    #Discard imagePath (not needed)