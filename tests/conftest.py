"""
    Fixture Setup
"""

import pdb
import json
import jmespath
from datetime import datetime, timedelta

import pandas as pd
import pytest
from betamax import Betamax
from betamax_serializers import pretty_json

from config import base_dir
from pathlib import WindowsPath

from app import db, shocal
from app.models import Artist, Concert, Track
from app.pipeline import data_collection, spotify_adapter

# Setup Cassette configuration
Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
with Betamax.configure() as config:
    config.cassette_library_dir = 'tests/fixtures/cassettes'
    config.default_cassette_options['serialize_with'] = 'prettyjson'
    config.default_cassette_options['record'] = 'new_episodes'

# Database fixtures
@pytest.fixture()
def memory_db():
    shocal.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()


@pytest.fixture
def concert_tbl(memory_db):
    """
        Create concert table.
    """

    n = 100
    today = datetime.today()
    memory_db.session.bulk_insert_mappings(
        Concert,
        [
            dict(
                artist_name=f'name_{i}',
                show_date=today + timedelta(days=i),
                show_location=f'venue_{i}',
                show_info=f'info_{i}'
            ) for i in range(n)
        ],
    )
    memory_db.session.commit()
    return memory_db


@pytest.fixture
def artist_tbl(memory_db):
    """
        Create Concert table.
    """

    n = 100
    memory_db.session.bulk_insert_mappings(
        Artist,
        [
            dict(
                spotify_id=f'id_{i}',
                artist_name=f'artist_name_ar{i}',
                followers=i
            ) for i in range(n)
        ],
    )
    memory_db.session.commit()
    return memory_db


@pytest.fixture
def track_tbl(memory_db):
    """
        Create Track table.
    """

    n = 100
    memory_db.session.bulk_insert_mappings(
        Track,
        [
            dict(
                track_id=f'spotify_id_{i}',
                track_name=f'track_name_{i}',
                artist_id=f'{i}'
            ) for i in range(n)
        ],
    )
    memory_db.session.commit()
    return memory_db

# Data Collection Fixtures


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
def spotify_response():

    path = WindowsPath(base_dir)

    with open(path / r'tests\fixtures\spotify_artists.json', 'r') as f:
        artist_response = json.load(f)

    with open(path / r'tests\fixtures\spotify_track_ids.json', 'r') as f:
        track_response = json.load(f)

    response = {}
    response['artist'] = artist_response
    response['track'] = track_response

    return response


@pytest.fixture
def spotify_data(spotify_response):

    response = spotify_response
    track_info = jmespath.search(
        "[].tracks[*].{track_id: id, track_name: name}", response['track'])

    artist_info = jmespath.search(
        "[].artists.items[].{artist_name: name, spotify_id: id,"
        "popularity: popularity, followers: followers.total}", response['artist'])

    data = {}
    data['artist'] = artist_info
    data['track'] = track_info

    return data

# def artist_data(spotify_artist_response, spotify_track_response):
# @pytest.fixture
# def artist_mgr(spotify, spotify_artist_response, spotify_track_response):
#     """
#         Set fixture attributes to cached Spotify Query responses.
#     """

#     artist_mgr = spotify_adapter.SpotifyArtistManager(spotify=spotify)
#     artist_mgr.spotify_artists = spotify_artist_response
#     artist_mgr.spotify_track_ids = spotify_track_response

#     return artist_mgr


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
