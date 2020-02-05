from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base

engine = create_engine(
    'postgresql://postgres:mysecretpassword@postgres/postgres',
    executemany_mode='values',
    executemany_values_page_size=100000)


def create_all():
    Base.metadata.create_all(engine)


Session = sessionmaker(bind=engine)
session = Session()
