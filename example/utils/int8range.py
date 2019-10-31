"""Support for INT8RANGE type in PostgreSQL.

See https://github.com/kvesteri/sqlalchemy-utils/pull/401.
"""
from sqlalchemy_utils.types.range import RangeType, IntRangeComparator
from sqlalchemy.dialects.postgresql import INT8RANGE
import intervals

__all__ = ('Int8RangeType',)


class Int8RangeType(RangeType):
    impl = INT8RANGE
    comparator_factory = IntRangeComparator

    def __init__(self, *args, **kwargs):
        super(Int8RangeType, self).__init__(*args, **kwargs)
        self.interval_class = intervals.IntInterval
