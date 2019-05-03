"""
    Fixtures
"""

from app import shocal, db
from app.models import Catalog, Concert
from app.pipeline import data_collection, spotify_adapter
from datetime import date, timedelta
import pytest
import json
from betamax import Betamax
from betamax_serializers import pretty_json

import pandas as pd

# Setup Cassette configuration
Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
with Betamax.configure() as config:
    config.cassette_library_dir = 'tests/fixtures/cassettes'
    config.default_cassette_options['serialize_with'] = 'prettyjson'
    config.default_cassette_options['record'] = 'new_episodes'

@pytest.mark.usefixtures('betamax_session')
@pytest.fixture
def athens_scraper(betamax_session):
    scraper = data_collection.Scraper(session=betamax_session)
    scraper.get_response()
    return scraper

@pytest.fixture
def spotify(betamax_session):
    sp_adaptr = spotify_adapter.SpotipyAdapter(session=betamax_session)
    return sp_adaptr.authenticate_user()

@pytest.fixture
def spotify_artist_response():
    with open('spotify_artists.json', 'r') as f:
        response = json.load(f)
    return response

@pytest.fixture
def spotify_track_response():
    with open('spotify_track_ids.json', 'r') as f:
        response = json.load(f)
    return response

@pytest.fixture
def artist_mgr(spotify, spotify_artist_response, spotify_track_response):
    """
        Set fixture attributes to cached Spotify Query responses.
    """

    artist_mgr = spotify_adapter.SpotifyArtistManager(spotify=spotify)
    artist_mgr.spotify_artists = spotify_artist_response
    artist_mgr.spotify_track_ids = spotify_track_response
    
    return artist_mgr

@pytest.fixture
def concert_mgr(athens_scraper):
    concert_dict = athens_scraper.get_concerts()
    return data_collection.ConcertManager(concerts=concert_dict)

@pytest.fixture
def catalog_observer(concert_mgr):
    return data_collection.Catalog(concert_manager=concert_mgr)


@pytest.fixture
def playlist_observer(concert_mgr):
    return data_collection.Playlist(concert_manager=concert_mgr)


@pytest.fixture
def spotify_playlist_mgr(spotify):
    playlist_mgr = spotify_adapter.SpotifyPlaylistManager(spotify=spotify)
    return playlist_mgr

@pytest.fixture
def memory_db():
    shocal.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()

@pytest.fixture
def catalog(memory_db):
    # add 200 records
    n=200
    memory_db.session.bulk_insert_mappings(
        Catalog,
        [
            dict(
                spotify_id=f'id_{i}',
                artist_name=f'name_{i}',
                followers=i,
                artist_track_ids=f'track_ids_{i}'
            ) for i in range(n)
        ],
    )
    memory_db.session.commit()
    return memory_db