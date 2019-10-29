from astropy.table import Table
from astropy.time import Time
from ligo.gracedb.rest import GraceDb

from shutil import copyfileobj
from tempfile import NamedTemporaryFile

from .models import db, Localization

gracedb = GraceDb(force_noauth=True)


def create_all():
    db.reflect()
    db.drop_all()
    db.session.commit()
    db.create_all()


def load_examples(n):
    gps_end = int(Time.now().gps)
    gps_start = gps_end - 7200
    query = f'category: MDC {gps_start} .. {gps_end}'
    for s in gracedb.superevents(query):
        gracedb_id = s['superevent_id']
        with gracedb.files(gracedb_id, 'bayestar.multiorder.fits') as remote:
            with NamedTemporaryFile(mode='wb') as local:
                copyfileobj(remote, local)
                sky_map = Table.read(local.name, format='fits')
                db.session.merge(Localization.from_multiresolution(sky_map))
                db.session.commit()
