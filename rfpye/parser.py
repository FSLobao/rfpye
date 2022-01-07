# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/01_parser.ipynb (unless otherwise specified).

__all__ = ['evaluate_checksum', 'buffer2base_block', 'create_block', 'parse_bin', 'CrfsGPS', 'CrfsSpectrum',
           'check_block_exists', 'append_spec_data']

# Internal Cell
import os
import gc
from dataclasses import dataclass
from pathlib import Path
from typing import *
from collections import defaultdict, namedtuple
from fastcore.basics import partialler, listify
from fastcore.utils import parallel
from fastcore.foundation import L, GetAttr
from .constants import *
from .blocks import MAIN_BLOCKS, BaseBlock
from .utils import get_files, getattrs, bin2int, bin2str, cached
# from rfpye.cyparser import cy_extract_compressed
from loguru import logger
import pandas as pd
import numpy as np
from rich import print
# For scripts
config = {
    "handlers": [
        {
            "sink": "parser.log",
            "serialize": True,
            "rotation": "1 month",
            "compression": "zip",
            "backtrace": True,
            "diagnose": True,
        },
    ],
}
logger.configure(**config)

# Cell
def evaluate_checksum(file, next_block, data_size) -> int:
    """Receives a byte_block and verify if the calculated checksum is equal to the one registed in the specific byte"""
    checksum = np.frombuffer(file.read(4), np.uint32).item()
    block_size = file.tell() - next_block
    file.seek(-block_size, 1) # Go back to the beginning of the block
    calculated_checksum = (
            np.frombuffer(file.read(12+data_size), dtype=np.uint8)
            .sum()
            .astype(np.uint32)
            .item()
        )
    file.seek(4,1) # skip checksum
    return checksum if calculated_checksum == checksum else None

# Cell
def buffer2base_block(file, next_block: int) -> Union[BaseBlock, None]:
    """Receives an opened file buffer from the bin file and returns a dataclass with the attributes
    'thread_id', 'size', 'type', 'data', 'checksum' or None in case any error is identified.
    """
    thread_id = np.frombuffer(file.read(4), np.uint32).item()
    data_size = np.frombuffer(file.read(4), np.uint32).item()
    data_type = np.frombuffer(file.read(4), np.int32).item()
    data_block = file.read(data_size)
    if (checksum := evaluate_checksum(file, next_block, data_size)) is None:
        return None
    return BaseBlock(thread_id, data_size, data_type, data_block, checksum)

# Cell
def create_block(file, next_block) -> Union[GetAttr, None]:
    """Receives a byte_block, and converts it into one of the main classes
    Args: byte_block: A byte block directly returned from the file
    Returns: The Instance of the Block Type or None in case of error
    """
    if (base_block := buffer2base_block(file, next_block)) is None:
        return None, None
    block_type = base_block.type
    constructor = MAIN_BLOCKS.get(block_type)
    if not constructor:
        _ = logger.log(
            "INFO", f"This block type constructor is not implemented: {block_type}"
        )
        return None, None
    block = constructor(base_block)
    if getattr(block, "gerror", -1) != -1 or getattr(block, "gps_status", -1) == 0:
        _ = logger.log("INFO", f"Block with error: {block_type}")
        return None, None  # spectral or gps blocks with error
    return getattrs(block, KEY_ATTRS.get(block.type)), block

# Cell
def parse_bin(bin_file: Union[str, Path], precision=np.float32) -> dict:
    """Receives a CRFS binfile and returns a dictionary with the file metadata, a GPS Class and a list with the different Spectrum Classes
    A block is a piece of the .bin file with a known start and end and that contains different types of information.
    It has several fields: file_type, header, data and footer.
    Each field has lengths and information defined in the documentation.
    Args:
        bin_file (Union[str, Path]): path to the bin file

    Returns:
        Dictionary with the file metadata, file_version, string info, gps and spectrum blocks.
    """
    bin_file = Path(bin_file)
    meta = {}
    fluxos = {}
    gps = CrfsGPS()
    with  open(bin_file, mode="rb") as file:
        # The first block of the file is the header and is 36 bytes long.
        header = file.read(BYTES_HEADER)
        meta["filename"] = bin_file.name
        meta["file_version"] = bin2int(header[:4])
        meta["string"] = bin2str(header[4:])
        file_size = file.seek(0, 2)
        file.seek(36, 0)
        while (next_block := file.tell()) < file_size:
            attrs, block = create_block(file, next_block)
            if not file.read(4) == b'UUUU':
                logger.warning("End of block not found, skipping it")
                continue
            if block is None:
                continue
            dtype = block.type
            if dtype == 40:
                for k in BLOCK_ATTRS.get(40, []):
                    getattr(gps, f"_{k}").append(getattr(block, k))
                continue
            elif dtype in VECTOR_BLOCKS:
                append_spec_data(attrs, fluxos, block, precision)
            else:
                meta.update(attrs)
    meta["gps"] = gps
    meta["spectrum"] = L(fluxos.values())
    return meta


