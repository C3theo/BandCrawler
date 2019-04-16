"""
    This modules contains classes to build playlists that are up to date
    with the schedule of touring musicians.
    Extraction:
        Web Scrapers
        Spotify API

    Transformation:
        Spotify Artist Table

        Concert Date Table

        Current Artist Table

    Loading
        Pandas Dataframes -> Sqllite Database
        Flask Web application

    Data Sources:
        Spotify API
        Local newspaper and concert websites

    Example:


TODO:
    Flask Web App

"""
import os
# TODO: Refactor out time and just use datetime
import time
from pathlib import WindowsPath

import spotipy
import spotipy.oauth2 as oauth
import spotipy.util as util

import config
from concert_etl import DataManager
from config import logger

# TODO:
# separate class for playlist
# class ArtistDataManager():


class PlaylistManager():
    """
    A class used to handle Spotify authentication and updating playlist.

    Args:
        ply_name
        new_artists

    Instance Attributes
        artists
        ply_name
        sp
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
# Shocal app config
# TODO move to env file for deployment
    # username = os.environ['SPOTIPY_USERNAME']
    # client_id = os.environ['SPOTIPY_CLIENT_ID']
    # client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
    # scope = 'playlist-modify-private playlist-read-private'
    # redirect_uri = 'https://www.google.com/'

    # TODO: Test env file
    username = os.environ['SPOTIFY_USERNAME']
    client_id = os.environ['SPOTIFY_CLIENT_ID']
    client_secret = os.environ['SPOTIFY_CLIENT_SECRET']
    scope = os.environ['SPOTIFY_SCOPE']
    redirect_uri = os.environ['SPOTIFY_REDIRECT_URI']

    def __init__(self, ply_name=None, artists=None):

        self.ply_name = ply_name
        self.artists = artists

        self.token_info = None
        self.response_code = None
        self.sp = None
        self.user_playlists = None
        self.ply_id = None
        self.artist_ids = None
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
        self.client_mgr = spotipy.oauth2.SpotifyOAuth(self.client_id, self.client_secret,
                                                      self.redirect_uri, scope=self.scope,
                                                      cache_path=cache_path)

    def get_auth_token(self):
        """
        Get oauth token from cache or prompt for new token.
        """

        try:
            self.token_info = self.client_mgr.get_cached_token()
            logger.info(
                f"Token expires at {time.strftime('%c', time.localtime(self.token_info['expires_at']))}", exc_info=True)
            return self
        # TODO: add other exceptions
        except Exception:
            # Or scope not subset
            # expired
            logger.error("No token in cache, or invalid scope.", exc_info=True)

    def create_spotify(self):
        """
        Create Spotify object.

        Args: token, session, client_mgr
        """

        auth_info = {'auth': self.token_info['access_token'], 'requests_session': self.session,
                     'client_credentials_manager': self.client_mgr}
        # Create Spotify object
        # TODO: Test token and client_mgr
        self.sp = catch(spotipy.Spotify, auth_info)

    # TODO: Determine how the Playlist will be 'maintained'
    def create_playlist(self):
        """
        Create playlist with ply_name attribute if it does not already exist.
        """

        try:
            self.sp.user_playlist_create(
                self.username, self.ply_name, public=False)
        except spotipy.client.SpotifyException:
            logger.error(
                fr"Invalid Scope: {self.sp.client_credentials_manager.scope}", exc_info=True)
        except Exception:
            logger.error("Exception occured.", exc_info=True)

    def get_playlists(self):
        """
        Set usr_playlist attribute to list of current user playlist names.
        """

        self.usr_playlists = self.sp.current_user_playlists()
        return self

    def get_playlist_id(self, name=None):
        """
        Return uri of specified user playlists. 
        """

        # TODO: Refactor w/o for loop
        # list comp
        
        for each in self.usr_playlists['items']:
            # How to use catch()??
            #  Check format of usr_playlists
            try:
                each['name'] == name
            except Exception:
                logger.exception(" Exception occured. ")
            else:
                self.ply_id = self.get_uri(each["uri"])

    def get_artist_ids(self):
        """ 
        Set artist_ids attribute to list of artist ids returned from
        find_artist_info().
        """

        self.artist_ids = [
            self.find_artist_info('artist', each)['artists']['items'][0]['uri']
            for each in self.artists]

    def find_artist_info(self, category, item):
        """ Query artist api """

        kwargs = {'q': fr'{category}: {item}', 'type': category}
        return catch(self.sp.search, kwargs)

    def get_top_tracks(self, num_songs=10):
        """ Return uris of all the artists top ten tracks."""

        for each in self.artist_ids:
            results = self.sp.artist_top_tracks(each)
            uris = {
                self.get_uri(each['uri'])
                for each in results['tracks'][:num_songs]}
        return uris

    def add_tracks(self, uris):
        """
        Add tracks to playlist matchig ply_id attribute.

        Args: uris
        """

        self.sp.user_playlist_add_tracks(self.username, self.ply_id, uris)

    def clear_playlist(self, sp, user, playlist_id=None):
        """ Remove all tracks from playlist. """

        playlist_tracks = sp.user_playlist_tracks(user, playlist_id)
        sp.user_playlist_remove_all_occurrences_of_tracks(
            user, playlist_id, playlist_tracks, snapshot_id=None)

    def update_playlist(self):
        """
        Update spotify playlist
        """
        pass

    def get_uri(self, string):
        """
        Return URI at the end of Spotify String.

        Args: string
        """
        str_list = string.split(':')
        return str_list[-1]


def catch(func, kwargs):
    """
    Helper function for logging unknown exceptions.
    """

    try:
        return func(**kwargs)
    except Exception:
        logger.exception('Exception occured')
