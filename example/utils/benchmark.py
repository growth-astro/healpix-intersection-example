from contextlib import contextmanager
from time import perf_counter
import numpy as np


@contextmanager
def time(label):
    start = perf_counter()
    yield
    end = perf_counter()
    elapsed = np.format_float_positional(end - start, 1, trim='0')
    print('***', label, '-', elapsed, 's')
