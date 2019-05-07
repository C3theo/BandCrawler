"""
    This modules contains classes to build playlists that are up to date
    with the schedule of touring musicians.

    Extraction:
        Artist Information

    Transformation:
        Spotify Artist Table

    Loading
        Pandas -> SQL

    Sources:
        Spotify API


"""

# TODO:
# user_playlist_reorder_tracks()
# currently_playing(market=None)
# user_playlist_is_following

import json
import os
import pdb
import time
from pathlib import WindowsPath

import jmespath
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from app import db, logger
from app.models import Artist, Track
from config import base_dir, load_dotenv

load_dotenv(dotenv_path=base_dir)

# TODO: create spotify singleton/ Module Variable
# issue with circular imports/where spotify object created

class SpotipyAdapter():
    """
        Adapter to spotipy library.
    """

    def __init__(self, session=None):
        
        self.session = session
        self.spotify = None
        self.artist_data = None
        self.track_data = None

    def authenticate_user(self):

        auth_mgr = SpotifyAuthManager(session=self.session)
        auth_mgr.create_client_mgr().get_auth_token()
        self.spotify = auth_mgr.create_spotify()

        return self

    def update_playlist(self):
        return self

    def get_catalog_data(self, artists=None):
        """
            Create Artist ad Track DataFrames.
        """

    
        artist_mgr = SpotifyArtistManager(spotify=self.spotify, artists=artists)

        artist_mgr.get_artist_info()
        artist_mgr.get_track_info()
        artist_mgr.save_artist_json()
        artist_mgr.prepare_data()

        self.artist_data = artist_mgr.artist_info
        self.track_data = artist_mgr.track_info

        return self

# TODO:
# need to add try except to refresh tokens
# make class singleton
class SpotifyAuthManager():
    """
        A class used to handle Spotify Oauth.
        Refreshable user authentication.

        Owned by Playlist & ArtistManager.

        Args:

        Instance Attributes

        Class Attributes:

    """

    username = os.environ['SPOTIFY_USERNAME']
    client_id = os.environ['SPOTIFY_CLIENT_ID']
    client_secret = os.environ['SPOTIFY_CLIENT_SECRET']
    scope = os.environ['SPOTIFY_SCOPE']
    redirect_uri = os.environ['SPOTIFY_REDIRECT_URI']

    def __init__(self, session=None):

        self.token_info = None
        self.response_code = None
        self.client_mgr = None

        self.session = session
        # use same session
        # self.session = session

    def create_client_mgr(self):
        """
        Create SpotifyOauth object.

        Args:
            client_id
            client_secret
            redirect_uri
            scope
            cache_path

        """

        cache_path = WindowsPath("__pycache__") / fr'.cache-{self.username}'
        self.client_mgr = SpotifyOAuth(self.client_id, self.client_secret,
                                       self.redirect_uri, scope=self.scope,
                                       cache_path=cache_path)
        return self

    def get_auth_token(self):
        """
        Get oauth token from cache or prompt for new token.
        """

        try:
            self.token_info = self.client_mgr.get_cached_token()
            logger.info(
                f"Token expires at {time.strftime('%c', time.localtime(self.token_info['expires_at']))}")
            return self
        # TODO: add specific exceptions
        except Exception:
            logger.info("No token in cache. Getting new token.", exc_info=True)
            auth_url = self.client_mgr.get_authorize_url()
            user_auth = self.session.get(auth_url).url
            response_code = input(f'Use Browser to authenticate: {user_auth}')
            code = self.client_mgr.parse_response_code(response_code)
            self.token_info = self.client_mgr.get_access_token(code)

            with open(self.client_mgr.cache_path, 'w') as f:
                f.write(json.dumps(self.token_info))

    def refresh_auth_token(self):
        """
            Refresh authentication token.

            Same spotify obect used throughout. How to call from owning classes.
        """

        self.client_mgr.refresh_access_token(self.token_info['refresh_token'])
        logger.info(
            f"Token refreshed, expires at: {time.strftime('%c', time.localtime(self.token_info['expires_at']))}")

    def create_spotify(self):
        """
        Create Spotify object for Authorization Code flow.

        Args: token, session, client_mgr
        """

        try:
            auth_info = {'auth': self.token_info['access_token'], 'requests_session': self.session,
                         'client_credentials_manager': self.client_mgr}
            return catch(spotipy.Spotify, auth_info)
        except TypeError:
            # Why TypeError?
            logger.error("Token error.", exc_info=True)


