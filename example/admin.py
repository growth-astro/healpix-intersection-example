import logging
import re
from shutil import copyfileobj
from tempfile import NamedTemporaryFile

from astropy.coordinates import SkyCoord
from astropy.table import Table
from astropy.time import Time
from astropy.utils.data import get_readable_fileobj
from astropy import units as u
from ligo.gracedb.rest import GraceDb
import numpy as np

from .models import db, Localization, Telescope, Field

gracedb = GraceDb(force_noauth=True)

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)


def create_all():
    db.reflect()
    db.drop_all()
    db.session.commit()
    db.create_all()


def load_examples(n):
    gps_end = int(Time.now().gps)
    gps_start = gps_end - 7200
    query = f'category: MDC {gps_start} .. {gps_end}'
    log.info('querying GraceDB: "%s"', query)
    for s in gracedb.superevents(query):
        gracedb_id = s['superevent_id']
        log.info('downloading sky map for %s', gracedb_id)
        with gracedb.files(gracedb_id, 'bayestar.multiorder.fits') as remote:
            with NamedTemporaryFile(mode='wb') as local:
                copyfileobj(remote, local)
                sky_map = Table.read(local.name, format='fits')
        log.info('creating ORM records')
        db.session.merge(Localization.from_sky_map(sky_map))
        log.info('committing')
        db.session.commit()
        log.info('done')
        break


def get_ztf_footprint_corners():
    """Return the corner offsets of the ZTF footprint."""
    x = 6.86 / 2
    return [-x, +x, +x, -x] * u.deg, [-x, -x, +x, +x] * u.deg


def get_footprints_grid(lon, lat, offsets):
    """Get a grid of footprints for an equatorial-mount telescope.

    Parameters
    ----------
    lon : astropy.units.Quantity
        Longitudes of footprint vertices at the standard pointing.
        Should be an array of length N.
    lat : astropy.units.Quantity
        Latitudes of footprint vertices at the standard pointing.
        Should be an array of length N.
    offsets : astropy.coordinates.SkyCoord
        Pointings for the field grid.
        Should have length M.

    Returns
    -------
    astropy.coordinates.SkyCoord
        Footprints with dimensions (M, N).
    """
    lon = np.repeat(lon[np.newaxis, :], len(offsets), axis=0)
    lat = np.repeat(lat[np.newaxis, :], len(offsets), axis=0)
    return SkyCoord(lon, lat, frame=offsets[:, np.newaxis].skyoffset_frame())


def load_ztf():
    log.info('downloading and reading ZTF field list')
    url = 'https://github.com/ZwickyTransientFacility/ztf_information/raw/master/field_grid/ZTF_Fields.txt'
    with get_readable_fileobj(url) as f:
        first_line, *lines = f
        names = re.split(r'\s\s+', first_line.lstrip('%').strip())
        table = Table.read(lines, format='ascii', names=names)

    # FIXME: this is really slow, so just take the first 100 fields for now
    n = 100
    table = table[:100]
    log.info('taking only first %d fields for speed', n)

    log.info('building footprint polygons')
    lon, lat = get_ztf_footprint_corners()
    centers = SkyCoord(table['RA'] * u.deg, table['Dec'] * u.deg)
    vertices = get_footprints_grid(lon, lat, centers)

    log.info('creating ORM records')
    db.session.merge(
        Telescope(
            telescope_name='ZTF',
            fields=[Field.from_polygon(verts, field_id=field_id)
                    for field_id, verts in zip(table['ID'], vertices)]
        )
    )
    log.info('committing')
    db.session.commit()
    log.info('done')
