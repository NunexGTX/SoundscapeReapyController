import base64
from pathlib import Path
from reapy import reascript_api as RPR
from ..RiReverbs import RiReverbs

class MultiConvReverb(RiReverbs):
    plugin_name  = "VST: sparta_multiconv (AALTO) (64ch)"
    _PRESET_NAME = "AmbisonicReverbConvolve"
    _PRESET_FILE = Path(__file__).parent / "Presets" / "MultiConv.RPL"

    def _patch_chunk_paths(self, chunk_bytes: bytes, path_map: dict) -> bytes:
        return self._patch_xml_path(chunk_bytes, next(iter(path_map.values())))

    def _load_rir_preset(self, rir_preset: str):
        local_path = self._get_rir_path(rir_preset)
        if not local_path.exists():
            raise FileNotFoundError(f"RIR file not found: {local_path}")
        chunk_bytes = self._read_rir_chunk(str(self._PRESET_FILE), self._PRESET_NAME)
        patched = self._patch_chunk_paths(chunk_bytes, {None: str(local_path)})
        RPR.TrackFX_SetNamedConfigParm(
            self.TrackFX.parent_id, self.TrackFX.index, "vst_chunk",
            base64.b64encode(patched).decode()
        )
