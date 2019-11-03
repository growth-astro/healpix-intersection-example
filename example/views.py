from flask import flash, redirect, render_template, url_for

from .flask import app
from . import admin
from . import healpix
from .models import db, LocalizationTile, FieldTile


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create_all', methods=['POST'])
def create_all():
    admin.create_all()
    flash('Initialized database.', 'success')
    return redirect(url_for('index'))


@app.route('/load_examples', methods=['POST'])
def load_examples():
    n = 5
    admin.load_examples(n)
    flash(f'Loaded some recent mock events', 'success')
    return redirect(url_for('index'))


@app.route('/load_ztf', methods=['POST'])
def load_ztf():
    admin.load_ztf()
    flash(f'Loaded ZTF fields', 'success')
    return redirect(url_for('index'))


@app.route('/example_queries', methods=['POST'])
def example_queries():
    area = healpix.area(LocalizationTile.nested_range * FieldTile.nested_range)
    prob = LocalizationTile.probdensity * area

    query = db.session.query(
        db.func.sum(prob),
        LocalizationTile
    ).join(
        FieldTile,
        LocalizationTile.nested_range.overlaps(FieldTile.nested_range)
    ).group_by(
        LocalizationTile.localization_id
    )

    flash(str(query), 'success')
    # flash(query.one(), 'success')
    return redirect(url_for('index'))
