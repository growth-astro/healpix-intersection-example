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
        db.Sequence('localization_id_seq'),
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


class Field(db.Model):

    field_id = db.Column(
        db.Integer,
        db.Sequence('field_id_seq'),
        primary_key=True)

    tiles = db.relationship(
        'FieldTile',
        backref='field')


class FieldTile(db.Model):

    field_id = db.Column(
        db.Integer,
        db.ForeignKey(Field.field_id),
        primary_key=True)

    pixels = db.Column(
        Int8RangeType,
        primary_key=True)
