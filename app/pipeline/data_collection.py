"""
    Module for data collection from the web and Spotify API.

"""
import pdb
from bs4 import BeautifulSoup
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from datetime import datetime
from datetime import date, timedelta
from config import logger

import pandas as pd
import jmespath
# from .spotify_adapter import SpotipyAdapter

class TimeoutHTTPAdapter(HTTPAdapter):
    """
        Subclass HTTPAdapter to add timeouts to session
    """

    def send(self, *args, **kwargs):
        kwargs['timeout'] = 5
        return super(TimeoutHTTPAdapter, self).send(*args, **kwargs)


def start_session(retries=3, backoff_factor=0.3,
                  status_forcelist=(500, 502, 504)):
    """ Create Session object with user-agent headers, timeout, 
    and retry backoff."""

    headers = {
        'user-agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            'AppleWebKit/537.36 (KHTML, like Gecko)'
            'Chrome/68.0.3440.106 Safari/537.36')}

    retry = Retry(total=retries, read=retries, connect=retries,
                  backoff_factor=backoff_factor, status_forcelist=status_forcelist)

    with Session() as session:
        adapter = TimeoutHTTPAdapter(max_retries=retry)
        session.headers.update(headers)
        session.mount('http:', adapter)
        session.mount('https://', adapter)
        return session

# Strategy Pattern
class Scraper:
    """
        Behavior:
            Scrape Website
            Create Beautifulsoup object

        Data:
            url
    """

    def __init__(self, session=None):

        self.url = 'http://www.flagpole.com/events/live-music'
        self.session = session
        self.response = None

    def get_response(self):
        """
        Set response attr to response
        returned from URL.

        Args: url string
        """

        try:
            self.response = self.session.get(self.url, stream=True)
            logger.info('Response from %s: \n %s', self.url, self.response)
        except Exception:
            logger.exception("Exception occured", exc_info=True)

    def get_concerts(self):
        """
        """
        content = self.response.content
        soup = BeautifulSoup(content, 'lxml')
        return parse_soup(soup)


def parse_soup(soup):
    """
        Return dictionary of upcoming shows in Athens, Ga.

        Args:
            self.concert_soup

        Return:
            concert: dict
                keys: Date, Event Count, Show Location, Artists, 
                and Show information.
    """

    # logger.info(' Building Concert Dict. ')

    events = soup.find(class_='event-list').findAll('h2')
    # TODO: change to list of dicts for pandas
    concert_dict = {}
    concert_dict['concerts'] = []
    for event in events:

        concert_date = event.text
        concert_date = fr'{concert_date} {date.today().year}'
        concert_datetime = datetime.strptime(concert_date, '%A, %B %d %Y')

        event_count = event.findNext('p')

        # concert_dict[concert_date] = {'date_time': concert_datetime,
        #                               'event_count': event_count.text,  # Event Count for Data Audit
        #                               'shows': []}

        venues = event.findNext('ul').findAll('h4')
        shows = []
        for venue in venues:
            info = venue.findNext('p')
            bands = info.fetchNextSiblings()
            names = [each.strong.text.replace('\xa0', '')
                     for each in bands if each.strong]
            shows.append({'date_time': concert_datetime,
                          'show_venue': venue.text,
                          'show_artists': names, 'show_info': info.text
                          })
            # concert_dict[concert_date]['shows'].append({'show_venue': venue.text,
            #                                             'show_artists': names,
            #                                             'show_info': info.text})

        concert_dict['concerts'].extend(shows)
    # TODO: add ability to log range of concert dates
    # logger.info('Concerts found for these dates)
    # TODO: pprint logs
    # logger.info('Concerts Found: \n\n %s', concert_dict)
    return concert_dict


class Concert:
    """
        Created from concert_dict.
    """

    def __init__(self, venue=None, date=None, artists=None):

        self.venue = venue
        self.date = date
        self.artists = artists


