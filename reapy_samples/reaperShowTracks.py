import reapy

#Load the project
#project = reapy.Project()

'''A function that prints all tracks with their index and their corresponding name'''
def showProjectTracks(project):
    TrackList = reapy.TrackList(project) #We retrieve the TrackList object that has the track list
    print(project.name, "Tracks")
    for Track in TrackList:
        print(Track.index, " - ",Track.name) #Access the track and print its index and name