class SpotifyPlaylistManager():
    """
        Class to get User Playlist information.
        ID
        Artists in playlist
        Followers
    """

    def __init__(self, playlist_name='test', spotify=None):

        self.playlist_id = None
        self.spotify = spotify
        self.playlist_name = playlist_name

        self.spotify_dict = None

    def get_playlist_id(self):
        """
        Return uri of specified user playlists.
        """

        self.playlist_id = jmespath.search(f"items[?name=='{self.playlist_name}'].id",
                                           self.spotify.current_user_playlists())[0]

    def get_playlist_artists(self):
        """
            Return list of artists in playlists.
        """
        pass

    def get_playlist_tracks(self):
        """
        """
        # Get full details of the tracks of a playlist owned by a user
        self.spotify.user_playlist_tracks()

    def add_tracks(self, uris):
        """
        Add tracks to playlist matchig ply_id attribute.

        Args: uris
        """
        pass

        # self.spotify.user_playlist_add_tracks(self.username, self.ply_id, uris)

    def clear_playlist(self, spotify, user, playlist_id=None):
        """ Remove all tracks from playlist. """

        playlist_tracks = spotify.user_playlist_tracks(user, playlist_id)
        spotify.user_playlist_remove_all_occurrences_of_tracks(
            user, playlist_id, playlist_tracks, snapshot_id=None)

    def update_playlist(self):
        """
        Update spotify playlist. Once per week.
        """
        pass
        # self.clear_playlist()
        # self.add_tracks()


class SpotifyArtistManager():
    """
        Class for getting artist info from Spotify API.

    """

    def __init__(self, spotify=None, artists=None):

        self.spotify = spotify
        self.artists = artists

        self.artist_response = None
        self.track_response = None

    def find_artist_info(self, query=None, item_type=None):
        """
            Query Spotify Search endpoint.
        """

        kwargs = {'q': f'{item_type}: {query}', 'type': item_type}
        result = self.spotify.search(**kwargs)
        result = result if result is not None else None

        return result

    def get_artist_info(self):
        """
            Set spotify_artists attribute to list of filtered artist json objects returned from
            Spotify API query. List of dicts that are used to load into catalog dataframe.

        """

        artists = self.artists
        results = []

        for each in artists:
            # logger.info(
            #     'Queried Spotify API Artist Endpoint for: %s\n\n', each)
            result = self.find_artist_info(query=each, item_type='artist')
            if jmespath.search("artists.items", result):
                # TODO: fix this log to only return artist names
                # logger.info('Spotify API Artist Endpoint returned:\n\n %s',
                #             jmespath.search("artists.items", result))
                results.append(result)

            else:
                continue

        self.artist_response = results

    def get_track_info(self):
        """
            Return uris of all the artists top ten tracks.
        """

        # get all artist ids
        artist_ids = jmespath.search(
            "[].artists.items[].id", self.artist_response)
        results = [self.spotify.artist_top_tracks(each) for each in artist_ids]

        self.track_response = results

    def save_artist_json(self):
        """
            Save artist json objects to file for logging/testing.
        """

        fixture_path = WindowsPath(base_dir / r'test/fixtures')
        with open(fixture_path / 'spotify_artists.json', 'w') as f:
            json.dump(self.artist_response, f)

        with open(fixture_path / 'spotify_track_ids.json', 'w') as f:
            json.dump(self.track_response, f)

    def format_artist_info(self):
        """
            Format Artist responses into list of dicts for Dataframe.
        """

       # Artist ID
        data = jmespath.search(
            "[].artists.items[].{artist_name: name, genres: genres, spotify_id: id,"
            "popularity: popularity, followers: followers.total}", self.artist_response)

        return data

    def format_track_info(self):
        """
            Format Track responses into list of dicts for DataFrame.
        """

        # TrackID
        data = jmespath.search(
            "[].tracks[*].{track_id: id, track_name: name}", self.track_response)

        return data

    def prepare_data(self):
        """
            Creates list of dicts to load into DataFrame.
            Add artist ID to track dicts for Foreign Key.
        """

        self.artist_info = self.format_artist_info()

        track_info = self.format_track_info()
        if len(self.artist_info) != len(track_info):
            raise AssertionError('Spotify Query Error')
        else:
            # add artist id to dict to create foreign key
            for i, each in enumerate(track_info):
                for track in each:
                    track['artist_id'] = self.artist_info[i]['artist_id']

        self.track_info = [j for i in track_info for j in i]

    def check_artist_names(self, df):
        """
            Check if Artist name returned from Spotify Query matches up with name scraped from
            web.
        """

        artists = self.artists
        # compare artist columns between two df's. drop all that don't match
        df = df.loc[df['artist_name'].str.lower().isin(artists), :]
        df.loc[:, 'artist_name'] = df.loc[:, 'artist_name'].str.lower()

        return df

    @staticmethod
    def drop_dup_artists(df):
        """
            Keep Duplicate artist name returned from Spotify query that has most followers.
        """

        # sort by followers
        df.sort_values(by=['followers'], ascending=False, inplace=True)
        # Keep duplicate artist with most followers
        df.drop_duplicates(subset='artist_name', inplace=True)
        return df



