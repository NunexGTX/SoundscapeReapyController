import base64
from pathlib import Path
from reapy import reascript_api as RPR
from ..RiReverbs import RiReverbs

class ReverbRIR(RiReverbs):
    plugin_name  = "VST: ReaVerb (Cockos)"
    _PRESET_NAME = "RiReverb"
    _PRESET_FILE = Path(__file__).parent / "Presets" / "ReverbRiR.RPL"

    def _patch_chunk_paths(self, chunk_bytes: bytes, path_map: dict) -> bytes:
        return self._patch_fileldr_paths(chunk_bytes, path_map)

    def _load_rir_preset(self, rir_preset: str):
        local_path = self._get_rir_path(rir_preset)
        if not local_path.exists():
            raise FileNotFoundError(f"RIR file not found: {local_path}")
        chunk_bytes = self._read_rir_chunk(str(self._PRESET_FILE), self._PRESET_NAME)
        stored_paths = self._extract_fileldr_paths(chunk_bytes)
        if not stored_paths:
            raise ValueError("No FILELDR paths in template preset")
        patched = self._patch_chunk_paths(chunk_bytes, {stored_paths[0]: str(local_path)})
        RPR.TrackFX_SetNamedConfigParm(
            self.TrackFX.parent_id, self.TrackFX.index, "vst_chunk",
            base64.b64encode(patched).decode()
        )
