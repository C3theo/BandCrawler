"""
    Find details about upcoming local concerts.
    Build playlists on Spotify and keep them up to date with upcoming concert schedule.

"""
import re
import os
import pdb

from requests import Session
from bs4 import BeautifulSoup

import spotipy
import spotipy.util as util

from datetime import datetime
import pandas as pd

class AuthorizationError(Exception):
    pass
class ConcertNotFoundError(Exception):
    """City Not supported."""
    pass
class ArtistNotFoundError(Exception):
    pass

class Manager:
    """ Manage sessions, responses, data storage, and remove expired data.
        kwargs: headers??? what else??
    """
    def __init__(self, **kwargs):
        ""

        self.today = datetime.today()
        self.session = None
        # super().__init__(**kwargs)
    
    def start_session(self):
        """
        Create Session object

        """

        self.session = Session()
        return self

    def get_response(self, url, **kwargs):
        """ Return response from website"""
     
        if self.session is not None:
            try:
                return self.session.get(url, **kwargs)
            except Exception as e:
                raise e
            
    def record_data(self, data):
        """Return dataframe from dictionary of collected data."""
        # Where, When, Who, How Much?
        # Columns: Venue, Showtime, Artist, Price

        self.df = pd.DataFrame(data)
        return self

    def keep_time(self):
        """Remove all entries from before today's date."""
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

# Existing Concert Sources
    links = {
        'Athens': 'http://www.flagpole.com/events/live-music',
        'Music Midtown': 'https://www.musicmidtown.com/lineup/interactive/',
        'Bonnaroo':'https://www.bonnaroo.com/lineup/interactive/'}

    def __init__(self, concert=None, **kwargs):
        
        self.concert = concert
        self.soup = None
        self.response = None
        self.lineup = None
        
        try:
            self.url = self.links[concert]
        except Exception as e:
            raise ConcertNotFoundError(e)

        super().__init__(**kwargs)
  
    def start_session(self):

        super().start_session()
        self.session.headers.update(self.headers)

    def get_response(self):

        params = {'stream':True}
        
        self.response = super().get_response(self.url, **params)

    def get_concert_soup(self):

        if hasattr(self, 'response'):
            self.soup = BeautifulSoup(self.response.content, 'lxml')
        else:
            return None

    def athens_concerts(self):
        """Return Dictionary of upcoming concert info in Athens, GA"""

        events = self.soup.find(class_='event-list').findAll('h2')
        concert_dict = {}
        for e in events:
            concert_date = e.text
            concert_date = concert_date + ' 2018'
            concert_date = datetime.strptime(concert_date, '%A, %B %d %Y')
            event_count = e.findNext('p')
            concert_dict[concert_date]= {'Event Count':event_count.text}
            venues = e.findNext('ul').findAll('h4')
            
            for v in venues:
                info = v.findNext('p')
                bands = info.fetchNextSiblings()
                names = [each.strong.text.replace('\xa0', '')
                        for each in bands if each.strong]
                concert_dict[concert_date][v.text] = {'Info':info.text, 'Artists':names}

        return concert_dict

    def athens_lineup(self, concert_dict):
        "Return list of artists playing in Athens, GA"

        lineup = [concert_dict[each][i]['Artists'] 
            for each in concert_dict 
            for i in concert_dict[each] 
            if i != 'Event Count']

        self.lineup = [i 
            for each in lineup
            for i in each
            if i.lower() != 'open mic']

    def coachella_lineup(self):
        "Return list of artists playing at Coachella 2018."
        pass

    def bonnaroo_lineup(self):
        "Return list of artists playing at Bonnaroo 2019."

        events = self.soup.findAll(class_="c-lineup__caption-text js-view-details js-lineup__caption-text ")
        self.lineup = [e.text.strip() for e in events]


# #     @midtown
# #     def search(self, search_func):
# #         self.artists = {
# #             ' '.join(each.text.split())
# #             for each in self.soup.findAll(class_=search_func)}

# #     def __repr__(self):
# #         return f"ConcertManager({self.url})"

# #     def __str__(self):
# #         return f"ConcertManager({self.url})"

# # def midtown(f):

# #     def wrapper(*args, **kwargs):
# #         search = re.compile('c-lineup__caption-text js-view-details'
# #                             ' js-lineup__caption-text ')

# #         return f(search)

# #     return wrapper

# # def athens(func):

# #     def wrapper(self):
# #         search = re.compile("")

# #         def str_func(soup_tag):
# #             return ' '.join(soup_tag.text.split())

# #         return func(self, str_func, search)

# #     return wrapper

class PlaylistManager(Manager):

    username = os.environ['SPOTIPY_USERNAME']
    client_id = os.environ['SPOTIPY_CLIENT_ID']
    client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
    scope = 'playlist-read-private playlist-modify-private'
    redirect_uri = 'http://locallhost.com/?'

    def __init__(self, name=None, artists=None, **kwargs):

        self.new_artists = artists
        self.ply_name = name
        self.sp = None
        self.token = None
        self.usr_playlists = None
        self.artist_ids = None
        self.ply_id = None
    
        super().__init__(**kwargs)

    def start_session(self):
        
        super().start_session()
        return self

# Use cached_token if available
# automate web browser/copy paste redirect link
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
    
    def create_playlist(self):
        if self.ply_name is None:
            raise Exception('Playlist does not exist')
        else:
            self.sp.user_playlist_create(self.username, self.ply_name)


    def get_playlists(self):
        "Return list of user playlist names."

        self.usr_playlists = self.sp.current_user_playlists()
        return self

    def get_playlist_id(self, name=None):
        'Return uri of specified user playlists'

        for each in self.usr_playlists['items']:
            if each['name'] == name:
                self.ply_id = self.get_uri(each["uri"])
                print(self.ply_id)
                return self
            else:
                raise Exception()

    def get_artist_ids(self):
        self.artist_ids = [
            self.find_artist_info('artist', each)['artists']['items'][0]['uri']
            for each in self.new_artists]
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
        try:
            return func(**kwargs)
        except Exception as e:
            return handle(e)

    def get_uri(self, string):
        str_list = string.split(':')
        return str_list[-1]


def main():
    con_manager = ConcertManager(concert='Athens')
    ply_manager = PlaylistManager(con_manager)
    ply_manager.start_session()
    ply_manager.authenticate_spotify()
    ply_manager.get_playlists()
    ply_manager.get_playlist_id(name='Cole')

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


if __name__ == '__main__':
    main()