# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/04_constants.ipynb (unless otherwise specified).

__all__ = ['BYTES_HEADER', 'ENDMARKER', 'EXCLUDE_ATTRS', 'DICT_PROCESSING', 'DICT_UNIT', 'TUNING_BLOCK', 'BYTES_TIMED',
           'BYTES_TIMED_NE', 'BYTES_6', 'BYTES_20', 'BYTES_21', 'BYTES_24', 'BYTES_40', 'BYTES_41', 'BYTES_42',
           'BYTES_51', 'BYTES_64', 'BYTES_65', 'BYTES_V5', 'BYTES_66', 'BYTES_67', 'KEY_ATTRS', 'TIMED_BLOCKS',
           'SPECTRAL_BLOCKS', 'OCC', 'VECTOR_BLOCKS', 'UNCOMPRESSED', 'COMPRESSED', 'GPS_BLOCK', 'BLOCK_ATTRS']

# Cell
from typing import Mapping, List, Tuple

# Cell
BYTES_HEADER = 36

ENDMARKER: bytes = b"UUUU"

EXCLUDE_ATTRS: List = (
    "count",
    "index",
    "checksum",
    "default",
    "walldate",
    "walltime",
    "wallnano",
    "wallclock_datetime",
    "timestamp",
    "data",
    "raw_data",
    "levels",
    "matrix",
    "frequencies",
    "agc",
    "tunning",
)

DICT_PROCESSING: Mapping[int, str] = {
    0: "single measurement",
    1: "average",
    2: "peak",
    3: "minimum",
}

DICT_UNIT: Mapping[int, str] = {0: "dBm", 1: "dBμV/m"}

TUNING_BLOCK: Mapping[int, str] = {
    0: "completed without error",
    1: "error occurred",
    2: "radio produced an error",
    3: "GPRS transmission occured during capture",
    4: "ADC overflowed during capture",
}


BYTES_TIMED: Mapping[int, slice] = {
    0: slice(0, 4),
    1: slice(4, 8),
    2: slice(8, 12),
    3: slice(12, 14),
    4: slice(14, 18),
    5: slice(18, 20),
    6: slice(20, 24),
    7: slice(24, 26),
    8: slice(26, 28),
}

BYTES_TIMED_NE: Mapping[int, slice] = {0: slice(0, 4), 1: slice(4, 8), 2: slice(8, 12)}

BYTES_6: Mapping[int, slice] = {
    0: slice(0, 4),
    1: slice(4, 8),
    2: slice(8, 12),
    3: slice(12, 16),
    4: slice(16, 20),
    5: slice(20, 24),
}

BYTES_20: Mapping[int, slice] = {
    0: slice(0, 4),
    1: slice(4, 8),
    2: slice(8, 12),
    3: slice(12, 16),
    4: slice(16, 20),
    5: slice(20, 24),
    6: slice(24, 28),
    7: slice(28, 32),
    8: slice(32, 36),
    9: slice(36, 40),
}


BYTES_21: Mapping[int, slice] = {0: slice(0, 16), 1: slice(16, 20)}

BYTES_24: Mapping[int, slice] = {0: slice(0, 4), 1: slice(4, 8)}

BYTES_40: Mapping[int, slice] = {
    3: slice(12, 16),
    4: slice(16, 20),
    5: slice(20, 21),
    6: slice(21, 22),
    7: slice(22, 24),
    8: slice(24, 28),
    9: slice(28, 32),
    10: slice(32, 36),
    11: slice(36, 40),
}

BYTES_41: Mapping[int, slice] = {3: slice(12, 44), 4: slice(44, 48)}

BYTES_42: Mapping[int, slice] = {
    3: slice(12, 16),
    4: slice(16, 20),
    5: slice(20, 52),
    6: slice(52, 56),
}

BYTES_51: Mapping[int, slice] = {5: slice(20, 24)}

BYTES_64: Mapping[int, slice] = {22: slice(52, 56), 23: slice(56, 60)}

BYTES_65: Mapping[int, slice] = {
    9: slice(28, 32),
    10: slice(32, 33),
    11: slice(33, 34),
    12: slice(34, 36),
    13: slice(36, 37),
    14: slice(37, 38),
    15: slice(38, 39),
    16: slice(39, 40),
    17: slice(40, 42),
    18: slice(42, 44),
    19: slice(44, 48),
}