class ConcertManager:

    def __init__(self, concerts=None):
        self.observers = []
        self.concerts = concerts
        self.week_range = get_week_range()

        self.weekly_concert_schedule = None

    def attach(self, observer):
        self.observers.append(observer)

    def create_weekly_schedule(self):
        """
            Return list of concerts for the given week.
        """

        week_concerts = []
        week_start, week_end = self.week_range

        if self.concerts:
            for concert in self.concerts:
                if week_start < concert.date < week_end:
                    week_concerts.append(concert)
                elif week_start == concert.date:
                    week_concerts.append(concert)

        else:
            raise ValueError("No concerts.")
        # raise ValueError("No concerts for given week")

        self.weekly_concert_schedule = week_concerts
        self.update_observers()

    def update_observers(self):
        for observer in self.observers:
            observer()

# helper
def get_week_range():
    """
        Return start and end datetime objects for todays date.
    """
    week_start_int = date.today().weekday()
    week_start = date.today() - timedelta(days=week_start_int)
    week_end_int = 7 - week_start_int
    week_end = date.today() + timedelta(days=week_end_int)

    return week_start, week_end


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def get_weeks_shows(concert_dict):
    # This sucks but works
    data = jmespath.search("concerts[*]", concert_dict)
    date_times = jmespath.search("concerts[*].date_time", concert_dict)

    start_date, end_date = get_week_range()

    for date in daterange(start_date, end_date):
        for i, each in enumerate(date_times):
            if each.month == date.month and each.day == date.day:
                show_index = i

    return data[:show_index]


def concerts_df(concert_dict):
    """
        Using Pandas
    """
    
    df = pd.DataFrame(data=concert_dict['concerts'])
    return df

def weeks_artist(df):
    """
        Using Pandas
    """
    _, week_end = get_week_range()
    artists = df[df['date_time'] < week_end]['show_artists'].tolist()
    artists = [j for i in artists for j in i]
    return artists

# move this into different module?
class Playlist:

    def __init__(self, concert_manager=None):
        self.concert_manager = concert_manager
        self.catalog = None

    def __call__(self):
        self.update_playlist()

    def update_playlist(self):
        print('Updating playlists')
        # query catalog
        # get spotify_id

# singleton
class Catalog(list):
    """
        Class to create and update catalog of artist information.
        Playlist will use this catalog to get Artist and track id's.
    """

    def __init__(self, concert_manager=None):
        self.concert_manager = concert_manager
        self.artists = []
        # key = artist name, value = spotify_id
        # how to get spotify_id
        # top_tracks

    def __call__(self):
        self.update_catalog()

    def get_artists(self):
        concerts = self.concert_manager.weekly_concert_schedule
        for concert in concerts:
            # if concert.artists not in self:
            self.artists.extend(concert.artists)

    def update_catalog(self):
        self.get_artists()
        # check if artist exists

        # for artists in artists:
        #     if artist in catalog:
        #         return True
        #     else:
        #         self.append(artist)


class QueryTemplate:
    def connect(self):
        pass

    def construct_query(self):
        pass

    def do_query(self):
        pass

    def format_results(self):
        pass

    def output_results(self):
        pass

    def process_format(self):
        self.connect()
        self.construct_query()
        self.do_query()
        self.format_results()
        self.output_results()

# # Refactor Spotify Info below


# """
#     This modules contains classes to build playlists that are up to date
#     with the schedule of touring musicians.

#     Extraction:
#         Artist Information

#     Transformation:
#         Spotify Artist Table

#     Loading
#         Pandas -> SQL

#     Sources:
#         Spotify API


# """

# import os
# import pdb
# # TODO: Refactor out time and just use datetime
# import time
# from pathlib import WindowsPath
# import jmespath


# from .concert_etl import DataManager
# from config import logger
# from dotenv import load_dotenv

# import spotipy
# from spotipy.oauth2 import SpotifyOAuth
# load_dotenv()

# # create spotify singleton
# spotify = SpotipyAdapter()

# class SpotipyAdapter():
#     """
#         Adapter to spotipy library.
#     """

#     def authenticate_user(self):

#     def update_playlist(self):

#     def get_artist_info(self):


# # make class singleton
# class SpotifyAuthManager():
#     """
#         A class used to handle Spotify Oauth.
#         Refreshable user authentication.

