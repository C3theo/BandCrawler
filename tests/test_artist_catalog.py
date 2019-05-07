"""
    Artist Catalog tests.
"""

import pdb

import jmespath
import pandas as pd
import pytest

from app.models import Artist, Concert, Track
from app.pipeline import data_collection, spotify_adapter
from app.pipeline.data_collection import Catalog


class TestDatabase(object):

    def test_artist_tbl_ins(self, artist_tbl):

        func = artist_tbl.func
        distinct = artist_tbl.distinct
        unique = artist_tbl.session.query(
            func.count(distinct(Artist.artist_name))).scalar()
        assert unique == 100

    def test_track_tbl_ins(self, track_tbl):

        func = track_tbl.func
        distinct = track_tbl.distinct
        unique = track_tbl.session.query(
            func.count(distinct(Track.track_name))).scalar()
        assert unique == 100

    def test_concert_tbl_ins(self, memory_db, concert_tbl):

        func = concert_tbl.func
        distinct = concert_tbl.distinct
        unique = concert_tbl.session.query(
            func.count(distinct(Concert.artist_name))).scalar()
        assert unique == 100

    def test_artist_track_relationship(self, memory_db):

        artist_1 = Artist(spotify_id='artist_spotify_id_1',
                          artist_name='artist_name_1',
                          followers=11)

        artist_2 = Artist(spotify_id='artist_spotify_id_2',
                          artist_name='artist_name_2',
                          followers=22)

        memory_db.session.add_all([artist_1, artist_2])
        memory_db.session.commit()

        track_1 = Track(track_id='spotify_id_1',
                        track_name='track_1',
                        artist_id=1)

        track_2 = Track(track_id='spotify_id_2',
                        track_name='track_2',
                        artist_id=1)

        track_3 = Track(track_id='spotify_id_3',
                        track_name='track_3',
                        artist_id=2)

        memory_db.session.add_all([track_1, track_2, track_3])
        memory_db.session.commit()

        assert track_1.artist == artist_1
        assert track_2.artist == artist_1
        assert track_3.artist == artist_2

    def test_catalog_load(self, memory_db, mocker, spotify_data):
        """
            Test Catalog load records method
        """

        data = spotify_data

        # mocking spotify singleton object with correct spec
        class TestSpotipyAdapter(spotify_adapter.SpotipyAdapter):
            artist_data = data['artist']
            track_data = data['track']

        # patch spotify singleton
        mocker.patch('app.pipeline.data_collection.spotify',
                     artist_data=data['artist'], track_data=data['track'],
                     autospec=TestSpotipyAdapter)

        # patch entire db with memory_db fixture at import

        def create_db():
            return memory_db
        mock_db = mocker.patch(
            'app.pipeline.data_collection.db', new_callable=create_db)
        c = Catalog()
        triage = c.load_records()

        query = mock_db.session.query(Artist.id).all()

        assert len(triage) == 0
        assert len(query) > 0


# def test_spotify_adapter(spotify_response):

#     response = spotify_response

#     mocker.patch('app.pipeline.spotfy_adapter.SpotifyArtistManager',
#                 get_artist_info,
#                 return_value=response['artist'])

#     mocker.patch('app.pipeline.spotfy_adapter.SpotifyArtistManager',
#                 get_track_info,
#                 return_value=response['track'])


def test_spotify(spotify):
    assert isinstance(spotify, spotify_adapter.spotipy.Spotify)


def test_spotify_playlist_id(spotify_playlist_mgr):
    print(f'PlaylistID: {spotify_playlist_mgr.playlist_id}')
    spotify_playlist_mgr.get_playlist_id()
    assert spotify_playlist_mgr.playlist_id == '4uZwzDvVcuiZW6DIWvC8O1'


def test_create_weekly_schedule(concert_mgr):
    print(f"Concerts: {concert_mgr.weekly_artists}")
    concert_mgr.create_weekly_schedule()
    print(f"Concerts: {concert_mgr.weekly_artists}")

    assert len(concert_mgr.weekly_artists) > 0


# functiional observer test
def test_update_observers(mocker, concert_mgr, catalog_observer,
                          playlist_observer, spotify_artist_response, spotify_track_response, memory_db):
    """
        Testing Interactions between Concert Manager and two observers - Playlist and Catalog.
    """

    mocker.patch.object(spotify_adapter.SpotipyAdapter,
                        'get_artist_info', return_value='Artist Info')
    # mocker.patch.object('app.pipeline.data_collection.db', 'engine', return_value=memory_db.engine)
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

    pd.testing.assert_frame_equal(
        concert_mgr.concerts_df, catalog_observer.concerts_df)
    assert concert_mgr.create_weekly_schedule.call_count == 1
    assert catalog_observer.update_catalog.call_count == 1
    assert playlist_observer.update_playlist.call_count == 1
    assert len(playlist_observer.artists) >= 1
    assert catalog_observer.catalog_df == "Artist Info"


def test_web_scraper(athens_scraper):
    concert_dict = athens_scraper.get_concerts()
    assert concert_dict is not None
