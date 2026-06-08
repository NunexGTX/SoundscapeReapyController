import reapy

with reapy.inside_reaper():
    project = reapy.Project()
    track = project.tracks[0]
    RPR = reapy.reascript_api

    # Find or add ReaVerb
    fx = track.add_fx("ReaVerb")
    fx_idx = fx.index

    # Load preset by name (must match exactly as it appears in REAPER)
    ok = RPR.TrackFX_SetPreset(track.id, fx_idx, "sweetverbi")
    print(f"Preset loaded: {ok}")