def load_data(data):
    """
        Create Dataframe from prepared list of dicts
    """

    df = pd.DataFrame(data)
    return df

# class decorator refresh token
# def refresh_token(func, kwargs):
    # wrap all methods
    # if spotify token is old, get new one fore existing object

    # try:
    #     # spotify.method() with existing token
    # except:
    #     spotify.refresh_token()
    # try:
    #     # try to run method.
    #     pdb.set_trace()
    #     func(**kwargs)
    # except SpotifyException:
    #     obj.spotify.refresh_auth_token()


def catch(func, kwargs):
    """
    Helper function for logging unknown exceptions.
    """

    try:
        return func(**kwargs)
    except Exception:
        logger.exception('Exception occured', exc_info=True)
        raise

#   def spotify_stage_df():
#         """
#             Create staging df from artist responses in cache.
#         """
#         # TODO: add absolute path to saved json
#         # move to testing
#         df = pd.read_json('spotify_artists.json', orient='records')
#         df.rename(axis=1, mapper={
#                   'artists': 'spotify_responses'}, inplace=True)
#         return df


# Tested Workflow in Jupyter notebook
# TODO: Need way to refresh token

# session = data_collection.start_session()
# athens_scraper = data_collection.Scraper(session=session)
# athens_scraper.get_response()
# concerts = athens_scraper.get_concerts()

# # Original Data scraped from website
# stage_df = pd.DataFrame(data=concerts['concerts'])
# artists = [j.lower() for i in stage_df['show_artists'].tolist() for j in i]

# # Spotify API Auth
# spotify_mgr = SpotifyAuthManager(session=session)
# spotify_mgr.create_client_mgr()
# spotify_mgr.get_auth_token()
# spotify = spotify_mgr.create_spotify()

# # Get User playlist info
# play_mgr = SpotifyPlaylistManager(playlist_name='test', spotify=spotify)
# play_mgr.get_playlist_id()

# play_mgr.playlist_id
# # test playlist_id ='4uZwzDvVcuiZW6DIWvC8O1'

# # Get Artist Info
# artist_mgr = SpotifyArtistManager(spotify=spotify, artists=artists )

# # use cached spotify responses
# with open('spotify_artists.json', 'r') as f:
#     spotify_artists = json.load(f)
# artist_mgr.spotify_artists = spotify_artists

# #Create spotify_df / Catalog
# data = artist_mgr.format_artist_data()
# spotify_df = pd.DataFrame(data)

# # add trackids to catalog
# artist_ids = spotify_df['spotify_id'].tolist()
# track_response = []
# for each in spotify_df['spotify_id'].values:
#     track_response.append(artist_mgr.spotify.artist_top_tracks(each))
# artist_track_ids = jmespath.search('[].tracks[*].id', test_track_response)
# spotify_df['artist_track_ids'] = artist_track_ids

# # throw out empty artist_track_ids
# catalog_df = spotify_df[spotify_df['artist_track_ids'].apply(len) > 0].copy()

# #compare artist columns between two df's. drop all that don't match
# load_df = spotify_df.loc[spotify_df['artist_name'].str.lower().isin(artists), :]
# load_df.loc[:, 'artist_name'] = load_df.loc[:, 'artist_name'].str.lower()
# # sort by followers
# load_df.sort_values(by=['followers'], ascending=False, inplace=True)
# # Keep duplicate artist with most followers
# load_df.drop_duplicates(subset='artist_name', inplace=True)

# # Storage Option 1: Just store list of id's in Dataframe
# pprint.pprint(jmespath.search('tracks[].id', test_trks))

# # TODO: use this later
# # Storage option 2: New table with Spotify ID as key
# pprint.pprint(jmespath.search('tracks[].{track_name: name, track_id: id}', test_trks))
