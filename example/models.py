from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, Integer, Unicode
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy.orm import relationship

from .utils import numpy_adapters
from .utils.auto_table_name import AutoTableName
from .healpix import Point, Region, Tile


Base = declarative_base(cls=AutoTableName)


class Localization(Base):

    localization_id = Column(
        Integer,
        primary_key=True)

    tiles = relationship(
        'LocalizationTile',
        backref='localization')

    @classmethod
    def from_sky_map(cls, sky_map, *args, **kwargs):
        """Create an instance from a multiresolution sky map.

        Parameters
        ----------
        sky_map : astropy.table.Table
        """
        tiles = [
            LocalizationTile(uniq=row['UNIQ'], probdensity=row['PROBDENSITY'])
            for row in sky_map]
        return cls(*args, tiles=tiles, **kwargs)


class LocalizationTile(Tile, Base):

    localization_id = Column(
        Integer,
        ForeignKey(Localization.localization_id),
        primary_key=True)

    probdensity = Column(
        DOUBLE_PRECISION,
        nullable=False)


class Telescope(Base):

    telescope_name = Column(
        Unicode,
        primary_key=True)

    fields = relationship(
        'Field',
        backref='telescope')


class Galaxy(Point, Base):

    simbad_name = Column(
        Unicode,
        primary_key=True)


class Field(Region, Base):

    tile_class = lambda: FieldTile

    telescope_name = Column(
        Unicode,
        ForeignKey(Telescope.telescope_name),
        primary_key=True)

    field_id = Column(
        Integer,
        primary_key=True)


class FieldTile(Tile, Base):

    @declared_attr
    def __table_args__(cls):
        return (
            *super().__table_args__,
            ForeignKeyConstraint(
                ['telescope_name',
                 'field_id'],
                ['field.telescope_name',
                 'field.field_id'],
            )
        )

    telescope_name = Column(
        Unicode,
        ForeignKey(Telescope.telescope_name),
        primary_key=True)

    field_id = Column(
        Integer,
        primary_key=True)
