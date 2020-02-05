"""Provide default table names for declarative SQLAlchemy models."""
from inflection import underscore
from sqlalchemy.ext.declarative import declared_attr


class AutoTableName:

    @declared_attr
    def __tablename__(cls):
        """Add default table name."""
        return underscore(cls.__name__)
