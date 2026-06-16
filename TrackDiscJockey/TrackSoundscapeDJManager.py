import reapy
import math
import time
from reapy import reascript_api as RPR
import json
import threading
import logging
from Debug.PerformanceMonitoring.PlayDelayMeasure import PlayDelayMeasure
from AudioPlugins.Sparta.AmbisonicENCoder import AmbisonicENCoder
from AudioPlugins.Sparta.AmbisonicDECoder import AmbisonicDECoder
from AudioPlugins.Sparta.AmbisonicBinaural import AmbisonicBINaural
from uuid import UUID
from pathlib import Path
from TrackDiscJockey.SoundTrack import SoundTrack
from jsonUtils.SoundscapeReapyControllerConfig import SoundscapeReapyControllerConfig
from jsonUtils.AudiosData import AudiosData
from jsonUtils.AudioData import AudioData
#Sound effect plugin classes
from AudioPlugins.SoundEffects.Echo import Echo
from AudioPlugins.SoundEffects.Occlusion import Occlusion
from AudioPlugins.SoundEffects.HighLowPassFilter import HighLowPassFilter
from AudioPlugins.RiReverbs import RiReverbs

logging.basicConfig(level=logging.INFO)

class TrackSoundscapeDJManager:
    def __init__(self,project: reapy.Project, reapy_controller_config: SoundscapeReapyControllerConfig):
        self.__project = project
        self.__logger = logging.getLogger(self.__class__.__name__)
        
        self.__SoundTracks = []
        self.__CurrentMaxAudioDuration = 0.0
        self.__ReaperTimeSelection = reapy.TimeSelection(project) #To do the looping and set the timeline duration
        self.__reapy_controller_config = reapy_controller_config
        self.__sounds_folder_path = reapy_controller_config.SoundsLocation
        self.__audiosData = AudiosData(reapy_controller_config)

        self.__NonLoopSoundtracks = [] #Tracks to delete after 1 reaper loop

        self.__EncoderAmbisonic = project._get_track_by_name(reapy_controller_config.EncoderAmbisonicTrackName)
        self.__EncoderMono = project._get_track_by_name(reapy_controller_config.EncoderMonoAudioTrackName)
        self.__DecoderBinaural = project._get_track_by_name(reapy_controller_config.DecoderBinauralTrackName)
        self.__DecoderAmbisonic = project._get_track_by_name(reapy_controller_config.DecoderAmbisonicTrackName)

        self.__MonoAudiosCounter = 0
        self.__AmbisonicOrder = reapy_controller_config.AmbisonicOrder
        self.__AmbiENC = AmbisonicENCoder(self.__EncoderMono.fxs[AmbisonicENCoder.plugin_name],1,
                                          reapy_controller_config.InvertAzimuth,reapy_controller_config.InvertElevation,self.__AmbisonicOrder)
        self.__AmbiDEC = AmbisonicDECoder(self.__DecoderAmbisonic.fxs[AmbisonicDECoder.plugin_name],self.__AmbisonicOrder)
        self.__AmbiBIN = AmbisonicBINaural(self.__DecoderBinaural.fxs[AmbisonicBINaural.plugin_name],self.__AmbisonicOrder)

        self.__TrackSelectAddNewNext = project._get_track_by_name(reapy_controller_config.DecoderAmbisonicTrackName) #The track to preselect before adding a new track
        self.__InitTrackCount = reapy_controller_config.TrackChannels

        self.__soundscapeTime = 0 #if its 0 its supposed to play forever
        self.__soundscapeLoop = False
        self.__soundscapeInfinite = False
        self.__soundscapeInfiniteLimit = reapy_controller_config.MaxInfiniteSoundscapeMinutesTime
        self.__SoundscapePlaying = False
        self.__lock = threading.Lock()
        self.__nonloop_timer: threading.Timer | None = None

        self.__availableSoundEffects = {
            "echo": Echo,
            "occlusion": Occlusion,
            "pass": HighLowPassFilter,
            "reverb": RiReverbs
        }

        #Set project sample rate
        self.__sample_rate = 96000
        RPR.GetSetProjectInfo(project.id, "PROJECT_SRATE_USE", 1.0, True)
        RPR.GetSetProjectInfo(project.id, "PROJECT_SRATE", self.__sample_rate, True)

        #Initial config commands
        self.__ReaperTimeSelection.loop()
        self.__AmbiENC.setNumSources(1)
        self.__setTracksForAmbisonic()
        self.__setTracksVolumes()
        self.__setDecoderMutes()

        self.measure_delay = reapy_controller_config.MeasureDelay
        PlayDelayMeasure.save_to_file = reapy_controller_config.SaveDelayMeasure

    def __setTracksForAmbisonic(self):
        #Set number of tracks for mono encoder and decoders
        self.__EncoderMono.set_info_value("I_NCHAN", self.__InitTrackCount)
        self.__DecoderBinaural.set_info_value("I_NCHAN", self.__InitTrackCount)
        self.__DecoderAmbisonic.set_info_value("I_NCHAN", self.__InitTrackCount)

    def __setTracksVolumes(self):
        #Sets the track's volumes
        linearVolume = self.__db_to_linear(0)
        
        RPR.SetMediaTrackInfo_Value(self.__EncoderAmbisonic.id,"D_VOL",linearVolume)
        RPR.SetMediaTrackInfo_Value(self.__EncoderMono.id,"D_VOL",linearVolume)
        RPR.SetMediaTrackInfo_Value(self.__DecoderBinaural.id,"D_VOL",linearVolume)
        RPR.SetMediaTrackInfo_Value(self.__DecoderAmbisonic.id,"D_VOL",linearVolume)

    def __setDecoderMutes(self):
        if self.__reapy_controller_config.MuteBinauralDecoder:
            self.__DecoderBinaural.mute()
        else:
            self.__DecoderBinaural.unmute()

        if self.__reapy_controller_config.MuteAmbisonicDecoder:
            self.__DecoderAmbisonic.mute()
        else:
            self.__DecoderAmbisonic.unmute()
        

    def CommandReceive(self,msg: str) -> str:
        try:
            with self.__lock:
                return self.__HandleCommand(json.loads(msg))
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self.__logger.error(f"Malformed command: {e}")
            return "Invalid Command or Instructions"
        except Exception as e:
            self.__logger.error(f"Failed to handle command: {e}")
            return "Command failed"

    def __HandleCommand(self, message: dict) -> str:
        command = message["command"]

        if command == "new_soundscape":
            self.__NewSoundscape(int(message["Duration"]),bool(message["Loop"]))
            return "New Soundscape started"

        elif command == "start_soundscape":
            self.__StartSoundscape(int(message["timestamp"]))
            return "soundscape_started"
        
        elif command == "no_start_wait":
            self.__SoundscapePlaying = True
            return "Skipped waiting for soundscape start message"

        elif command == "end_soundscape":
            self.__EndSoundscape()
            return "Soundscape has been finished"

        elif command == "new_track":
            try:
                self.__NewTrack(message["AudioID"],UUID(message["SoundUUID"]), float(message["Volume"]),bool(message["Loop"]),int(message["Delay"]))
            except FileNotFoundError:
                audioID = message["AudioID"]
                self.__logger.error(f"ERROR: The audio track with id {audioID} has no valid audio file in the sounds folder.")
                return "Track was not created successfully in Reaper. Reason: The audio file is not available in SoundscapeVReapy Controller"
            return "track_created" #messages that have to be interpreted are not supposed to have spaces

        elif command == "source_position":
            uuid = UUID(message["SoundUUID"])
            position_angles = (message["azim"],message["elev"])  # (azim, elevation)
            distance = float(message["distance"])
            if not self.__UpdateAudioPosition(uuid, position_angles, distance):
                return "Source Position Failed: UUID not found"
            return "Source Position Updated"

        elif command == "mute":
            self.__muteTrack(UUID(message["SoundUUID"]))
            return "Muted Track"

        elif command == "unmute":
            self.__unmuteTrack(UUID(message["SoundUUID"]))
            return "Unmuted Track"

        elif command == "add_effect":
            self.__addSoundEffect(UUID(message["SoundUUID"]),str(message["EffectName"]),list(message["EffectParams"]))
            return "Effect Added to Track"

        elif command == "remove_effect":
            self.__removeSoundEffect(UUID(message["SoundUUID"]),str(message["EffectName"]))
            return "Effect Removed from Track"

        elif command == "delete_track":
            uuid = UUID(message["SoundUUID"])
            self.__DeleteTrack(uuid)
            return "Track Deleted"

        return "Invalid Command or Instructions"
    
    def __NewSoundscape(self, duration_seconds: int, loop: bool):
        self.__soundscapeLoop = loop
        self.__soundscapeTime = duration_seconds
        self.__soundscapeInfinite = False
        self.__SoundscapePlaying = False
        if duration_seconds == 0:
            self.__soundscapeInfinite = True

        self.__NewAudioDurations()
        #self.__project.play()

    def __StartSoundscape(self, timestamp=None):
        if self.__nonloop_timer:
            self.__nonloop_timer.cancel()
        self.__project.play()

        if self.measure_delay and timestamp is not None:
            PlayDelayMeasure.measure_delay(timestamp)

        self.__SoundscapePlaying = True
        self.__nonloop_timer = threading.Timer(
            self.__CurrentMaxAudioDuration, self.__DeleteTracksAfterLoop
        )
        self.__nonloop_timer.start()

    def __EndSoundscape(self):
        if self.__nonloop_timer:
            self.__nonloop_timer.cancel()
            self.__nonloop_timer = None
        for soundTrack in list(self.__SoundTracks):
            self.__DeleteSoundTrack(soundTrack)

        self.__soundscapeTime = 0
        self.__SoundscapePlaying = False

        self.__project.stop()
        self.__NewAudioDurations()

    def __NewTrack(self,audioID: str, soundUUID: UUID, volume: float, loop: bool, delay: int, redo_track = True):
        if self.__CurrentMaxAudioDuration == 0.0:
            self.__logger.warning("new_track received before new_soundscape, track not created")
            return
        #Check if that specific sound with that UUID already exists. This will early return the function but try to make sure this command isn't received
        if self.__FindTrackByUUID(soundUUID):
            if redo_track:
                #Delete track first
                self.__DeleteTrack(soundUUID)
            else:
                self.__logger.warning("A command to create a new track that already exists has been ignored")
                return

        #Create a new track with soundtrack class instance and add it to the list
        audioTrackInfo = self.__audiosData.GetAudioFileInfo(audioID) #Prepare the audio's info and check if audio is available
        try:
            audioPath = self.__get_audio_path(audioTrackInfo)
        except FileNotFoundError:
            raise

        with reapy.inside_reaper():
            #Cursor in 0 to insert the audio and paused
            self.__project.cursor_position = delay
            self.__project.stop()
            self.__project.unselect_all_tracks()
            self.__TrackSelectAddNewNext.select()

            existing_track_ids = {t.id for t in self.__project.tracks}
            RPR.InsertMedia(audioPath,1) #creates a track which its name is the same as the sound file name #Make the track with the audio file
            newTrack = next(t for t in self.__project.tracks if t.id not in existing_track_ids)

            newTrack.mute() #Avoid pop

            if loop:
                item = newTrack.items[0]
                RPR.SetMediaItemInfo_Value(item.id, "B_LOOPSRC", 1)  # enable loop source on item
                #Item starts at the delay offset, so trim its length to end exactly at the loop boundary
                item.length = self.__CurrentMaxAudioDuration - delay

                self.__project.cursor_position = 0 #Get cursor back to 0

        self.__Set_Track_Channels(newTrack,audioTrackInfo.ambisonic)
        ambi_source_index = self.__SetTrackRedirect(newTrack,audioTrackInfo.ambisonic)

        soundTrack = SoundTrack(audioTrackInfo,soundUUID, newTrack,delay, loop)
        soundTrack.ambiSourceIndex = ambi_source_index
        soundTrack.VolumeGain = volume
        self.__SoundTracks.append(soundTrack)
        #self.__NewAudioDurations()

        if not loop and self.__soundscapeLoop == False: #If the audio isnt even supposed to repeat, we have to avoid it being replayed after the project loops
            self.__SetNonLoopTrackDeactivation(soundTrack)

        if self.__SoundscapePlaying:
            self.__StartSoundscape()

    def __get_audio_path(self,audioTrackInfo: AudioData):
        audioPath = Path(self.__sounds_folder_path+"/"+audioTrackInfo.fileName)
        if not audioPath.exists():
            raise FileNotFoundError(f"The path '{audioPath}' is not a valid file.")
        else:
            return str(audioPath)

    def __Set_Track_Channels(self,track: reapy.Track, ambisonic:bool):
        if not ambisonic:
            track.set_info_value("I_NCHAN", 2)
        else:
            track.set_info_value("I_NCHAN", 4)

    def __SetNonLoopTrackDeactivation(self,soundTrack):
        self.__NonLoopSoundtracks.append(soundTrack)

    def __DeleteTracksAfterLoop(self):
        with self.__lock:
            for soundTrack in list(self.__NonLoopSoundtracks):
                self.__DeleteSoundTrack(soundTrack)
            self.__NonLoopSoundtracks.clear()

    def __NewAudioDurations(self):
        if self.__soundscapeInfinite == True:
            self.__CurrentMaxAudioDuration = self.__soundscapeInfiniteLimit * 60 #config value is in minutes, durations are in seconds
        else:
            self.__CurrentMaxAudioDuration = self.__soundscapeTime

        self.__ReaperTimeSelection._set_start_end(0, self.__CurrentMaxAudioDuration)

    def __SetTrackRedirect(self,track: reapy.Track, ambisonic: bool):
        #Do not route to master
        RPR.SetMediaTrackInfo_Value(track.id, "B_MAINSEND", 0)

        if not ambisonic:
            return self.__SetNormalTrackEncoderRedirect(track)
        else:
            return self.__SetAmbisonicTrackEncoderRedirect(track)
        

    def __SetNormalTrackEncoderRedirect(self,source_track: reapy.Track):
        #First set the new receive count in the encoder
        self.__MonoAudiosCounter += 1
        self.__AmbiENC.setNumSources(self.__MonoAudiosCounter+1)

        send = source_track.add_send(self.__EncoderMono)

        # I_SRCCHAN | 1024 = mono flag, index 0 = first channel of source track
        RPR.SetTrackSendInfo_Value(source_track.id, 0, send.index, "I_SRCCHAN", 0 | 1024)

        # Destination increments by 1 each time (0=ch1/2, 2=ch2/3, 3=ch3/4, ...)
        dst_chan = self.__MonoAudiosCounter-1
        RPR.SetTrackSendInfo_Value(source_track.id, 0, send.index, "I_DSTCHAN", dst_chan)

        self.__AmbiENC.SpeakerPositions(self.__MonoAudiosCounter, (0.0, 0.0)) #Set default value in the beginning

        return self.__MonoAudiosCounter

    def __SetAmbisonicTrackEncoderRedirect(self,source_track: reapy.Track, num_channels = 4):
        send = source_track.add_send(self.__EncoderAmbisonic)

        # Encode: start_ch (0) | (num_channels - 1) << 10
        ch_value = 0 | ((num_channels - 1) << 10)  # = 3072 for 4ch
        
        # Get the raw REAPER track pointer and send index
        send_idx = send.index
        track_ptr = source_track.id

        RPR.SetTrackSendInfo_Value(track_ptr, 0, send_idx, "I_SRCCHAN", ch_value)
        RPR.SetTrackSendInfo_Value(track_ptr, 0, send_idx, "I_DSTCHAN", ch_value)

        return None
    
    def __UpdateAudioPosition(self, soundUUID: UUID, position_angles: tuple, distanceRadius: float):
        soundTrack = self.__FindTrackByUUID(soundUUID)
        if soundTrack is None:
            self.__logger.warning(f"source_position received for unknown UUID {soundUUID}")
            return False
        
        if not soundTrack.ambisonic:
            # Update Sparta plugin source position
            self.__AmbiENC.SpeakerPositions(soundTrack.ambiSourceIndex, position_angles)

        # Calculate and apply distance attenuation
        volume_db = self.__CalculateDistanceDB(distanceRadius)
        linearVolume = self.__db_to_linear(volume_db)*soundTrack.VolumeGain
        RPR.SetMediaTrackInfo_Value(soundTrack.Track.id,"D_VOL",linearVolume)

        # Save state on the SoundTrack
        soundTrack.positionalRot = position_angles
        soundTrack.distanceRadius = distanceRadius
        soundTrack.currentVolumeDB = volume_db

        #unmute track
        #soundTrack.Track.unmute()
        return True

    def __CalculateDistanceDB(self, distanceRadius: float) -> float:
        # 0dB at the 1m reference, then -20*log10(distance): -6dB per doubling of distance (every 10x distance is -20dB)
        if distanceRadius <= 0:
            return 0.0
        return -20 * math.log10(max(distanceRadius, 1.0))
        # Clamped to 1m minimum so we never get positive gain from sub-1m distances

    def __db_to_linear(self,volume_db: float) -> float:
        return 10 ** (volume_db / 20)
    
    def __FindTrackByUUID(self,soundUUID: UUID) -> SoundTrack:
        return next((st for st in self.__SoundTracks if st.SoundUUID == soundUUID), None)
    
    def __DeleteTrack(self, soundUUID: UUID):
        soundTrack = self.__FindTrackByUUID(soundUUID)
        if soundTrack is None:
            return

        self.__DeleteSoundTrack(soundTrack)
        #self.__NewAudioDurations()

    def __DeleteSoundTrack(self, soundTrack: SoundTrack):
        was_mono = soundTrack.ambiSourceIndex is not None

        self.__SoundTracks.remove(soundTrack)
        if soundTrack in self.__NonLoopSoundtracks:
            self.__NonLoopSoundtracks.remove(soundTrack)

        with reapy.inside_reaper():
            soundTrack.Track.delete()

            if was_mono:
                self.__MonoAudiosCounter -= 1
                # Compact remaining mono sources to fill the gap
                self.__ReallocateMonoSources()
                # Update Sparta source count after reallocation
                self.__AmbiENC.setNumSources(max(self.__MonoAudiosCounter, 1))
                # Shrink encoder track channels accordingly, but do not go initially set number
                self.__EncoderMono.set_info_value("I_NCHAN", max(self.__MonoAudiosCounter * 2, self.__InitTrackCount))
        

    def __ReallocateMonoSources(self):
        # Sort remaining mono tracks by their current index so we reassign in order
        mono_tracks = sorted(
            [st for st in self.__SoundTracks if st.ambiSourceIndex is not None],
            key=lambda st: st.ambiSourceIndex
        )

        for new_index, soundTrack in enumerate(mono_tracks, start=1):
            if soundTrack.ambiSourceIndex == new_index:
                continue  # already in the right slot, skip

            # Reroute the send to the new destination channel pair
            send = self.__FindSendToTrack(soundTrack.Track, self.__EncoderMono)
            if send is not None:
                dst_chan = new_index - 1
                RPR.SetTrackSendInfo_Value(
                    soundTrack.Track.id, 0, send.index, "I_DSTCHAN", dst_chan
                )

            # Move the Sparta position data to the new slot
            self.__AmbiENC.SpeakerPositions(new_index, soundTrack.positionalRot)

            soundTrack.ambiSourceIndex = new_index

    def __FindSendToTrack(self, source_track: reapy.Track, dest_track: reapy.Track):
        for send in source_track.sends:
            if send.dest_track.id == dest_track.id:
                return send
        return None

    def __muteTrack(self, soundUUID: UUID):
        soundTrack = self.__FindTrackByUUID(soundUUID)
        if soundTrack:
            soundTrack.mute()

    def __unmuteTrack(self, soundUUID: UUID):
        soundTrack = self.__FindTrackByUUID(soundUUID)
        if soundTrack:
            soundTrack.unmute()

    def __addSoundEffect(self,SoundUUID: UUID, effect_name: str, effectParams: list):
        soundTrack = self.__FindTrackByUUID(SoundUUID)
        if soundTrack:
            effectClass = self.__availableSoundEffects.get(effect_name)
            if effectClass is None:
                self.__logger.warning("A sound effect not yet implemented was attempted to be added to the track")
                return
            newEffect = effectClass.add_to_track(soundTrack, effectParams)

            #Add to soundtrack
            soundTrack.newSoundEffect(newEffect)

    def __removeSoundEffect(self, SoundUUID: UUID, effect_name: str):
        soundTrack = self.__FindTrackByUUID(SoundUUID)
        if soundTrack:
            effectType = self.__availableSoundEffects.get(effect_name)
            if effectType is None:
                self.__logger.warning("A sound effect not yet implemented was attempted to be deleted from the track")
                return
            
            fxType = next((item for item in soundTrack.SoundEffects if isinstance(item, effectType)), None)
            if fxType is None:
                self.__logger.warning(f"Sound effect '{effect_name}' was not found in the track")
                return
            
            #remove from soundtrack
            soundTrack.deleteSoundEffect(fxType)

    

            
