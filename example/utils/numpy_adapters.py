"""Adapt Numpy values for postgres databases.

Inspired by https://github.com/kgullikson88/Stellar_database/blob/master/NumpyAdaptorsPostgreSQL.py.
"""
import numpy as np
from psycopg2.extensions import register_adapter, AsIs


def adapt_literal(const):
    return lambda arg: const


for dtype in [np.int8, np.int16, np.int32, np.int64,
              np.uint8, np.uint16, np.uint32, np.uint64,
              np.float32, np.float64]:
    register_adapter(dtype, AsIs)

register_adapter(np.nan, lambda value: "'NaN'")
register_adapter(np.inf, lambda value: "'Infinity'")
register_adapter(-np.inf, lambda value: "'-Infinity'")
register_adapter(np.ndarray, lambda value: AsIs(value.tolist()))
