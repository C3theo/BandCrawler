"""
    Artist Catalog tests.
"""

import pdb

def test_catalog_tbl_ins(memory_db):

    func = memory_db.func
    distinct = memory_db.distinct
    unique = memory_db.session.query(func.count(distinct(Catalog.artist_name))).scalar()
    assert unique == 200
    
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

    mocker.patch.object(spotify_adapter.SpotipyAdapter, 'get_artist_info', return_value='Artist Info')
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
    
    pd.testing.assert_frame_equal(concert_mgr.concerts_df, catalog_observer.concerts_df)
    assert concert_mgr.create_weekly_schedule.call_count == 1
    assert catalog_observer.update_catalog.call_count == 1
    assert playlist_observer.update_playlist.call_count == 1
    assert len(playlist_observer.artists) >= 1
    assert catalog_observer.catalog_df == "Artist Info"


def test_web_scraper(athens_scraper):
    concert_dict = athens_scraper.get_concerts()
    assert concert_dict is not None
