import reapy

class AmbisonicENCoder:
    #sliderVals = [0,1] #This represents in between which values each parameter must be

    ambisonic_plugin_name = "VST: sparta_ambiENC (AALTO) (64ch)"

    __param_defaults = [1,"ACN","SN3D"]

    __outputOrder_range = [1,10]

    __ChannelOrderVals = {
        "ACN": 0,
        "FuMa": 1
    }

    __NormTypeVals = {
        "N3D": 0,
        "SN3D": 0.5,
        "FuMa": 1
    }

    __source_range = [1,128]

    __spatial_sound_positions_start_index = 4 #The parameter's index of the FX in which the values become related to the position elevation and rotation of the speaker sources

    __azim_range = [-180,180]

    __elevation_range = [-90,90]

    def __init__(self,TrackFX,Sources: int,params = __param_defaults):
        self.TrackFX = TrackFX
        self.Sources = Sources #The number of speakers being used by the ambisonic plugin

        try:
            self.__checkInitialParams(params,Sources)
        except ValueError as e:
            print(e)
        
        self.__setInitialParams(params,Sources)
        
    def __setInitialParams(self,params,sources: int):
        self.__setOutputOrder(params[0])
        self.__setChannelOrder(params[1])
        self.__setNormType(params[2])
        self.__setNumSources(sources)

    def __setOutputOrder(self,ouputOrder_val):
        self.TrackFX.params[0] = self.__param_val_calc(ouputOrder_val,self.__outputOrder_range[0],self.__outputOrder_range[1])

    def __setChannelOrder(self,channelOrder_val):
        self.TrackFX.params[1] = self.__ChannelOrderVals[channelOrder_val]

    def __setNormType(self,normType_val):
        self.TrackFX.params[2] = self.__NormTypeVals[normType_val]

    def __setNumSources(self,numSources_val):
        self.TrackFX.params[3] = self.__param_val_calc(numSources_val,self.__source_range[0],self.__source_range[1])

    def __param_val_calc(self,x,min_val,max_val):
        #This uses the formula : (x-xmin)/(xmax-xmin) to rescale the values from 0 to 1
        return (x-min_val)/(max_val-min_val)
    
    '''Setting speaker array positions'''

    '''Receives an array with all sources positions
    Each element of the array has a tuple with each speaker's elevation and rotation
    It is possible to call this to set only some speakers at once by the order in which they are on the array
    But all speaker positions greater than the sources number will be ignored'''
    def SpeakersPositions(self,sources_positions):
        if len(sources_positions) > self.Sources:
            sources_positions = sources_positions[:self.Sources-1]
        
        for i in range(len(sources_positions)):
            self.SpeakerPositions(i+1,sources_positions[i])

    '''This function expects a tuple with the (azim,elevation) of the speaker and its source number'''
    def SpeakerPositions(self,source_number,position):
        rotation, elevation = position

        try:
            self.__check_speaker_availability(source_number)
            self.__check_azim_value(rotation)
            self.__check_elevation_value(elevation)
        except ValueError as e:
            print(e)

        self.setSpeakerAzim(source_number,rotation)
        self.setSpeakerElevation(source_number,elevation)

    '''
    def SpeakerPositions(self,source_number,rotation,elevation):
        self.SpeakerPositions(source_number,(rotation,elevation)) 
    '''
        
    def setSpeakerAzim(self,source_number,azim_value):
        speaker_param_index = (self.__spatial_sound_positions_start_index-1) + (source_number*2)-1
        self.TrackFX.params[speaker_param_index] = self.__param_val_calc(azim_value,self.__azim_range[0],self.__azim_range[1])
    
    def setSpeakerElevation(self,source_number,elevation_value):
        speaker_param_index = (self.__spatial_sound_positions_start_index-1) + (source_number*2)
        self.TrackFX.params[speaker_param_index] = self.__param_val_calc(elevation_value,self.__elevation_range[0],self.__elevation_range[1])

    '''Check functions'''
    def __checkInitialParams(self, params, sources):
        if not self.__outputOrder_range[0] <= params[0] <= self.__outputOrder_range[1]:
            raise ValueError(f"The Output Order of the ambisonic output must be between the values {self.__outputOrder_range[0]} and {self.__outputOrder_range[1]}")
        if params[1] not in self.__ChannelOrderVals:
            raise ValueError(f"{params[1]} is not a valid Channel Order Value")
        if params[2] not in self.__NormTypeVals:
            raise ValueError(f"{params[2]} is not a valid Norm Type Value")
        if not self.__source_range[0] <= sources <= self.__source_range[1]:
            raise ValueError(f"There can only be up to 128 channel speakers on your ambisonic setup with sparta, which means {sources} speakers isn't a valid amount of speakers. Either you typed wrong or don't know how to count")

    def __check_speaker_availability(self,source_number):
        if not 1 <= source_number <= self.Sources:
            raise ValueError(f"You tried to assign a position to a Speaker Source that does not exist at the moment. Source Number: {source_number}")
        
    def __check_azim_value(self,azim_val):
        if not self.__azim_range[0] <= azim_val <= self.__azim_range[1]:
            raise ValueError(f"{azim_val}º is not a valid speaker rotation angle. Acceptable speaker rotation range: {str(self.__azim_range)}")
        
    def __check_elevation_value(self,elevation_val):
        if not self.__elevation_range[0] <= elevation_val <= self.__elevation_range[1]:
            raise ValueError(f"{elevation_val}º is not a valid speaker elevation angle. Acceptable speaker rotation range: {str(self.__elevation_range)}")
        
    '''Static methods'''