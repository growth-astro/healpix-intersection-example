"""Model base classes for multiresolution HEALPix data."""
from astropy.coordinates import ICRS
from astropy import units as u
from astropy_healpix import (level_to_nside, nside_to_pixel_area,
                             uniq_to_level_ipix, HEALPix)
from mocpy import MOC
from sqlalchemy import BigInteger, Column, Index
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.sql.expression import func

LEVEL = MOC.HPY_MAX_NORDER
"""Base HEALPix resolution. This is the maximum HEALPix level that can be
stored in a signed 8-byte integer data type."""

HPX = HEALPix(nside=level_to_nside(LEVEL), order='nested', frame=ICRS())
"""HEALPix projection object."""

PIXEL_AREA = HPX.pixel_area.to_value(u.sr)
"""Native pixel area in steradians."""


class Point:
    """Mixin class for a table that stores a HEALPix multiresolution point."""

    nested = Column(
        BigInteger, index=True, nullable=False,
        comment=f'HEALPix nested index at nside=2**{LEVEL}')


class Tile:
    """Mixin class for a table that stores a HEALPix multiresolution tile."""

    nested_lo = Column(
        BigInteger, index=True, nullable=False, primary_key=True,
        comment=f'Lower end of range of HEALPix nested indices at nside=2**{LEVEL}')

    nested_hi = Column(
        BigInteger, nullable=False,
        comment=f'Upper end of range of HEALPix nested indices at nside=2**{LEVEL}')

    def __init__(self, *args, uniq=None, **kwargs):
        super().__init__(*args, **kwargs)
        if uniq is not None:
            self.uniq = uniq

    @hybrid_property
    def uniq(self):
        """HEALPix UNIQ pixel index."""
        # This is the same expression as in astropy_healpix.level_ipix_to_uniq,
        # but reproduced here so that SQLAlchemy can map it to SQL.
        ipix = self.nested_lo
        return ipix + (1 << 2 * (LEVEL + 1))  # FIXME: wrong, get level from log2(nested_hi - nested_lo)/2

    @uniq.setter
    def uniq(self, value):
        """HEALPix UNIQ pixel index."""
        level, ipix = uniq_to_level_ipix(value)
        shift = 2 * (LEVEL - level)
        self.nested_lo = ipix << shift
        self.nested_hi = ((ipix + 1) << shift) - 1


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
        if nested_ranges.size == 0:
            nested_ranges = nested_ranges.reshape(-1, 2)
        tiles = [tile_class(nested_lo=lo, nested_hi=hi)
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
