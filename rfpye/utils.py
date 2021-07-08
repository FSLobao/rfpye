# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/02_utils.ipynb (unless otherwise specified).

__all__ = ['get_files', 'bin2int', 'bin2str', 'bin2date', 'bin2time', 'pad', 'optimize_floats', 'optimize_ints',
           'optimize_objects', 'df_optimize', 'public_attrs', 'getattrs']

# Cell
import os
from typing import *
import numpy as np
import pandas as pd
from fastcore.foundation import L
from fastcore.xtras import Path
from fastcore.basics import uniqueify, listify
from .constants import EXCLUDE_ATTRS

# Cell
def _get_files(p, fs, extensions=None):
    p = Path(p)
    res = [
        p / f
        for f in fs
        if not f.startswith(".")
        and ((not extensions) or f'.{f.split(".")[-1].lower()}' in extensions)
    ]
    return res

# Cell
def get_files(path, extensions=None, recurse=True, folders=None, followlinks=True):
    "Get all the files in `path` with optional `extensions`, optionally with `recurse`, only in `folders`, if specified."
    path = Path(path)
    folders = L(folders)
    if extensions is not None:
        extensions = set(uniqueify(extensions))
        extensions = {e.lower() for e in extensions}
    if recurse:
        res = []
        for i, (p, d, f) in enumerate(
            os.walk(path, followlinks=followlinks)
        ):  # returns (dirpath, dirnames, filenames)
            if len(folders) != 0 and i == 0:
                d[:] = [o for o in d if o in folders]
            else:
                d[:] = [o for o in d if not o.startswith(".")]
            if len(folders) != 0 and i == 0 and "." not in folders:
                continue
            res += _get_files(p, f, extensions)
    else:
        f = [o.name for o in os.scandir(path) if o.is_file()]
        res = _get_files(path, f, extensions)
    return L(res)

# Cell
def bin2int(binary_data: bytes, is_signed: bool = True) -> int:
    """Convert bytes number to int
    :param binary_data: valor de int comprimido
    :param is_signed: indica se é um valor negativo ou não
    :return: decoded int
    """
    return int.from_bytes(binary_data, byteorder="little", signed=is_signed)


def bin2str(binary_data: bytes) -> str:
    """
    bytes > str
    :param binary_data: valor de str comprimida
    :return: str traduzida

    Conversor binario para str.
    Erros do 'decoder' são ignorados.
    Ignora o final do dado binario ('\x00') que é usado apenas para manter o tamanho dos campos.
    """
    return binary_data.decode(errors="ignore").rstrip("\x00")


def bin2date(binary_data: bytes) -> Tuple[int, int, int, int]:
    """
    bytes > (int, int, int, int)
    :param binary_data: valor de data comprimido
    :return: dia, mês, ano, reserva

    Date is expressed as dd/mm/yy/null, i.e. 4 bytes
    """
    day = binary_data[:1]
    month = binary_data[1:2]
    year = binary_data[2:3]
    reserve = binary_data[3:]
    return bin2int(day), bin2int(month), bin2int(year), bin2int(reserve)


def bin2time(binary_data: bytes) -> Tuple[int, int, int, int]:
    """
    bytes > (int, int, int, int)
    :param binary_data: valor de hora comprimido
    :return: horas, minutos, segundos, décimos de segundo

     Time is expressed as hh/mm/ss/cc (4 bytes), where cc is centiseconds;
     and a 32-bit nanoseconds field, expressed as an unsigned 32-bit integer,
     to support higher precision where required.
     At most one of cc and nanoseconds can be nonzero.
    """
    hours = binary_data[:1]
    minutes = binary_data[1:2]
    seconds = binary_data[2:3]
    centiseconds = binary_data[3:]
    return bin2int(hours), bin2int(minutes), bin2int(seconds), bin2int(centiseconds)

def pad(text, block_size):

    # Calculate the missing number of
    # bytes, say N
    pad_size = block_size - len(text) % block_size

    # Pad with character of N
    fit_text = text + chr(pad_size) * pad_size

    return (fit_text,)

# Cell
def optimize_floats(df: pd.DataFrame, exclude = None) -> pd.DataFrame:
    floats = df.select_dtypes(include=["float64"]).columns.tolist()
    floats = [c for c in floats if c not in listify(exclude)]
    df[floats] = df[floats].apply(pd.to_numeric, downcast="float")
    return df


def optimize_ints(df: pd.DataFrame, exclude=None) -> pd.DataFrame:
    ints = df.select_dtypes(include=["int64"]).columns.tolist()
    ints = [c for c in ints if c not in listify(exclude)]
    df[ints] = df[ints].apply(pd.to_numeric, downcast="integer")
    return df


def optimize_objects(df: pd.DataFrame, datetime_features: List[str], exclude=None) -> pd.DataFrame:
    for col in df.select_dtypes(include=["object"]).columns.tolist():
        if col not in datetime_features:
            if col in listify(exclude): continue
            num_unique_values = len(df[col].unique())
            num_total_values = len(df[col])
            if float(num_unique_values) / num_total_values < 0.5:
                dtype = "category"
            else:
                dtype = "string"
            df[col] = df[col].astype(dtype)
        else:
            df[col] = pd.to_datetime(df[col]).dt.date
    return df


def df_optimize(df: pd.DataFrame, datetime_features: List[str] = [], exclude = None):
    return optimize_floats(optimize_ints(optimize_objects(df, datetime_features, exclude), exclude), exclude)

# Cell
def public_attrs(obj: Any) -> L:
    """Receives an object and return its public attributes (not starting with underscore _) excluding those listed in `EXCLUDE_ATTRS`"""
    return L(k for k in dir(obj) if not k.startswith("_") and k not in EXCLUDE_ATTRS)


def getattrs(obj: Any, attrs: Iterable = None) -> L:
    if attrs is None:
        attrs = public_attrs(obj)
    return {x: getattr(obj, x) for x in attrs}