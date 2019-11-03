from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from sqlalchemy.ext.declarative import declared_attr

from .flask import app
from .utils import numpy_adapters
from .healpix import Region, Tile

db = SQLAlchemy(app)


class Localization(db.Model):

    localization_id = db.Column(
        db.Integer,
        primary_key=True)

    tiles = db.relationship(
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


class LocalizationTile(Tile, db.Model):

    localization_id = db.Column(
        db.Integer,
        db.ForeignKey(Localization.localization_id),
        primary_key=True)

    probdensity = db.Column(
        DOUBLE_PRECISION,
        nullable=False)


class Telescope(db.Model):

    telescope_name = db.Column(
        db.Unicode,
        primary_key=True)

    fields = db.relationship(
        'Field',
        backref='telescope')


class Field(Region, db.Model):

    tile_class = lambda: FieldTile

    telescope_name = db.Column(
        db.Unicode,
        db.ForeignKey(Telescope.telescope_name),
        primary_key=True)

    field_id = db.Column(
        db.Integer,
        primary_key=True)


class FieldTile(Tile, db.Model):

    @declared_attr
    def __table_args__(cls):
        return (
            *super().__table_args__,
            db.ForeignKeyConstraint(
                ['telescope_name',
                 'field_id'],
                ['field.telescope_name',
                 'field.field_id'],
            )
        )

    telescope_name = db.Column(
        db.Unicode,
        db.ForeignKey(Telescope.telescope_name),
        primary_key=True)

    field_id = db.Column(
        db.Integer,
        primary_key=True)
