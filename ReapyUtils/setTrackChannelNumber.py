import reapy

track = reapy.Project().tracks[0]
n_channels = int(track.get_info_value("I_NCHAN"))
print(n_channels)  # e.g. 2 for stereo

track.set_info_value("I_NCHAN", 4)   # Set to 4 channels