#         Owned by Playlist & ArtistManager.

#         Args:

#         Instance Attributes

#         Class Attributes:

#     """

#     username = os.environ['SPOTIFY_USERNAME']
#     client_id = os.environ['SPOTIFY_CLIENT_ID']
#     client_secret = os.environ['SPOTIFY_CLIENT_SECRET']
#     scope = os.environ['SPOTIFY_SCOPE']
#     redirect_uri = os.environ['SPOTIFY_REDIRECT_URI']

#     def __init__(self):

#         self.token_info = None
#         self.response_code = None
#         self.client_mgr = None

#         self.session = DataManager().start_session().session
#         # use same session
#         # self.session = session

#     def create_client_mgr(self):
#         """
#         Create SpotifyOauth object.

#         Args:
#             client_id
#             client_secret
#             redirect_uri
#             scope
#             cache_path

#         """

#         cache_path = WindowsPath("__pycache__") / fr'.cache-{self.username}'
#         self.client_mgr = SpotifyOAuth(self.client_id, self.client_secret,
#                                        self.redirect_uri, scope=self.scope,
#                                        cache_path=cache_path)
#         return self

#     def get_auth_token(self):
#         """
#         Get oauth token from cache or prompt for new token.
#         """

#         try:
#             self.token_info = self.client_mgr.get_cached_token()
#             logger.info(
#                 f"Token expires at {time.strftime('%c', time.localtime(self.token_info['expires_at']))}")
#             return self
#         # TODO: add other exceptions
#         except Exception:
#             # Or scope not subset
#             # expired
#             logger.error("No token in cache, or invalid scope.", exc_info=True)

#         return self

#     def refresh_auth_token(self):
#         """
#             Refresh authentication token.

#             Same spotify obect used throughout. How to call from owning classes.
#         """

#         self.client_mgr.refresh_access_token(self.token_info['refresh_token'])
#          logger.info(
#                 f"Token refreshed, expires at: {time.strftime('%c', time.localtime(self.token_info['expires_at']))}")


#     def create_auth_spotify(self):
#         """
#         Create Spotify object for Authorization Code flow.

#         Args: token, session, client_mgr
#         """

#         try:
#             auth_info = {'auth': self.token_info['access_token'], 'requests_session': self.session,
#                          'client_credentials_manager': self.client_mgr}
#             return catch(spotipy.Spotify, auth_info)
#         except TypeError:
#             # Why TypeError?
#             logger.error("Token error.", exc_info=True)


# class SpotifyPlaylistManager():
#     """
#         Class to get User Playlist information.
#         ID
#         Artists in playlist
#         Followers
#     """

#     def __init__(self, playlist_name=None, spotify=None):

#         # TODO: EAFP
#         # if self.spotify is None:
#         #     self.spotify = SpotifyAuthManager().create_client_mgr(
#         #     ).get_auth_token().create_auth_spotify()
#         # else:
#         #     self.spotify = spotify

#         self.spotify = spotify
#         self.playlist_name = playlist_name

#         self.playlist_id = None

#     def get_playlist_id(self):
#         """
#         Return uri of specified user playlists.
#         """

#         self.playlist_id = jmespath.search(f"items[?name=='{self.playlist_name}'].id",
#                                            self.spotify.current_user_playlists())[0]

#     def get_playlist_artists(self):
#         """
#             Return list of artists in playlists.
#         """
#         pass

#     def get_playlist_tracks(self):
#         """
#         """
#         # Get full details of the tracks of a playlist owned by a user
#         self.spotify.user_playlist_tracks()

#     def add_tracks(self, uris):
#         """
#         Add tracks to playlist matchig ply_id attribute.

#         Args: uris
#         """

#         self.spotify.user_playlist_add_tracks(self.username, self.ply_id, uris)

#     def clear_playlist(self, spotify, user, playlist_id=None):
#         """ Remove all tracks from playlist. """

#         playlist_tracks = spotify.user_playlist_tracks(user, playlist_id)
#         spotify.user_playlist_remove_all_occurrences_of_tracks(
#             user, playlist_id, playlist_tracks, snapshot_id=None)

