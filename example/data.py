"""Load external sample data"""
import re
import logging
from shutil import copyfileobj
from tempfile import NamedTemporaryFile

from astropy.coordinates import SkyCoord
from astropy.table import Table
from astropy.time import Time
from astropy.utils.data import get_readable_fileobj
from astropy import units as u
from ligo.gracedb.rest import GraceDb
from mocpy import MOC
import numpy as np
from sqlalchemy import func

from . import db
from . import healpix
from .models import Localization, LocalizationTile, FieldTile, Telescope, Field

gracedb = GraceDb(force_noauth=True)

log = logging.getLogger(__name__)


def load_examples(n):
    gps_end = int(Time.now().gps)
    gps_start = gps_end - 86400
    query = f'category: MDC {gps_start} .. {gps_end}'
    log.info('querying GraceDB: "%s"', query)
    for i, s in enumerate(gracedb.superevents(query)):
        if i >= n:
            break
        gracedb_id = s['superevent_id']
        log.info('downloading sky map for %s', gracedb_id)
        with gracedb.files(gracedb_id, 'bayestar.multiorder.fits') as remote:
            with NamedTemporaryFile(mode='wb') as local:
                copyfileobj(remote, local)
                sky_map = Table.read(local.name, format='fits')
        log.info('creating ORM records')
        localization = Localization.from_sky_map(sky_map)
        log.info('saving')
        db.session.add(localization)
    log.info('committing')
    db.session.commit()
    log.info('done')


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
    with get_readable_fileobj(url, show_progress=False) as f:
        first_line, *lines = f
        names = re.split(r'\s\s+', first_line.lstrip('%').strip())
        table = Table.read(lines, format='ascii', names=names)

    log.info('building footprint polygons')
    lon, lat = get_ztf_footprint_corners()
    centers = SkyCoord(table['RA'] * u.deg, table['Dec'] * u.deg)
    vertices = get_footprints_grid(lon, lat, centers)

    log.info('building MOCs')
    mocs = [MOC.from_polygon_skycoord(verts) for verts in vertices]

    log.info('creating ORM records')
    telescope = Telescope(
        telescope_name='ZTF',
        fields=[Field.from_moc(moc, field_id=field_id)
                for field_id, moc in zip(table['ID'], mocs)]
    )
    log.info('saving')
    db.session.add(telescope)
    db.session.commit()
    log.info('done')


def top_10_fields_by_prob():
    area = healpix.area(LocalizationTile.nested_range * FieldTile.nested_range)
    prob = func.sum(LocalizationTile.probdensity * area).label('probability')

    query = db.session.query(
        prob,
        LocalizationTile.localization_id,
        FieldTile.field_id
    ).join(
        FieldTile,
        LocalizationTile.nested_range.overlaps(FieldTile.nested_range)
    ).group_by(
        LocalizationTile.localization_id, FieldTile.field_id
    ).order_by(
        prob.desc()
    ).limit(
        10
    )

    return query.all()