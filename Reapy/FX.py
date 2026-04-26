import reapy

'''
This fuction returns the ambisonic fx either in the BUS track or master track (which will be accessed if Track_idx is -1)
'''
def getFX_byName(reaper_project: reapy.Project,plugin_name: str, Track_idx = -1):
    if Track_idx == -1:
        return reaper_project.master_track.fxs[plugin_name]
    return reapy.Track(Track_idx,reaper_project).fxs[plugin_name]

def getFX_byIndex(reaper_project: reapy.Project,plugin_index: int, Track_idx = -1):
    if Track_idx == -1:
        return reaper_project.master_track.fxs[plugin_index]
    return reapy.Track(Track_idx,reaper_project).fxs[plugin_index]