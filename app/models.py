"""
    Model/Schema Definitions
"""

from app import db

class Concert(db.Model):
    __tablename__ = 'concerts'
    
    id = db.Column(db.Integer, primary_key=True)
    artist_name = db.Column(db.String(20), nullable=False, unique=True) 
    show_date = db.Column(db.String(20)) 
    show_location = db.Column(db.String(20)) 
    show_info = db.Column(db.String(20))

    def __repr__(self):
        return f'<Concert {self.show_location}>'
    
class Catalog(db.Model):
    __tablename__ = 'catalog'
    
    id = db.Column(db.Integer, primary_key=True)
    spotify_id = db.Column(db.String(25), unique=True)
    artist_name = db.Column(db.String(20)) 
    followers = db.Column(db.Integer) 
#     genres = db.Column(db.String(20)) 
    artist_track_ids = db.Column(db.String)
    def __repr__(self):
        return f'<Catalog {self.artist_name}>'
    
    
# Later
# class Track_Catalog(db.Model):
#     __tablename__ = 'track_catalog'
    
#     artist_track_ids = db.Column(db.String(20)
#     spotify_id = db.Column(db.Integer, primary_key=True)
#     artist_name = db.Column(db.String(20), nullable=False) 
#     followers = db.Column(db.String(20), nullable=False) 
#     genres = db.Column(db.String(20)) 
#     artist_track_ids = db.Column(db.String(20))
#     def __repr__(self):
#         return f'<Concert {self.show_location}>'




