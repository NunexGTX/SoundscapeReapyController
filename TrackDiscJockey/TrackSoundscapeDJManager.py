import reapy
import math
from reapy import reascript_api as RPR
import json
import asyncio
from ..AudioPlugins.Sparta.AmbisonicENCoder import AmbisonicENCoder
from uuid import UUID
from SoundTrack import SoundTrack
from jsonUtils.SoundscapeReapyControllerConfig import SoundscapeReapyControllerConfig
from jsonUtils.AudiosData import AudiosData

class TrackSoundscapeDJManager:
    def __init__(self,project: reapy.Project, reapy_controller_config: SoundscapeReapyControllerConfig):
        self.__project = project
        self.__SoundTracks = []
        self.__CurrentMaxAudioDuration = 0.0
        self.__ReaperTimeSelection = reapy.TimeSelection(project) #To do the looping and set the timeline duration
        self.__reapy_controller_config = reapy_controller_config
        self.__sounds_folder_path = reapy_controller_config.SoundsLocation
        self.__audiosData = AudiosData(reapy_controller_config)

        self.__EncoderMono = project._get_track_by_name(reapy_controller_config.EncoderMonoAudioTrackName)
        self.__MonoAudiosCounter = 0
        self.__AmbiENC = AmbisonicENCoder(self.__EncoderMono.fxs[AmbisonicENCoder.plugin_name])

        self.EncoderAmbisonic = project._get_track_by_name(reapy_controller_config.EncoderAmbisonicTrackName)

        #Initial config commands
        self.__ReaperTimeSelection.loop()
        self.__AmbiENC.setNumSources(1)

    def CommandReceive(self,msg: str) -> str:
        message = json.loads(msg)
        command = message["command"]

        if command == "new_track":
            self.__NewTrack(message["AudioID"],UUID(message["SoundUUID"]),bool(message["Loop"]))
            return "Track Created in Reaper"
        
        elif command == "source_position":
            uuid = UUID(message["SoundUUID"])
            position_angles = tuple(message["position"])  # (azim, elevation)
            distance = float(message["distance"])
            self.__UpdateAudioPosition(uuid, position_angles, distance)
            return "Source Position Updated"
        
        elif command == "delete_track":
            uuid = UUID(message["SoundUUID"])
            self.__DeleteTrack(uuid)
            return "Track Deleted"

        return "Invalid Command or Instructions"

    def __NewTrack(self,audioID: str, soundUUID: UUID, loop: bool):
        #Cursor in 0 to insert the audio and paused
        self.__project.cursor_position = 0
        self.__project.pause()
        #Create a new track with soundtrack class instance and add it to the list
        audioTrackInfo = self.__audiosData.GetAudioFileInfo(audioID) #Prepare the audio's info
        RPR.InsertMedia(self.__sounds_folder_path+"/"+audioTrackInfo.fileName,1) #creates a track which its name is the same as the sound file name #Make the track with the audio file
        #Get current first track (it should be the new one)
        newTrack = self.__project.tracks[0]

        self.__Set_Track_Channels(newTrack,audioTrackInfo.ambisonic)
        ambi_source_index = self.__SetTrackRedirect(newTrack,audioTrackInfo.ambisonic)

        soundTrack = SoundTrack(audioTrackInfo,soundUUID, newTrack)
        soundTrack.ambiSourceIndex = ambi_source_index
        self.__SoundTracks.append(soundTrack)
        self.__NewAudioDurations()

        if not loop:
            self.__DeleteLoopTrack(soundUUID,soundTrack.audio_duration_seconds)

        self.__project.play()

    def __Set_Track_Channels(self,track: reapy.Track, ambisonic:bool):
        if not ambisonic:
            track.set_info_value("I_NCHAN", 2)
        else:
            track.set_info_value("I_NCHAN", 4)

    def __NewAudioDurations(self):
        if len(self.__SoundTracks) == 0:
            self.__ProjectNoTrackPause()
            return

        # Update max duration from the full list
        self.__CurrentMaxAudioDuration = max(
            st.audio_duration_seconds for st in self.__SoundTracks
        )

        # Extend all tracks to the largest clean multiple of their own duration
        self.__ExtendAllTrackItems()

        self.__ReaperTimeSelection._set_start_end(0, self.__CurrentMaxAudioDuration)
    
    def __ExtendAllTrackItems(self):
        for soundTrack in self.__SoundTracks:
            native_duration = soundTrack.audio_duration_seconds
            # How many full plays fit within the longest audio?
            n_loops = math.floor(self.__CurrentMaxAudioDuration / native_duration)
            extended_duration = n_loops * native_duration  # always <= max, always a clean loop end

            item = soundTrack.Track.items[0]
            RPR.SetMediaItemInfo_Value(item.id, "B_LOOPSRC", 1)  # enable loop source on item
            item.length = extended_duration

    def __ProjectNoTrackPause(self):
        self.__project.pause()
        self.__project.cursor_position = 0
        self.__CurrentMaxAudioDuration = 0.0

    def __SetTrackRedirect(self,track: reapy.Track, ambisonic: bool):
        if not ambisonic:
            return self.__SetNormalTrackEncoderRedirect(track)
        else:
            return self.__SetAmbisonicTrackEncoderRedirect(track)

    def __SetNormalTrackEncoderRedirect(self,source_track: reapy.Track):
        #First set the new receive count in the encoder
        self.__MonoAudiosCounter += 1
        self.__AmbiENC.setNumSources(self.__MonoAudiosCounter)

        send = source_track.add_send(self.__EncoderMono)

        # I_SRCCHAN | 1024 = mono flag, index 0 = first channel of source track
        RPR.SetTrackSendInfo_Value(source_track.id, 0, send.index, "I_SRCCHAN", 0 | 1024)

        # Destination increments by 2 each time (0=ch1/2, 2=ch3/4, 4=ch5/6, ...)
        dst_chan = (self.__MonoAudiosCounter - 1) * 2
        RPR.SetTrackSendInfo_Value(source_track.id, 0, send.index, "I_DSTCHAN", dst_chan)

        self.__AmbiENC.SpeakerPositions(self.__MonoAudiosCounter, (0.0, 0.0)) #Set default value in the beginning

        return self.__MonoAudiosCounter

    def __SetAmbisonicTrackEncoderRedirect(self,source_track: reapy.Track):
        send = source_track.add_send(self.EncoderAmbisonic)

        # Send all channels from src ch 0 → dst ch 0 (1/2/3/4 all flow through)
        RPR.SetTrackSendInfo_Value(source_track.id, 0, send.index, "I_SRCCHAN", 0)
        RPR.SetTrackSendInfo_Value(source_track.id, 0, send.index, "I_DSTCHAN", 0)

        return None
    
    def __UpdateAudioPosition(self, soundUUID: UUID, position_angles: tuple, distanceRadius: float):
        soundTrack = self.__FindTrackByUUID(soundUUID)
        if soundTrack is None:
            raise ValueError(f"SoundTrack with UUID {soundUUID} not found")
        if soundTrack.ambisonic:
            raise ValueError(f"SoundTrack {soundUUID} is ambisonic, position control not applicable")

        # Update Sparta plugin source position
        self.__AmbiENC.SpeakerPositions(soundTrack.ambiSourceIndex, position_angles)

        # Calculate and apply distance attenuation
        volume_db = self.__CalculateDistanceDB(distanceRadius)
        trackRPR = RPR.GetTrack(0,soundTrack.Track.index)
        RPR.SetMediaTrackInfo_Value(trackRPR,"D_VOL",self.__db_to_linear(volume_db))

        # Save state on the SoundTrack
        soundTrack.positionalRot = position_angles
        soundTrack.distanceRadius = distanceRadius
        soundTrack.currentVolumeDB = volume_db

    def __CalculateDistanceDB(self, distanceRadius: float) -> float:
        # Inverse square law: 0dB at 1m reference, -6dB per doubling of distance
        if distanceRadius <= 0:
            return 0.0
        return -20 * math.log10(max(distanceRadius, 1.0))
        # Clamped to 1m minimum so we never get positive gain from sub-1m distances

    def __db_to_linear(self,volume_db: float) -> float:
        return 10 ** (volume_db / 20)
    
    def __FindTrackByUUID(self,soundUUID: UUID):
        return next((st for st in self.__SoundTracks if st.SoundUUID == soundUUID), None)
    
    def __DeleteTrack(self, soundUUID: UUID):
        soundTrack = self.__FindTrackByUUID(soundUUID)
        if soundTrack is None:
            return

        was_mono = soundTrack.ambiSourceIndex is not None

        self.__SoundTracks.remove(soundTrack)
        soundTrack.Track.delete()

        if was_mono:
            self.__MonoAudiosCounter -= 1
            # Compact remaining mono sources to fill the gap
            self.__ReallocateMonoSources()
            # Update Sparta source count after reallocation
            self.__AmbiENC.setNumSources(max(self.__MonoAudiosCounter, 1))
            # Shrink encoder track channels accordingly
            self.__EncoderMono.set_info_value("I_NCHAN", max(self.__MonoAudiosCounter * 2, 2))

        self.__NewAudioDurations()

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
                dst_chan = (new_index - 1) * 2
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

    async def __DeleteLoopTrack(self, soundUUID: UUID, audio_time: float):
        await asyncio.sleep(audio_time)
        self.__DeleteTrack(soundUUID)
