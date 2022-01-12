# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/01_parser.ipynb (unless otherwise specified).

__all__ = ['parse_bin', 'CrfsGPS', 'CrfsSpectrum']

# Cell
import sys, os
from pathlib import Path

# Insert in Path Project Directory
sys.path.insert(0, str(Path().cwd().parent))

# Internal Cell
import os
import gc
from dataclasses import dataclass
from pathlib import Path
from typing import *
from collections import defaultdict
from dataclasses import asdict, make_dataclass
from fastcore.utils import parallel
from fastcore.foundation import L, GetAttr
from .constants import *
from .blocks import MAIN_BLOCKS, BaseBlock
from .utils import get_files, getattrs, bin2int, bin2str, cached
from .cyparser import cy_extract_compressed
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

# Internal Cell
def evaluate_checksum(file, next_block, data_size) -> int:
    """Receives a byte_block and verify if the calculated checksum is equal to the one registed in the specific byte"""
    start = file.tell()
    try:
        checksum = np.frombuffer(file.read(4), np.uint32).item()
    except ValueError:
        logger.error(f"Erro na leitura do checksum, posição: {file.tell()}")
        file.seek(4, 1)
        return None
    block_size = file.tell() - next_block
    file.seek(-block_size, 1) # Go back to the beginning of the block
    calculated_checksum = (
            np.frombuffer(file.read(12+data_size), dtype=np.uint8)
            .sum()
            .astype(np.uint32)
            .item()
        )
    file.seek(4,1) # skip checksum
    if checksum != calculated_checksum:
        logger.error(f"Checksum diferente: {checksum} != {calculated_checksum}. Posicao: {file.tell()}")
        return None
    return checksum

# Internal Cell
def buffer2base_block(file, next_block: int) -> Union[BaseBlock, None]:
    """Receives an opened file buffer from the bin file and returns a dataclass with the attributes
    'thread_id', 'size', 'type', 'data', 'checksum' or None in case any error is identified.
    """
    thread_id = np.frombuffer(file.read(4), np.int32).item()
    block_size = np.frombuffer(file.read(4), np.int32).item()
    block_type = np.frombuffer(file.read(4), np.int32).item()
    data_block = file.read(block_size)
    if (checksum := evaluate_checksum(file, next_block, block_size)) is None:
        return None, None
    return block_type, BaseBlock(thread_id, block_size, block_type, data_block, checksum)

# Internal Cell
def create_block(file, next_block) -> Tuple:
    """Receives a byte_block, and converts it into one of the main classes
    Args: byte_block: A byte block directly returned from the file
    Returns: The Instance of the Block Type or None in case of error
    """
    block_type, base_block = buffer2base_block(file, next_block)
    if block_type is None:
        return None, None
    constructor = MAIN_BLOCKS.get(block_type)
    if not constructor:
        logger.warning(f"This block type constructor is not implemented: {block_type}")
        return None, None
    block = constructor(base_block)
    if getattr(block, "gerror", -1) != -1 or getattr(block, "gps_status", -1) == 0:
        logger.error("INFO", f"Block with error: {block_type}")
        return None, None  # spectral or gps blocks with error
    return block_type, block

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
    with open(bin_file, mode="rb") as file:
        # The first block of the file is the header and is 36 bytes long.
        header = file.read(BYTES_HEADER)
        meta["filename"] = bin_file.name
        meta["file_version"] = bin2int(header[:4])
        meta["string"] = bin2str(header[4:])
        file_size = file.seek(0, 2)
        logger.info(f'Tamanho do arquivo: {file_size} bytes')
        file.seek(36, 0)
        while (next_block := file.tell()) < file_size:
            block_type, block = create_block(file, next_block)
            if (eof := file.read(4)) != b'UUUU':
                logger.error(f"EOF diferente de UUUU: {eof}, posicao: {file.tell()}")
                continue
            if block is None:
                continue
            if block_type == 40:
                gps._data.append(block)
            elif block_type in VECTOR_BLOCKS:
                append_spec_data(block_type,fluxos, block, precision)
            else:
                meta.update(getattrs(block, KEY_ATTRS.get(block_type)))
    meta["gps"] = gps
    meta["spectrum"] = L(fluxos.values())
    return meta


# Cell
class CrfsGPS:
    """Class with the GPS Attributes from the CRFS Bin File"""
    def __init__(self) -> None:
        self._data: L = L()

    def __len__(self):
        return len(self._data)

    def __getitem__(self, key):
        return self._latitude[key], self._longitude[key], self._altitude[key], self._num_satellites[key]

    def __iter__(self):
        return zip(self._latitude, self._longitude)

    @cached
    def _gps_datetime(self):
        return self._data.attrgot("gps_datetime")

    @cached
    def _latitude(self):
        return self._data.attrgot("latitude")

    @cached
    def _longitude(self):
        return self._data.attrgot("longitude")

    @cached
    def _altitude(self):
        return self._data.attrgot("altitude")

    @cached
    def _num_satellites(self):
        return self._data.attrgot("num_satellites")

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

    def __init__(self, metadata, precision=np.float32):
        self.default = metadata
        self._data: L = L()
        self.precision = precision

    def __getitem__(self, key):
        return self.timestamp[key], self.levels[key]

    def __iter__(self):
        return iter(self.levels)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return repr(self.default)

    def __str__(self):
        return f"""Blocks of Type: {self.type}, Thread_id: {self.thread_id}, Start: {self.start_mega} MHz, Stop: {self.stop_mega} MHz"""

    @cached
    def timestamp(self):
        return self._data.attrgot('wallclock_datetime')

    @cached
    def start_dateidx(self):
        return getattr(self._data[0], 'wallclock_datetime').item()

    @cached
    def stop_dateidx(self):
        return getattr(self._data[-1], 'wallclock_datetime').item()

    @cached
    def levels(self):
        """Return the spectrum levels"""
        if self.type in UNCOMPRESSED:
            levels = np.empty((len(self._data), self.ndata), dtype=self.precision)
            for i, level in enumerate(self._data.attrgot('levels')):
                levels[i,:] = level
            # levels = np.concatenate(self._data.attrgot('levels')).reshape((-1, self.ndata))
        elif self.type in COMPRESSED:
            levels = cy_extract_compressed(
                list(self._data.attrgot('levels')),
                len(self._data),
                int(self.ndata),
                int(self.thresh),
                float(self.minimum),
            )
        else:
            raise ValueError(
                "The current block is not of type spectrum or it's not implemented yet"
            )
        if self.precision != np.float32:
            levels = levels.astype(self.precision)
        return levels

    @cached
    def frequencies(self) -> np.ndarray:
        return np.linspace(self.start_mega, self.stop_mega, num=self.ndata)

    def matrix(self):
        """Returns the matrix formed from the spectrum levels and timestamp"""
        index = self.timestamp if len(self.timestamp) == len(self) else None
        data = pd.DataFrame(self.levels, index=index, columns=self.frequencies)
        data.columns.name = "Frequencies"
        data.index.name = "Time"
        return data

# Internal Cell
def append_spec_data(block_type, fluxos, block, precision=np.float32) -> None:
    """Append the spectrum data to the fluxos dict"""
    keys, vals = getattrs(block, KEY_ATTRS.get(block_type), as_tuple=True)
    if vals not in fluxos:
        metadata = make_dataclass('SpecData', fields=[(k,type(k)) for k in keys])
        fluxos[vals] = CrfsSpectrum(metadata(*vals), precision)
    fluxos[vals]._data.append(block)