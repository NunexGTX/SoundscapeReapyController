from abc import ABC, abstractmethod
import reapy
from reapy import reascript_api as RPR
import re
import base64

class AudioPluginController(ABC):
    sliderVals = (0,1) #This represents in between which values each parameter must be

    '''Abstract Variables'''
    @property
    @abstractmethod
    def plugin_name(self) -> str:
        pass

    @property
    @abstractmethod
    def _param_defaults(self) -> list:
        pass
    
    '''Constructor'''
    def __init__(self, TrackFX: reapy.FX):
        self.TrackFX = TrackFX

    '''Abstract Methods'''
    @abstractmethod
    def _checkInitialParams(self,params):
        pass

    @abstractmethod
    def _setInitialParams(self,params):
        pass
    
    '''Common Methods'''    
    def _param_val_calc(self,x,min_val,max_val):
        #This uses the formula : (x-xmin)/(xmax-xmin) to rescale the values from 0 to 1
        return (x-min_val)/(max_val-min_val)
    
    def _param_double_val_calc(self,x,min_val,max_val):
        #Used for parameters that go from 0 to 2 (like db parameters less than 1 are negatives more than 1 are positives)
        return self._param_val_calc(x,min_val,max_val)*2
    
    def preset_load(self, rpl_path: str, preset_name: str, path_map: dict = None):
        presets = self._parse_rpl(rpl_path)
        if preset_name not in presets:
            raise ValueError(f"Preset '{preset_name}' not found in {rpl_path}")
        chunk = presets[preset_name]
        if path_map:
            chunk_bytes = base64.b64decode(chunk)
            chunk_bytes = self._patch_fileldr_paths(chunk_bytes, path_map)
            chunk = base64.b64encode(chunk_bytes).decode('ascii')
        RPR.TrackFX_SetNamedConfigParm(self.TrackFX.parent_id, self.TrackFX.index, "vst_chunk", chunk)

    @staticmethod
    def _parse_rpl(rpl_path: str) -> dict:
        with open(rpl_path, 'r') as f:
            content = f.read()
        presets = {}
        for match in re.finditer(r'<PRESET\s+`([^`]+)`\s*([\s\S]*?)\n\s*>', content):
            presets[match.group(1)] = ''.join(match.group(2).split())
        return presets

    @staticmethod
    def _extract_fileldr_paths(chunk_bytes: bytes) -> list:
        MARKER = b'FILELDR\x00'
        paths = []
        offset = 0
        while True:
            idx = chunk_bytes.find(MARKER, offset)
            if idx == -1:
                break
            path_start = idx + len(MARKER) + 8  # skip block_size(4) + unknown(4)
            null_pos = chunk_bytes.index(b'\x00', path_start)
            paths.append(chunk_bytes[path_start:null_pos].decode('utf-8'))
            offset = null_pos + 1
        return paths

    @staticmethod
    def _patch_xml_path(chunk_bytes: bytes, new_path: str) -> bytes:
        return re.sub(
            rb'LastWavFilePath="[^"]*"',
            b'LastWavFilePath="' + new_path.encode('utf-8') + b'"',
            chunk_bytes,
        )

    @staticmethod
    def _read_rir_chunk(rpl_path: str, preset_name: str) -> bytes:
        return base64.b64decode(AudioPluginController._parse_rpl(rpl_path)[preset_name])

    @staticmethod
    def _patch_fileldr_paths(chunk_bytes: bytes, path_map: dict) -> bytes:
        MARKER = b'FILELDR\x00'
        buf = bytearray(chunk_bytes)
        offset = 0
        while True:
            idx = buf.find(MARKER, offset)
            if idx == -1:
                break
            block_size_pos = idx + len(MARKER)
            path_start = block_size_pos + 8
            null_pos = buf.index(b'\x00', path_start)
            old_path = buf[path_start:null_pos].decode('utf-8')
            if old_path in path_map:
                new_path_b = path_map[old_path].encode('utf-8')
                new_block_size = 4 + len(new_path_b) + 1
                buf[block_size_pos:block_size_pos + 4] = new_block_size.to_bytes(4, 'little')
                buf[path_start:null_pos] = new_path_b
                offset = path_start + len(new_path_b) + 1
            else:
                offset = null_pos + 1
        return bytes(buf)

    

