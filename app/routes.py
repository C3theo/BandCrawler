from flask import render_template, redirect, url_for
from app import shocal

@shocal.route('/')
@shocal.route('/index')
def index():
    concerts = [
        {
            'artists': ['artist_1', 'artist_2']
        },
        {
            'artists': ['artist_3', 'artist_4']
        }
    ]
    return render_template('index.html', concerts=concerts)