from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql

from .flask import app

db = SQLAlchemy(app)


class Localization(db.Model):

    localization_id = db.Column(
        db.Integer,
        db.Sequence('localization_id_seq'),
        primary_key=True)

    tiles = db.relationship(
        'LocalizationTile',
        backref='localization')


class LocalizationTile(db.Model):

    localization_id = db.Column(
        db.Integer,
        db.ForeignKey(Localization.localization_id),
        primary_key=True)

    pixels = db.Column(
        postgresql.INT8RANGE,
        primary_key=True)

    probdensity = db.Column(
        postgresql.DOUBLE_PRECISION,
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
        postgresql.INT8RANGE,
        primary_key=True)
