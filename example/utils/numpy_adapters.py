import numpy as np
from psycopg2.extensions import register_adapter, AsIs

register_adapter(np.float64, AsIs)
register_adapter(np.int64, AsIs)
