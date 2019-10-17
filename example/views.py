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
