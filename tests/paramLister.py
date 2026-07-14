import reapy

project = reapy.Project()
track = project.tracks["s"]

fx = track.fxs["VST: sparta_matrixconv (AALTO) (64ch)"]
for i, p in enumerate(fx.params):
    print(i, p.name, float(p))