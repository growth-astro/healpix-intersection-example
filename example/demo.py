import logging

logging.basicConfig(format='    %(asctime)s %(levelname)s %(message)s',
                    level=logging.INFO)

from .utils.benchmark import time
from . import db, data

log = logging.getLogger(__name__)

with time('create tables'):
    db.create_all()

with time('load ZTF fields'):
    data.load_ztf()

with time('load example LIGO sky map'):
    data.load_examples(1)

with time('loading 2MRS catalog'):
    data.load_2mrs()

with time('top 10 fields by probability'):
    data.top_10_fields_by_prob()

with time('top 10 galaxies by probability density'):
    data.top_10_galaxies_by_probdensity()
