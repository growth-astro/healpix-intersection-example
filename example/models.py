from astropy_healpix import uniq_to_level_ipix
from flask_sqlalchemy import SQLAlchemy
import numpy as np
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from sqlalchemy_utils.types.range import Int8RangeType

from .flask import app
from .utils import numpy_adapters

db = SQLAlchemy(app)

LEVEL = 29


class Localization(db.Model):

    localization_id = db.Column(
        db.Integer,
        primary_key=True)

    tiles = db.relationship(
        'LocalizationTile',
        backref='localization')

    @classmethod
    def from_multiresolution(cls, sky_map):
        level, ipix = uniq_to_level_ipix(sky_map['UNIQ'])
        factor = 1 << (LEVEL - level)
        ipix_lo = ipix * factor
        ipix_hi = (ipix + 1) * factor
        return cls(tiles=[
            LocalizationTile(pixels=(lo, hi), probdensity=p)
            for lo, hi, p in zip(ipix_lo, ipix_hi, sky_map['PROBDENSITY'])
        ])


class LocalizationTile(db.Model):

    localization_id = db.Column(
        db.Integer,
        db.ForeignKey(Localization.localization_id),
        primary_key=True)

    pixels = db.Column(
        Int8RangeType,
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


class Field(db.Model):

    telescope_name = db.Column(
        db.Unicode,
        db.ForeignKey(Telescope.telescope_name),
        primary_key=True)

    field_id = db.Column(
        db.Integer,
        primary_key=True)

    tiles = db.relationship(
        'FieldTile',
        backref='field')


class FieldTile(db.Model):

    __table_args__ = (
        db.ForeignKeyConstraint(
            ['telescope_name',
             'field_id'],
            ['field.telescope_name',
             'field.field_id'],
        ),
    )

    telescope_name = db.Column(
        db.Unicode,
        db.ForeignKey(Telescope.telescope_name),
        primary_key=True)

    field_id = db.Column(
        db.Integer,
        primary_key=True)

    pixels = db.Column(
        Int8RangeType,
        primary_key=True)
