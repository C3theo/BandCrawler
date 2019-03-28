"""
    Find details about upcoming local concerts.
    Build playlists on Spotify and keep them up to date with upcoming concert schedule.

"""
import re
import os
import pdb
from datetime import datetime

from requests import Session
from bs4 import BeautifulSoup

import spotipy
import spotipy.util as util

import numpy as np
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
    """
    def __init__(self, **kwargs):

        self.today = datetime.today()
        self.session = None
        # super().__init__(**kwargs)
    
    def start_session(self):
        """ Create Session object """

        self.session = Session()
        return self

    def get_response(self, url, **kwargs):
        """ Return response from website"""
     
        if self.session is not None:
            try:
                return self.session.get(url, **kwargs)
            except Exception as e:
                raise e
                

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

    def __init__(self, where=None, **kwargs):
        
        self.where = where
        self.soup = None
        self.response = None
        self.lineup = None
        
        try:
            self.url = self.links[where]
        except Exception as e:
            raise ConcertNotFoundError(e)

        super().__init__(**kwargs)


    def stage_data(self, data):
    # create records for each time an artist plays
        schema = {'Artist':[],
                'ShowDate':[],
                'ShowLocaton':[],
                'ShowInfo':[]}

        for date, events in concerts.items(): 
            for show in events['Shows']:
                for artist in show['Artists']:
                    schema['ShowDate'].append(date)
                    schema['ShowLocaton'].append(show['ShowLocation'])
                    schema['ShowInfo'].append(show['ShowInfo'])
                    schema['Artist'].append(artist)

        df = pd.DataFrame(data=schema)
        df['SourceRowID'] = df.index
        df = df[['SourceRowID','Artist', 'ShowDate', 'ShowLocation', 'ShowInfo']]
        df.loc[['ETLID']] = 1000
        
        return df
    
    def gate2_df(self, df):
        """ """
        ## use prefix function
        gate2_df = df
        gate2_df.ShowDate = pd.to_datetime(gate2_df.ShowDate)
        days =  gate2_df.ShowDate.apply(lambda x: x.day).astype(str)
        key = gate2_df.index.astype(str)
        key_df = key + days
        key_df = key_df.astype(int)
        gate2_df['ShowKey'] = test
        gate2_df = gate2_df[['ShowKey', 'SourceRowID', 'ShowDate', 'ShowLocaton', 'ETLID']]



#     def record_data(self, data):
#         """Return multi-indexed dataframe of all collected concert data."""
        
#         # Where, When, Who, How Much?
#         # Columns: Venue, Showtime, Artist, Price
#         # Stores All Data
#         # Not really necessary if just trying to keep track of artists in playlist

#         labels = ['Venue', 'Artists', 'Price']
#         conc_df = pd.DataFrame()
        
#         for date in data:
#             concerts = data[date]['Shows']
#             df = pd.DataFrame(data=concerts) 
            
#             tuples = list(zip([date] * 3, list(labels)))
#             index = pd.MultiIndex.from_tuples(tuples, names=['Date', 'Details'])
#             df.columns = index
            
#             conc_df = pd.concat([conc_df, df], axis=1)
                       
#         return conc_df
        
    
#     def dates_artists(self, data):
#         """Return dataframe of all artist playing on a certain date."""
#         ### TODO save different df's at in the beginning with the soup
        
#         date_artists = []
#         for date, event in data.items():
#             artists = [art for show in event['Shows'] for art in show['Artists']
#                if art.lower() != 'open mic']
#         if artists:
#             date_artists.append({date:artists})
        
#         ##TODO: make helper function
#         da_df = pd.DataFrame()
#         for show_date in date_artists:
#             df = pd.DataFrame(data=show_date)
#             da_df = pd.concat([df, conc_df], axis=1)
        
#         return da_df
    
#     def artists_df(self, data):
#         """Return dataframe with artists as row index values and list of all dates."""
        
#         # Unique set of Artists
#         artists = {each for k, v in data.items()
#                    for show in v['Shows']
#                    for each in show['Artists']}
#         artists = sorted(list(artists))
    
#         # Lists of aLl Show Dates for each Artist
#         a_dict = {each:[] for each in artists}
#         for date, event in data.items():
#             for show in event['Shows']:
#                 for artist in show['Artists']:
#                     a_dict[artist].append(date)
                    
#         art = {'Artists' : [each
#                             for k, v in a_dict.items()
#                             for each in [k] * len(v)]}
                    
#         df_data = {'Artists':list(a_dict.keys()),
#                    'Dates':list(a_dict.values()),
#                    'Spotify':False,
#                    'Future Shows':False}
#         df = pd.DataFrame(data=df_data)
#         df = df.astype({'Artists':str,
#                    'Dates':list,
#                    'Spotify':bool,
#                    'Future Shows':bool})
        
#         return df

    def update_future_shows(self):
        """Update column in df if artist has shows within the next 30 days."""
        # TODO
        
    
    def start_session(self):

        super().start_session()
        self.session.headers.update(self.headers)
        return self

    def get_response(self):

        # self.response = self.session.get(
        # self.url, headers=self.headers, stream=True)
        params = {'stream':True}
        self.response = super().get_response(self.url, **params)

    def get_concert_soup(self):

        if hasattr(self, 'response'):
            self.soup = BeautifulSoup(self.response.content, 'lxml')
        else:
            return None

    def athens_concerts(self):
        """Return dictionary of upcoming concerts in Athens, GA. From Flagpole website."""

        events = self.soup.find(class_='event-list').findAll('h2')
        concert_dict = {}
        for e in events:
            
            concert_date = e.text
            concert_date =  f'{concert_date} {datetime.today().year}'
            concert_datetime = datetime.strptime(concert_date, '%A, %B %d %Y')
            # datetime objects not working as dict keys
            
            event_count = e.findNext('p')
            venues = e.findNext('ul').findAll('h4')
            concert_dict[concert_date]= {'datetime':concert_datetime,
                                         'Event Count':event_count.text}
            ## Event Count for Data Audit
            concert_dict[concert_date]['Shows'] = []
            
            for v in venues:
                info = v.findNext('p')
                bands = info.fetchNextSiblings()
                names = [each.strong.text.replace('\xa0', '')
                        for each in bands if each.strong]
                concert_dict[concert_date]['Shows'].append({'ShowLocation':v.text,
                                                            'Artists':names,
                                                            'ShowInfo':info.text})
                
        return concert_dict

    def coachella_lineup(self):
        """Return list of artists playing at Coachella 2018"""
        pass

    def bonnaroo_lineup(self):
        """Return list of artists playing at Bonnaroo 2019"""
        
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
    redirect_uri = 'https://www.google.com/'

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
        "Return list user playlist names."

        self.usr_playlists = self.sp.current_user_playlists()
        return self

    def get_playlist_id(self, name=None):
        'Return uri of specified user playlists'

        for each in self.usr_playlists['items']:
            if each['name'] == name:
                self.ply_id = self.get_uri(each["uri"])
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