# Cell
@dataclass
class CrfsGPS:
    """Class with the GPS Attributes from the CRFS Bin File"""

    _gps_datetime: L = L()
    _latitude: L = L()
    _longitude: L = L()
    _altitude: L = L()
    _num_satellites: L = L()

    @property
    def latitude(self) -> float:
        return np.median(self._latitude) if self._latitude else -1

    @property
    def longitude(self) -> float:
        return np.median(self._longitude) if self._longitude else -1

    @property
    def altitude(self) -> float:
        return np.median(self._altitude) if self._altitude else -1

    @property
    def num_satellites(self) -> float:
        return np.median(self._num_satellites) if self._num_satellites else 0

    def __repr__(self):
        return f"GPS Data - Median of Coordinates: {self.latitude:.5f}:{self.longitude:.5f} Altitude: {self.altitude:.2f} #Satellites: {self.num_satellites:.1f}"


class CrfsSpectrum(GetAttr):
    """Class with the metadata and levels of a spectrum block from a CRFS Bin File"""

    def __init__(self, metadata: namedtuple, precision=np.float32):
        self.default = metadata
        self._timestamp: L = L()
        self._data: L = L()
        self.precision = precision

    def __len__(self):
        return self.levels.shape[0]

    def __repr__(self):
        return repr(self.default)

    def __str__(self):
        return f"""Blocks of Type: {self.type}, Thread_id: {self.thread_id}, Start: {self.start_mega} MHz, Stop: {self.stop_mega} MHz"""

    @cached
    def start_dateidx(self):
        return self._timestamp[0].item()

    @cached
    def stop_dateidx(self):
        return self._timestamp[-1].item()

    @cached
    def levels(self):
        """Return the spectrum levels"""
        if self.type in UNCOMPRESSED:
            levels = np.concatenate(self._data).reshape((-1, self.ndata))
        elif self.type in COMPRESSED:
            levels = cy_extract_compressed(
                list(self._data),
                len(self._data),
                int(self.ndata),
                int(self.thresh),
                float(self.minimum),
            )
        else:
            raise ValueError(
                "The current block is not of type spectrum or it's not implemented yet"
            )
        self._data = None
        gc.collect()
        if self.precision != np.float32:
            levels = levels.astype(self.precision)
        return levels

    @cached
    def frequencies(self) -> np.ndarray:
        return np.linspace(self.start_mega, self.stop_mega, num=self.ndata)

    def matrix(self):
        """Returns the matrix formed from the spectrum levels and timestamp"""
        index = self._timestamp if len(self._timestamp) == len(self) else None
        data = pd.DataFrame(self.levels, index=index, columns=self.frequencies)
        data.columns.name = "Frequencies"
        data.index.name = "Time"
        return data

# Cell
def check_block_exists(attrs, fluxos, precision):
    """Receives a dict of attributes and check if its values exist as keys in fluxos, otherwise create one and set to CrfsSpectrum Class"""
    values = tuple(attrs.values())
    if values not in fluxos:
        metadata = namedtuple("SpecData", attrs.keys())
        fluxos[values] = CrfsSpectrum(metadata(*attrs.values()), precision)
    return values, fluxos

# Cell
def append_spec_data(attrs, fluxos, block, precision=np.float32) -> None:
    values, fluxos = check_block_exists(attrs, fluxos, precision)
    time = getattr(block, "wallclock_datetime", None)
    data = getattr(block, "levels", None)
    if time is not None:
        fluxos[values]._timestamp.append(time)
    if data is not None:
        fluxos[values]._data.append(data)