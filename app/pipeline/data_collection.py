"""
    Module for data collection from the web and Spotify API.

"""
import pdb
from datetime import datetime, timedelta

import jmespath
import pandas as pd
from bs4 import BeautifulSoup
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app import db
from app.models import Artist, Concert, Track
from app.pipeline.spotify_adapter import SpotipyAdapter
from config import logger

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

    events = soup.find(class_='event-list').findAll('h2')
    concert_dict = {}
    concert_dict['concerts'] = []

    for event in events:
        concert_date = event.text
        concert_date = fr'{concert_date} {date.today().year}'
        concert_datetime = datetime.strptime(concert_date, '%A, %B %d %Y')
        # TODO: use in testing for Data Audit
        # event_count = event.findNext('p')
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
            concert_dict['concerts'].extend(shows)

    # TODO: add ability to log range of concert dates
    # logger.info('Concerts found for these dates)
    # TODO: pprint logs
    # logger.info('Concerts Found: \n\n %s', concert_dict)
    return concert_dict


class ConcertManager:
    """
    Gets Artist data from web scraper
    """

    def __init__(self, concerts=None):
        self.observers = []
        self.concerts = concerts  # for catalog - don't care about schedule
        self.df = pd.DataFrame(self.concerts['concerts'])

        self.artists = self.get_artists(self.df)
        self.weekly_artists = None

    def attach(self, observer):

        self.observers.append(observer)

    def create_weekly_schedule(self):
        """
            Set weekly artist attribute to artists playing for given week.
        """

        _, week_end = self.get_week_range()
        df = self.df.copy()
        self.weekly_artists = (df[lambda x: x['date_time']]
                               .apply(pd.Timestamp)
                               [lambda x: x['date_time'] < week_end]
                               .pipe(self.get_artists))

        self.update_observers()

    def update_observers(self):
        for observer in self.observers:
            observer()

    @staticmethod
    def get_week_range():
        """
            Return start and end datetime objects for each week.
        """

        # TODO: find better way to do this
        week_start_int = datetime.today().weekday()
        week_start = datetime.today() - timedelta(days=week_start_int)
        week_end_int = 7 - week_start_int
        week_end = datetime.today() + timedelta(days=week_end_int)

        return week_start, week_end

    @staticmethod
    def get_artists(df):

        df = df.copy()
        artists = [i.lower()
                   for i in df['show_artists'].tolist()
                   for j in i]

        return artists

class Playlist:
    """
        Searches artists scraped from Flagpole in Catalog for track ids.
        ConcertManager Observer
    """

    def __init__(self, concert_manager=None):
        self.concert_manager = concert_manager
        self.catalog = None
        self.artists = None

    def __call__(self):
        self.update_playlist()

    def update_playlist(self):
        self.artists = self.concert_manager.weekly_artists

    def query_catalog(self):
        pass

        # query catalog for artist names
        # get track_ids

class Catalog:
    """
        Class to create and update catalog of artist information.
        Playlist will use this catalog to get Artist and track id's.
        ConcertManager Observer
    """

# add all
    def __init__(self, concert_manager=None):

        self.concert_manager = concert_manager

        self.artists = None

    def __call__(self):
        """
            Update artist attribute with all artists from web scrape.
        """

        self.artists = self.concert_manager.artists
        spotify.get_catalog_data(self.artists)

    def load_records(self):
        """
            Load Artist records into Database. 
        """

        triage = []

        assert len(spotify.artist_data) == len(spotify.track_data)
     
        for artist, tracks in zip(spotify.artist_data, spotify.track_data):

            try:
                artist_exists = (db
                                .session.query(Artist.id)
                                .filter_by(spotify_id=artist['spotify_id']).scalar() is not None)
                # pdb.set_trace()
                if not artist_exists:
                    artist_rec = Artist(**artist)
                    db.session.add(artist_rec)

                for track in tracks:
                    track_exists = (db
                                    .session.query(Track.id)
                                    .filter_by(track_id=track['track_id']).scalar() is not None)
                                    
                    if not track_exists:
                            track_rec = Track(**track, artist=artist_rec)
                            db.session.add(track_rec)
                    
            except Exception as e:
                
                # log exception
                # add to triage table
                # Fails with UnboundLocalError
                triage.append({'artist': artist, 'track': track, 'Error': e})
                raise

        db.session.commit()

        # pdb.set_trace()
        return triage

def create_spotify():

    session = start_session()
    spotify = SpotipyAdapter(session=session).authenticate_user()
    return spotify

spotify = create_spotify()

    # def load_new_artists(self):
    #     """
    #         Load new artists from DataFrame
    #     """

    #     df = (df.pipe(self.clean_df_db_dups, 'catalog', db.engine)
    #         .pipe(to_sql, 'catalog', con=db.engine, if_exists='append', index_label='spotify_id'))

    # @staticmethod
    # def clean_df_db_dups(df, tablename, engine):
    #     """
    #     Remove rows from a dataframe that already exist in a database
    #     Required:
    #         df : dataframe to remove duplicate rows from
    #         engine: SQLAlchemy engine object
    #         tablename: tablename to check duplicates in
    #     Returns
    #         Unique list of values from dataframe compared to database table
    #     """

    #     catalog_df = pd.read_sql(tablename, index_col='spotify_id', con=engine)
    #     catalog_df.drop(axis=1, columns=['id'], inplace=True)
    #     new_df = (df[lambda x: x.merge(catalog_df,
    #                 left_index=True, right_index=True, how='left', indicator=True)
    #                 ['_merge'] == 'left_only'])


# class QueryTemplate:
#     def connect(self):
#         self.conn = None

#     def construct_query(self):
#         raise NotImplementedError()

#     def do_query(self):
#         self.conn.execute(self.query)

#     def format_results(self):
#         raise NotImplementedError()

#     def output_results(self):
#         raise NotImplementedError()

    # def process_format(self):
    #     self.connect()
    #     self.construct_query()
    #     self.do_query()
    #     self.format_results()
    #     self.output_results()