BYTES_V5: Mapping[int, slice] = {3: slice(12, 16), 4: slice(16, 20), 5: slice(20, 24)}

BYTES_66: Mapping[int, slice] = {3: slice(12, 16), 4: slice(16, 20), 5: slice(20, 24)}

BYTES_67: Mapping[int, slice] = {3: slice(12, 16), 4: slice(16, 20), 5: slice(20, 24)}

# Cell
KEY_ATTRS = {
    1: ('hostname',),
    3: ('description',),
    4: (
        "type",
        "thread_id",
        "start_mega",
        "stop_mega",
        "ndata",
        "processing",
        "antuid",
    ),
    5: (),
    6: ("type",
       "antuid",
       ),
    7: (
        "type",
        "thread_id",
        "thresh",
        "minimum",
        "start_mega",
        "stop_mega",
        "processing",
        "ndata",
        "antuid",
    ),
    8: (
        "type",
        "thread_id",
        "start_mega",
        "stop_mega",
        "ndata",
        "antuid",
    ),
    20: (
        "n_spectral_blocks",
        "nddt",
    ),
    21: ("hostname", "method", "unit_info", "file_number"),
    22: ('description',),
    23: (),
    24: ('description',),
    41: ("identifier",),
    42: ("identifier",),
    51: (),
    60: (
        "type",
        "thread_id",
        "start_mega",
        "stop_mega",
        "ndata",
        "nloops",
        "processing",
        "antuid",
    ),
    61: (
        "type",
        "thread_id",
        "thresh",
        "minimum",
        "start_mega",
        "stop_mega",
        "ndata",
        "nloops",
        "processing",
        "antuid",
    ),
    62: (
        "type",
        "thread_id",
        "start_mega",
        "stop_mega",
        "thresh",
        "ndata",
        "antuid",
    ),
    63: (
        "type",
        "thread_id",
        "description",
        "start_mega",
        "stop_mega",
        "dtype",
        "ndata",
        "processing",
        "antuid",
    ),
    64: (
        "type",
        "thread_id",
        "thresh",
        "minimum",
        "description",
        "start_mega",
        "stop_mega",
        "dtype",
        "ndata",
        "processing",
        "antuid",
    ),
    65: (
        "type",
        "thread_id",
        "start_mega",
        "stop_mega",
        "dtype",
        "ndata",
        "processing",
        "antuid",
    ),
    67: (
        "type",
        "thread_id",
        "description",
        "start_mega",
        "stop_mega",
        "dtype",
        "ndata",
        "bw",
        "processing",
        "antuid",
    ),
    68: (
        "type",
        "thread_id",
        "thresh",
        "description",
        "start_mega",
        "stop_mega",
        "minimum",
        "dtype",
        "ndata",
        "bw",
        "processing",
        "antuid",
    ),
    69: (
        "type",
        "thread_id",
        "description",
        "start_mega",
        "stop_mega",
        "dtype",
        "ndata",
        "bw",
        "opcount",
        "antuid",
    ),
}

TIMED_BLOCKS = (40, 41, 42, 51, 63, 64, 65, 66, 67, 68, 69)

SPECTRAL_BLOCKS = (4, 7, 60, 61, 63, 64, 67, 68)

OCC = (8, 62, 65, 69)

VECTOR_BLOCKS = SPECTRAL_BLOCKS + OCC

UNCOMPRESSED = (4, 60, 63, 67) + OCC

COMPRESSED = (7, 61, 64, 68)

GPS_BLOCK = 40

BLOCK_ATTRS: Mapping[int, Tuple] = {
    8: ("wallclock_datetime"),
    21: (),
    40: (
        "gps_datetime",
        "latitude",
        "longitude",
        "altitude",
        "num_satellites",
    ),
    41: (),
    42: (),
    60: ("wallclock_datetime"),
    61: ("wallclock_datetime"),
    62: ("wallclock_datetime"),
    63: ("wallclock_datetime"),
    64: ("wallclock_datetime"),
    65: ("wallclock_datetime"),
    67: ("wallclock_datetime"),
    68: ("wallclock_datetime"),
    69: ("wallclock_datetime"),
}