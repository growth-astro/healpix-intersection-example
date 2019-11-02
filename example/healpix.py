"""Model base classes for multiresolution HEALPix data."""
from astropy_healpix import uniq_to_level_ipix
from mocpy import MOC
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.dialects.postgresql import INT8RANGE
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.orm.mapper import Mapper
from psycopg2.extras import NumericRange

LEVEL = MOC.HPY_MAX_NORDER
"""Base HEALPix resolution. This is the maximum HEALPix level that can be
stored in a signed 8-byte integer data type."""


class Tile:
    """Mixin class for a table that stores a HEALPix multiresolution tile."""

    nested_range = Column(
        INT8RANGE, primary_key=True,
        comment=f'Range of HEALPix nested indices at nside=2**{LEVEL}')

    def __init__(self, *args, uniq=None, **kwargs):
        super().__init__(*args, **kwargs)
        if uniq is not None:
            self.uniq = uniq

    @hybrid_property
    def uniq(self):
        """HEALPix UNIQ pixel index."""
        # This is the same expression as in astropy_healpix.level_ipix_to_uniq,
        # but reproduced here so that SQLAlchemy can map it to SQL.
        ipix = self.nested_range.lower
        return ipix + (1 << 2 * (LEVEL + 1))

    @uniq.setter
    def uniq(self, value):
        """HEALPix UNIQ pixel index."""
        level, ipix = uniq_to_level_ipix(value)
        level_diff = (LEVEL - level)
        lower = ipix << level_diff
        upper = (ipix + 1) << level_diff
        self.nested_range = NumericRange(lower, upper)


def _class_or_lambda(cls):
    """Shim to allow subclasses to set tile_class to a lambda function."""
    # Adopted from sqlalchemy.orm.relationships.RelationshipProperty.entity
    if callable(cls) and not isinstance(cls, (type, Mapper)):
        cls = cls()
    return cls


class Region:
    """Mixin class for a HEALPix multiresolution region (e.g., multi-order
    coverage map)."""

    @declared_attr
    def tiles(cls):
        return relationship(cls.tile_class, backref=cls.__tablename__)

    @classmethod
    def from_moc(cls, moc, *args, **kwargs):
        """Create a new instance from a multi-order coverage map.

        Parameters
        ----------
        moc : mocpy.MOC
            The multi-order coverage map.

        Returns
        -------
        list
            A list of Tile instances.
        """
        tile_class = _class_or_lambda(cls.tile_class)
        nested_ranges = moc._interval_set.nested
        # FIXME: MOCpy should return an array of size(0, 2) 0 for an empty MOC,
        # but it actually returns an array of size(1, 0).
        if nested_ranges.shape == 0:
            nested_ranges = nested_ranges.reshape(-1, 2)
        tiles = [tile_class(nested_range=NumericRange(lo, hi))
                 for lo, hi in nested_ranges]
        return cls(*args, tiles=tiles, **kwargs)

    @classmethod
    def from_polygon(cls, polygon, *args, **kwargs):
        """Create a new instance from a polygon.

        Parameters
        ----------
        polygon : astropy.coordinates.SkyCoord
            The vertices of the polygon.

        Returns
        -------
        list
            A list of Tile instances.
        """
        moc = MOC.from_polygon_skycoord(polygon)
        return cls.from_moc(moc, *args, **kwargs)
