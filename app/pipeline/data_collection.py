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
from app.pipeline import spotify_adapter

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
    """

    def __init__(self, concerts=None):
        self.observers = []
        self.concerts = concerts # for catalog - don't care about schedule
        self.concerts_df = None

        self.weekly_concert_df = None
        self.weekly_artists = None

    def attach(self, observer):
        self.observers.append(observer)

    def create_weekly_schedule(self):
        """
            Return list of concerts for the given week.

        """
        _, week_end = get_week_range()
        self.concerts_df = pd.DataFrame(self.concerts['concerts'])
        stage_df = self.concerts_df.copy()
        stage_df.loc[:, 'date_time'] = stage_df.loc[:, 'date_time'].apply(pd.Timestamp)
        stage_df = stage_df[stage_df['date_time'] < week_end]
        
        
        self.weekly_concert_df = stage_df
        self.weekly_artists = [j.lower() for i in stage_df['show_artists'].tolist() for j in i]
        self.update_observers()

    def update_observers(self):
        for observer in self.observers:
            observer()

# helper
def get_week_range():
    """
        Return start and end datetime objects for each week.
    """
    # TODO: find better way to do this
    week_start_int = date.today().weekday()
    week_start = date.today() - timedelta(days=week_start_int)
    week_end_int = 7 - week_start_int
    week_end = datetime.today() + timedelta(days=week_end_int)

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

class Catalog():
    """
        Class to create and update catalog of artist information.
        Playlist will use this catalog to get Artist and track id's.
        ConcertManager Observer
    """

    def __init__(self, concert_manager=None):
        self.concert_manager = concert_manager
        self.catalog_df = None

    def __call__(self):
        self.update_catalog()

    def update_catalog(self):
        df = self.concerts_df = self.concert_manager.concerts_df
        artists = [j for i in df['show_artists'].tolist() for j in i]
        # This is causing problems
        self.catalog_df = spotify_adapter.SpotipyAdapter().get_artist_info(artists=artists)
        unique_df = clean_df_db_dups(self.catalog_df, 'catalog', engine)
        unique_df.to_sql('catalog', con=engine, if_exists='append', index_label='spotify_id')

def clean_df_db_dups(df, tablename, engine):
    """
    Remove rows from a dataframe that already exist in a database
    Required:
        df : dataframe to remove duplicate rows from
        engine: SQLAlchemy engine object
        tablename: tablename to check duplicates in
    Returns
        Unique list of values from dataframe compared to database table
    """

    catalog_df = pd.read_sql(tablename, index_col='spotify_id', con=engine)
    catalog_df.drop(axis=1, columns=['id'], inplace=True)
    unique_df = df.loc[df.merge(
                    catalog_df, left_index=True, right_index=True, how='left', indicator=True)['_merge'] == 'left_only', :]
    return unique_df


# Database setup

from sqlalchemy import create_engine, Column, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

connection_str = 'sqlite:///app.db'
engine = create_engine(connection_str)

Base = declarative_base()

class Concert(Base):
    __tablename__ = 'concerts'
    
    id = Column(Integer, primary_key=True)
    artist = Column(String(20), nullable=False) 
    show_date = Column(String(20), nullable=False) 
    show_location = Column(String(20)) 
    show_info = Column(String(20))

    def __repr__(self):
        return f'<Concert {self.show_location}>'
    
class Catalog(Base):
    __tablename__ = 'catalog'
    
    id = Column(Integer, primary_key=True)
    spotify_id = Column(String(25), nullable=False, unique=True)
    artist_name = Column(String(20), nullable=False) 
    followers = Column(Integer, nullable=False) 
#     genres = Column(String(20)) 
    artist_track_ids = Column(String, nullable=False)
    
# Later
# class Track_Catalog(Base):
#     __tablename__ = 'track_catalog'
    
#     artist_track_ids = Column(String(20)
#     spotify_id = Column(Integer, primary_key=True)
#     artist_name = Column(String(20), nullable=False) 
#     followers = Column(String(20), nullable=False) 
#     genres = Column(String(20)) 
#     artist_track_ids = Column(String(20))
#     def __repr__(self):
#         return f'<Concert {self.show_location}>'




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
