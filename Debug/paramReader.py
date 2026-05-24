import reapy

project = reapy.Project()

track = project.tracks["s"]

fx = track.fxs[0]

print(fx.params[1])
print(fx.params[0])