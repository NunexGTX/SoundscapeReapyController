import reapy

project = reapy.Project()

track = project.tracks["construction 2"]

fx = track.fxs[0]

print(fx.params[5])