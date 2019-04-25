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

class PlaylistManager():
    """
        A class used to handle Spotify authentication and updating playlist.

        Args:
            playlist
            new_artists

        Instance Attributes
            artists
            playlist
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

    # TODO: Test env file
    username = os.environ['SPOTIFY_USERNAME']
    client_id = os.environ['SPOTIFY_CLIENT_ID']
    client_secret = os.environ['SPOTIFY_CLIENT_SECRET']
    scope = os.environ['SPOTIFY_SCOPE']
    redirect_uri = os.environ['SPOTIFY_REDIRECT_URI']

    def __init__(self, playlist=None, artists=None):

        self.playlist = playlist
        self.artists = artists

        self.token_info = None
        self.response_code = None
        self.sp = None
        self.user_playlists = None
        self.ply_id = None

        self.client_mgr = None
        self.spotify_artists = []

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

    def create_spotify(self):
        """
        Create Spotify object.

        Args: token, session, client_mgr
        """

        try:
            auth_info = {'auth': self.token_info['access_token'], 'requests_session': self.session,
                         'client_credentials_manager': self.client_mgr}
            # Create Spotify object
            self.sp = catch(spotipy.Spotify, auth_info)
        except TypeError:
            logger.error("Token error.", exc_info=True)

    # TODO: Determine how the Playlist will be 'maintained'
    def create_playlist(self):
        """
        Create playlist with playlist attribute if it does not already exist.
        """
        try:
            self.sp.user_playlist_create(
                self.username, self.playlist, public=False)
        except spotipy.client.SpotifyException:
            logger.error(
                fr"Invalid Scope: {self.sp.client_credentials_manager.scope}", exc_info=True)
        except Exception:
            logger.error("Exception occured.", exc_info=True)

    def playlist_exists(self):
        """
        Check if playlist exists for user.
        """
    # TODO: Finish fcn
        self.get_playlist_id()

    def get_playlists(self):
        """
        Set usr_playlist attribute to list of current user playlist names.
        """

        self.usr_playlists = self.sp.current_user_playlists()
        return self

    def get_playlist_id(self):
        """
        Return uri of specified user playlists. 
        """

        if self.usr_playlists is not None:
            self.ply_id = jmespath.search(f"items[?name=='{self.playlist}'].id", self.usr_playlists)[0]
        else:
            # Bad practice??
            self.get_playlists()
            self.get_playlist_id()

    def get_artist_info(self):
        """ 
        Set spotify_artists attribute to list of artist json objects returned from
        find_artist_info().
        """

        #TODO: Add way to grab top 10 songs

        for each in self.artists:
            result = self.find_artist_info(query=each, item_type='artist')

            if jmespath.search("artists.items", result):
                logger.info(f'{each} artist found in Spotify Library')
                self.spotify_artists.append(result)
            else:
                continue

            # self.artist_ids = [
            #     self.find_artist_info('artist', each)[
            #         'artists']['items'][0]['uri']
            #     for each in self.artists]
        # except IndexError:
        #     logger.error('Artist not on spotify')

    def find_artist_info(self, query=None, item_type=None):
        """ Query Spotify Search endpoint. """

        kwargs = {'q': f'{item_type}: {query}', 'type': item_type}
        result = self.sp.search(**kwargs)

        result = result if result is not None else None
        return result

        # General Error handling
        # return catch(self.sp.search, kwargs)
    
    def fix_name(self):
        """
        Fix artist name if it doesn't match what's in Spotify library.
        """

        pass

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

    def upload_image(self):
        pass


def catch(func, kwargs):
    """
    Helper function for logging unknown exceptions.
    """

    try:
        return func(**kwargs)
    except Exception:
        logger.exception('Exception occured')
        raise
