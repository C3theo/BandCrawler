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
import os
import pdb
# TODO: Refactor out time and just use datetime
import time
from pathlib import WindowsPath
import jmespath

import spotipy
from spotipy.oauth2 import SpotifyOAuth

# pdb.set_trace()
from .concert_etl import DataManager
from config import logger
from dotenv import load_dotenv

load_dotenv()


class SpotifyAuthManager():
    """
        A class used to handle Spotify Oauth.
        Refreshable user authentication.

        Owned by Playlist & ArtistManager.

        Args:
            playlist
            new_artists

        Instance Attributes
            artists
            playlist
            spotify
            token
            usr_playlists
            artist_ids
            ply_id

        Class Attributes:
            username
            client_id
            client_secret
            scope
            redirect_uri
    """

    username = os.environ['SPOTIFY_USERNAME']
    client_id = os.environ['SPOTIFY_CLIENT_ID']
    client_secret = os.environ['SPOTIFY_CLIENT_SECRET']
    scope = os.environ['SPOTIFY_SCOPE']
    redirect_uri = os.environ['SPOTIFY_REDIRECT_URI']

    def __init__(self, playlist='test'):

        self.playlist = playlist

        self.token_info = None
        self.response_code = None
        self.client_mgr = None

        self.session = DataManager().start_session().session

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
                f"Token expires at {time.strftime('%c', time.localtime(self.token_info['expires_at']))}",
                exc_info=True)
            return self
        # TODO: add other exceptions
        except Exception:
            # Or scope not subset
            # expired
            logger.error("No token in cache, or invalid scope.", exc_info=True)

        return self

    def create_auth_spotify(self):
        """
        Create Spotify object for Authorization Code flow.

        Args: token, session, client_mgr
        """

        try:
            auth_info = {'auth': self.token_info['access_token'], 'requests_session': self.session,
                         'client_credentials_manager': self.client_mgr}
            return catch(spotipy.Spotify, auth_info)
        except TypeError:
            logger.error("Token error.", exc_info=True)

#  getting user playlistID artists spotify info and updating playlist.


class SpotifyPlaylistManager():
    """
        Class to get User Playlist information.
        ID
        Artists in playlist
        Followers
    """

    def __init__(self, playlist_name=None, spotify=None):

        # TODO: EAFP
        # if self.spotify is None:
        #     self.spotify = SpotifyAuthManager().create_client_mgr(
        #     ).get_auth_token().create_auth_spotify()
        # else:
        #     self.spotify = spotify

        self.spotify = None
        self.playlist_name = playlist_name

        self.playlist_id = None

    def get_playlist_id(self):
        """
        Return uri of specified user playlists. 
        """

        self.ply_id = jmespath.search(f"items[?name=='{self.playlist_name}'].id",
                                      self.spotify.current_user_playlists())[0]

    def get_playlist_artists(self):
        """
            Return list of artists in playlists.
        """
        pass

    def get_playlist_tracks(self):
        """
        """
        # Get full details of the tracks of a playlist owned by a use
        self.spotify.user_playlist_tracks()

    def add_tracks(self, uris):
        """
        Add tracks to playlist matchig ply_id attribute.

        Args: uris
        """

        self.spotify.user_playlist_add_tracks(self.username, self.ply_id, uris)

    def clear_playlist(self, spotify, user, playlist_id=None):
        """ Remove all tracks from playlist. """

        playlist_tracks = spotify.user_playlist_tracks(user, playlist_id)
        spotify.user_playlist_remove_all_occurrences_of_tracks(
            user, playlist_id, playlist_tracks, snapshot_id=None)

    def update_playlist(self):
        """
        Update spotify playlist
        """
        pass
# TODO:
# match with schedule
# user_playlist_reorder_tracks(

# How to use this when playing on webapp?
# currently_playing(market=None)
# user_playlist_is_following


class SpotifyArtistManager():
    """
        Class for getting artist info from Spotify API.

    """
    # Don't need oathentication to get artist info. Less rate limiting.

    def __init__(self, artists):

        self.artists = artists
        self.spotify_artists = []

    def get_artist_info(self):
        """
        Set spotify_artists attribute to list of artist json objects returned from
        find_artist_info().
        """

        for each in self.artists:
            result = self.find_artist_info(query=each, item_type='artist')

            if jmespath.search("artists.items", result):
                logger.info(f'{each} artist found in Spotify Library')
                self.spotify_artists.append(result)
            else:
                continue

        logger.info('Spotify API Artinst Endpoint Responses: \n')

    def find_artist_info(self, query=None, item_type=None):
        """
            Query Spotify Search endpoint.
        """

        kwargs = {'q': f'{item_type}: {query}', 'type': item_type}
        result = self.spotify.search(**kwargs)

        result = result if result is not None else None
        return result

    def save_artist_json(self):
        """
            Save artist json objects to file.
        """
        # TODO: add way to check for duplicates

        with open('spotify_artists.json', 'w') as f:
            json.dump(self.spotify_artists, f)

    def get_top_tracks(self, num_songs=10):
        """ Return uris of all the artists top ten tracks."""

        for each in self.artist_ids:
            results = self.spotify.artist_top_tracks(each)
            uris = {
                self.get_uri(each['uri'])
                for each in results['tracks'][:num_songs]}
        return uris

    def spotify_stage_df(self):
        """
            Stage artist responses in df.
        """
        # TODO: add absolute path to saved json
        df = pd.read_json('spotify_artists.json', orient='records')
        df.rename(axis=1, mapper={
                  'artists': 'spotify_responses'}, inplace=True)
        return df

    def format_artist_data(self):
        """
            Formats Artist responses to be loaded into Dataframe.
        """

        return jmespath.search(
            "[].artists.items[].{artist_name: name, genres: genres, spotify_id: id,"
            "popularity: popularity, followers: followers.total}", self.spotify_artists)

    def spotify_df(self):
        """
            Spotify Gate 2
        """

        data = self.format_artist_data()
        return pd.Dataframe(data)

    def small_spotify_df(self, df):
        """
            Filter for artists less than 1000 followers and sort descending.
        """
        small_artists_df = df.copy()
        small_artists_df[small_artists_df['followers'] < 1000].sort_values(
            'followers', axis=0, ascending=False)
        return small_artists_df


def catch(func, kwargs):
    """
    Helper function for logging unknown exceptions.
    """

    try:
        return func(**kwargs)
    except Exception:
        logger.exception('Exception occured', exc_info=True)
        raise