"""
    Model/Schema Definitions
"""

from datetime import datetime

from app import db

# Association Table
artist_concert = db.Table('artist_concert',
                          db.Column('concert_id', db.ForeignKey('concert.id')),
                          db.Column('artist_id', db.ForeignKey('artist.id'))
                          )

class Concert(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    artist_name = db.Column(db.String(20), nullable=False, unique=True)
    show_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    show_location = db.Column(db.String(20))
    show_info = db.Column(db.String(20))
    artists = db.relationship(
        'Artist', secondary=artist_concert,
        primaryjoin=(artist_concert.c.concert_id == id),
        secondaryjoin=(artist_concert.c.artist_id == id),
        backref=db.backref('artist_concert', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return f'<Concert {self.show_location} on {self.show_date}>'

class Artist(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    artist_name = db.Column(db.String(20))
    spotify_id = db.Column(db.String(25), unique=True)
    popularity = db.Column(db.Integer)
    followers = db.Column(db.Integer)
    concerts = db.relationship('Concert',
                               secondary=artist_concert,
                               backref=db.backref('artist_concert', lazy='dynamic'), lazy='dynamic')

    # tracks = db.relationship('Track', back_populates='artist')
    tracks = db.relationship('Track', backref='artist', lazy='dynamic')


    def __repr__(self):
        return f'<Artist {self.artist_name}>'

class Track(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    track_id = db.Column(db.String, unique=True)
    track_name = db.Column(db.String, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))

    def __repr__(self):
        return f'<Track {self.track_name}>'
