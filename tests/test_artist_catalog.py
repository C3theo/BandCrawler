"""
    Artist Catalog tests.
"""

from app.pipeline import data_collection, spotify_adapter
from datetime import date, timedelta
import pytest
import json
from betamax import Betamax
from betamax_serializers import pretty_json

import pandas as pd
import pdb

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


def test_spotify(spotify):
    assert isinstance(spotify, spotify_adapter.spotipy.Spotify)


def test_spotify_playlist_id(spotify_playlist_mgr):
    print(f'PlaylistID: {spotify_playlist_mgr.playlist_id}')
    spotify_playlist_mgr.get_playlist_id()
    assert spotify_playlist_mgr.playlist_id == '4uZwzDvVcuiZW6DIWvC8O1'


@pytest.mark.skip(reason=None)
def test_create_weekly_schedule(concert_mgr):
    print(f"Concerts: {concert_mgr.weekly_artists}")
    concert_mgr.create_weekly_schedule()
    print(f"Concerts: {concert_mgr.weekly_artists}")

    assert len(concert_mgr.weekly_artists) > 0


def test_update_observers(mocker, concert_mgr, catalog_observer,
                          playlist_observer, spotify_artist_response, spotify_track_response):
    """
        Testing Interactions between Concert Manager and two observers - Playlist and Catalog.
    """

    mocker.patch.object(spotify_adapter.SpotipyAdapter, 'get_artist_info', return_value='Artist Info')
    concert_mgr.attach(catalog_observer)
    concert_mgr.attach(playlist_observer)
    mocker.spy(concert_mgr, 'create_weekly_schedule')
    mocker.spy(catalog_observer, 'update_catalog')
    mocker.spy(playlist_observer, 'update_playlist')

    concert_mgr.create_weekly_schedule()
    print(f"Playlist Artists: {playlist_observer.artists[:10]}...\n\n")
    print(f"Concert Manger: {concert_mgr.concerts_df.info()}\n\n")
    print(f"Catalog:{catalog_observer.concerts_df.info()}\n\n")
    print(f'Catalog Dataframe: {catalog_observer.catalog_df} \n\n')
    
    pd.testing.assert_frame_equal(concert_mgr.concerts_df, catalog_observer.concerts_df)
    assert concert_mgr.create_weekly_schedule.call_count == 1
    assert catalog_observer.update_catalog.call_count == 1
    assert playlist_observer.update_playlist.call_count == 1
    assert len(playlist_observer.artists) >= 1
    assert catalog_observer.catalog_df == "Artist Info"

def test_

def test_web_scraper(athens_scraper):
    concert_dict = athens_scraper.get_concerts()
    assert concert_dict is not None