#     def update_playlist(self):
#         """
#         Update spotify playlist
#         """
#         pass

# # TODO:
# # match with schedule
# # user_playlist_reorder_tracks(

# # How to use this when playing on webapp?
# # currently_playing(market=None)
# # user_playlist_is_following


# class SpotifyArtistManager():
#     """
#         Class for getting artist info from Spotify API.

#     """

#     def __init__(self, spotify, artists):

#         self.spotify = spotify
#         self.artists = artists
#         self.spotify_artists = []

#     def get_artist_info(self):
#         """
#         Set spotify_artists attribute to list of artist json objects returned from
#         find_artist_info().
#         """

#         for each in self.artists:
#             logger.info('Queried Spotify API Artist Endpoint for: \n\n %s', each)
#             result = self.find_artist_info(query=each, item_type='artist')

#             if jmespath.search("artists.items", result):
#                 # TODO: fix this log to only return artist names
#                 logger.info('Spotify API Artist Endpoint returned %s', jmespath.search("artists.items", result))
#                 self.spotify_artists.append(result)
#             else:
#                 continue

#     def find_artist_info(self, query=None, item_type=None):
#         """
#             Query Spotify Search endpoint.
#         """

#         kwargs = {'q': f'{item_type}: {query}', 'type': item_type}
#         result = self.spotify.search(**kwargs)

#         result = result if result is not None else None
#         return result

#     def get_top_tracks(self, num_songs=10):
#         """ Return uris of all the artists top ten tracks."""

#         for each in self.spotify_artists:
#             results = self.spotify.artist_top_tracks(each)

#             # uris = {
#             #     self.get_uri(each['uri'])
#             #     for each in results['tracks'][:num_songs]}
#         return uris

#     def save_artist_json(self):
#         """
#             Save artist json objects to file for logging.
#         """
#         # TODO: add way to check for duplicates

#         with open('spotify_artists.json', 'w') as f:
#             json.dump(self.spotify_artists, f)

#     def spotify_stage_df(self):
#         """
#             Create staging df from artist responses in cache.
#         """
#         # TODO: add absolute path to saved json
#         # move to testing
#         df = pd.read_json('spotify_artists.json', orient='records')
#         df.rename(axis=1, mapper={
#                   'artists': 'spotify_responses'}, inplace=True)
#         return df

#     def format_artist_data(self):
#         """
#             Formats Artist responses to be loaded into Dataframe.
#         """

#         return jmespath.search(
#             "[].artists.items[].{artist_name: name, genres: genres, spotify_id: id,"
#             "popularity: popularity, followers: followers.total}", self.spotify_artists)

#     def spotify_df(self):
#         """
#             Spotify Gate 2
#         """

#         data = self.format_artist_data()
#         return pd.Dataframe(data)

#     def small_spotify_df(self, df):
#         """
#             Filter for artists less than 1000 followers and sort descending.
#         """
#         small_artists_df = df.copy()
#         small_artists_df[small_artists_df['followers'] < 1000].sort_values(
#             'followers', axis=0, ascending=False)
#         return small_artists_df

# # load_df = spotify_df.loc[spotify_df['artist_name'].str.lower().isin(stage_df['artist'].str.lower()), :]
# # refresh token decorator
# def check_token(cls, kwargs):
#     """
#         Helper function for refreshing authentication token.
#     """

#     for k, v in list(vars(cls).items()):
#         if callable(value):
#             setattr(cls, key, refresh_token(value))

# def refresh_token(func, kwargs):
#     #wrap all methods
#     # if spotify token is old, get new one fore existing object

#     # try:
#     #     # spotify.method() with existing token
#     # except:
#     #     spotify.refresh_token()
#     try:
#         # try to run method.
#         pdb.set_trace()
#         func(**kwargs)
#     except SpotifyException:
#         obj.spotify.refresh_auth_token()


# def catch(func, kwargs):
#     """
#     Helper function for logging unknown exceptions.
#     """

#     try:
#         return func(**kwargs)
#     except Exception:
#         logger.exception('Exception occured', exc_info=True)
#         raise
