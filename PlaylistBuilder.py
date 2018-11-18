

"""
    Find details about upcoming local concerts.

    Build playlists on Spotify and keep them up to date with upcoming concert schedule.
"""
import re
import os
import pdb

from datetime import date
import pandas as pd


from requests import Session
from bs4 import BeautifulSoup

import spotipy
import spotipy.util as util



## TODO
# When to use these custom Errors
class AuthorizationError(ValueError):
    pass

class ArtistNotFoundError():
    pass

class Manager():
    """"""

    def __init__(self, **kwargs):

        self.today = date.today()

        self.session = None
        self.session_params = kwargs
       
    def start_session(self, auth_tokens=None):
        "auth_tokens - tuple"
        if auth_tokens is not None:
            with Session() as s:
                self.session = s
                self.session.auth = auth_tokens
                self.session.headers.update(self.session_params)
                return self    
        else:
            raise AuthorizationError()

        def recv_message(self, url):
        " Return response form website"
        # Cases:
        # No-API - Need kwargs for header info, don't need auth token
        # API - Don't need kwargs, need Spotify Auth token - Check bad response
        # TODO
        # How to get Authorization code
        # self.session.params = {}
        # self.session.params['auth_token'] = auth_token
        # Pass Dictionary as kwargs???

        if self.session is not None:
            return self.session.get(url)
        else:
            raise AuthorizationError()
        

    def record_data(self, data):
        "Return dataframe from dictionary of collected data."
        # Where, When, Who, How Much?
        # Columns: Venue, Showtime, Artist, Price

        self.df = pd.DataFrame(data)
        return self

    def keep_time(self):
        "Remove all entries from before today's date."
        # TODO
        # Make sure self.df.ShowTime.toordinal() < self.today.toordinal()
        self.df[self.df.ShowTime < self.today]
        return self


        
class ConcertManager(Manager):
    """ Reporter, Tracker """

    headers = {
        'user-agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            'AppleWebKit/537.36 (KHTML, like Gecko)'
            'Chrome/68.0.3440.106 Safari/537.36')}
    links = {
        'Athens': 'http://www.flagpole.com/events/live-music',
        'Music Midtown': 'https://www.musicmidtown.com/lineup/interactive/'}

    def __init__(self, url=None):

# Smelly
        if url in self.links.keys():
            self.url = self.links[url]
        else:
            # raise url not found exception, but keep going
            self.url = url

        session_dict = {'url':self.url, 'headers':self.headers, 'stream':True}
        super().__init__(session_dict)

        self.response = super().start_session().recv_message()

        self.soup = None
        self.response = None
        self.concerts = None

    def get_concert_html(self):

        # self.response = self.session.get(
        # self.url, headers=self.headers, stream=True)
        

        if self.response.ok:
            return self
            # else: return self.response.exception

    def get_concert_soup(self):

        if hasattr(self, 'response'):
            self.soup = BeautifulSoup(self.response.content, 'lxml')
            return self
        else:
            return None

    # def midtown(func):

    #     def search_wrapper(self):
    #         search = re.compile('c-lineup__caption-text js-view-details'
    #                             ' js-lineup__caption-text ')

    #         def str_func(soup_tag):
    #             return ' '.join(soup_tag.text.split())

    #         return func(self, str_func, search)

    #     return search_wrapper
    
    # def athens(func):

    #     def search_wrapper(self):
    #         search = re.compile("")

    #         def str_func(soup_tag):
    #             return ' '.join(soup_tag.text.split())

    #         return func(self, str_func, search)

    #     return search_wrapper

    # @midtown
    # # def search(self, str_func, search_func):
    #     self.artists = {
    #         str_func(each) for each in self.soup.findAll(class_=search_func)}

    def __repr__(self):
        return f"ConcertManager({self.url})"

    def __str__(self):
        return f"ConcertManager({self.url})"


class PlaylistManager(Manager):
    """Judge, Sorter
     """

    # TODO Get API Keys again

    username = os.environ['SPOTIPY_USERNAME']
    client_id = os.environ['SPOTIPY_CLIENT_ID']
    client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
    redirect_uri = os.environ['SPOTIPY_REDIRECT_URI']
    # scope = os.environ['SPOTIPY_SCOPE']
    scope = 'playlist-read-private playlist-modify-private'

    def __init__(self, concert_manager=None):

        self.artists = concert_manager.artists
        self.session = Session()
        self.sp = None

        self.token = None
        self.usr_playlists = None
        self.artist_ids = None
        self.ply_id = None

# Use cached_token if available
    def authenticate_spotify(self):

        self.token = util.prompt_for_user_token(
            self.username, self.scope, self.client_id,
            self.client_secret, self.redirect_uri)
        if self.token is not None:
            self.sp = spotipy.Spotify(
                auth=self.token, requests_session=self.session)
            return self
        else:
            raise(AuthorizationError(self.token))

    def get_playlists(self):

        self.usr_playlists = self.sp.current_user_playlists(limit=50)
        return self

    def get_playlist_id(self, name=None):

        for each in self.usr_playlists['items']:
            if each['name'] == name:
                self.ply_id = self.get_uri(each["uri"])
                return self

    def get_artist_ids(self):

        self.artist_ids = [
            self.find_artist_info('artist', each)['artists']['items'][0]['uri']
            for each in self.artists]
        return self

# spotipy.client.SpotifyException: http status: 400, code:-1 - https://api.spotify.com/v1/search?q=artist%3AThe+Revivalists&limit=10&offset=0&type=type
    def find_artist_info(self, category, item):

        kwargs = {'q': f'{category}: {item}', 'type': category}
        return self.catch(self.sp.search, kwargs)

    def check_for_duplicate(self):
        pass

    def get_top_tracks(self, num_songs=10):
        for each in self.artist_ids:
            results = self.sp.artist_top_tracks(each)
            uris = {
                self.get_uri(each['uri'])
                for each in results['tracks'][:num_songs]}
        return uris

    # @top_tracks
    def add_tracks(self, uris):

        self.sp.user_playlist_add_tracks(self.username, self.ply_id, uris)

    def get_album(self):
        pass

    def clear_playlist(self, sp, user, playlist_id=None):
        playlist_tracks = sp.user_playlist_tracks(user, playlist_id)
        sp.user_playlist_remove_all_occurrences_of_tracks(
            user, playlist_id, playlist_tracks, snapshot_id=None)

    def catch(self, func, kwargs, handle=None):
        # pdb.set_trace()
        try:
            return func(**kwargs)
        except Exception as e:
            return handle(e)

    def get_uri(self, string):
        str_list = string.split(':')
        return str_list[-1]


# def main():
#     print('Test')
#     # band_link = 'https://www.musicmidtown.com/lineup/interactive/'
#     # new_concerts = ConcertManager(url=band_link).get_concert_html()
#     # new_concerts.get_concert_soup().search()

#     # ply_manager = PlaylistManager(new_concerts)
#     # pdb.set_trace()
#     # ply_manager.authenticate_spotify()
#     # ply_manager.get_playlists()
#     # ply_manager.get_playlist_id("Music Midtown 2018")
#     # ply_manager.get_artist_ids()
#     # ply_manager.add_top_five_songs()


# if __name__ == '__main__':
#     main()
