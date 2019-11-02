"""Model base classes for multiresolution HEALPix data."""
from astropy_healpix import level_ipix_to_uniq, uniq_to_level_ipix
from intervals import IntInterval
from mocpy import MOC
from sqlalchemy import Column
from sqlalchemy_utils.types.range import Int8RangeType
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.orm.mapper import Mapper

LEVEL = 29
"""Base HEALPix resolution. This is the maximum HEALPix level that can be
stored in a signed 8-byte integer data type."""


class Tile:
    """Mixin class for a table that stores a HEALPix multiresolution tile."""

    nested_range = Column(
        Int8RangeType, primary_key=True,
        comment=f'Range of HEALPix nested indices at nside=2**{LEVEL}')

    def __init__(self, *args, uniq=None, **kwargs):
        super().__init__(*args, **kwargs)
        if uniq is not None:
            self.uniq = uniq

    @hybrid_property
    def uniq(self):
        """HEALPix UNIQ pixel index."""
        ipix = self.nested_range.lower
        return ipix + (1 << 2 * (level + 1))

    @uniq.setter
    def uniq(self, value):
        """HEALPix UNIQ pixel index."""
        level, ipix = uniq_to_level_ipix(value)
        level_diff = (LEVEL - level)
        lower = ipix << level_diff
        upper = (ipix + 1) << level_diff
        self.nested_range = IntInterval.closed_open(int(lower), int(upper))


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
        # FIXME: MOCpy should return a 1D array of size 0 for an empty MOC,
        # but it actually returns an array of size(1, 0). Hence ravel().
        uniqs = moc._uniq_format().ravel()
        tiles = [tile_class(uniq=uniq) for uniq in uniqs]
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
