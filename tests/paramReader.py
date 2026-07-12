import reapy

project = reapy.Project()

track = project.tracks["s"]

fx = track.fxs[0]

print(fx.params[1])
print(fx.params[0])

fx.params[3] = ((2-1)/(128-1))

print(fx.params[3])