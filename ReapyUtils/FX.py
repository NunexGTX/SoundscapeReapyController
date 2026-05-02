import reapy

'''
This fuction returns the ambisonic fx either in the BUS track or master track (which will be accessed if Track_idx is -1)
'''
def getFX_byName(reaper_project: reapy.Project,plugin_name: str, track: reapy.Track):
    return track.fxs[plugin_name]

def getFX_byIndex(reaper_project: reapy.Project,plugin_index: int, track: reapy.Track):
    return track.fxs[plugin_index]