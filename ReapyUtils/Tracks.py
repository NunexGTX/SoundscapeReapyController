import reapy

'''A function that prints all tracks with their index and their corresponding name'''
def showProjectTracks(reaper_project: reapy.Project):
    TrackList = reapy.TrackList(reaper_project) #We retrieve the TrackList object that has the track list
    print(reaper_project.name, "Tracks")
    for Track in TrackList:
        print(Track.index, " - ",Track.name) #Access the track and print its index and name

def getTrack_byName(reaper_project: reapy.Project, track_name):
    return reaper_project._get_track_by_name(track_name)

def getTrack_byIndex(reaper_project, idx):
    return reapy.Track(idx,reaper_project)

def getMasterTrack(reaper_project: reapy.Project):
    reaper_project.master_track()