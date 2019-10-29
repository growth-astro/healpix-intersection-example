from flask import flash, redirect, render_template, url_for

from .flask import app
from . import admin


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
