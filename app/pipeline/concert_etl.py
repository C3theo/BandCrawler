"""
Concert ETL Functions
"""

from bs4 import BeautifulSoup
from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import pdb
import random
import re
from datetime import datetime

import numpy as np
import pandas as pd
import os

from config import logger


class AuthorizationError(Exception):
    """ Authorization keys not Cached. """
    # TODO check if token cached - use spotipy function
    pass

class ArtistNotFoundError(Exception):
    """ Artist not on Spotify. """
    pass


class TimeoutHTTPAdapter(HTTPAdapter):
    # headers = {
    #     'user-agent': (
    #             'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    #             'AppleWebKit/537.36 (KHTML, like Gecko)'
    #             'Chrome/68.0.3440.106 Safari/537.36')}

    def send(self, *args, **kwargs):
        kwargs['timeout'] = 5
        return super(TimeoutHTTPAdapter, self).send(*args, **kwargs)
    
    # def add_headers(self, *args, **kwargs):
    #     kwargs['headers'] = self.headers
    #     return super()

class DataManager():
    """
    A class used to start sessions, get HTTP Response's ,and return Beautiful Soup
    objects.
    
    TODO: Refactor out beautifulsoup calls
    Used for Playlistmanager as well.
    Start new session?
    Lmits?
    Attributes:
        url
        session
        resonse
    """

    def __init__(self, url=None):

        self.url = url

        self.session = None
        self.response = None

    def start_session(self,
        retries=3,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504)):
        """ Create new Session object with user-agent headers, timeout, 
        and retry backoff."""

        headers = {
        'user-agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                'AppleWebKit/537.36 (KHTML, like Gecko)'
                'Chrome/68.0.3440.106 Safari/537.36')}
        
        retry = Retry(total=retries, read=retries, connect=retries,
            backoff_factor=backoff_factor, status_forcelist=status_forcelist)

        with Session() as self.session:
            adapter = TimeoutHTTPAdapter(max_retries=retry)
            self.session.headers.update(headers)
            self.session.mount('http:', adapter)
            self.session.mount('https://', adapter)
            return self

    def get_response(self):
        """
        Set response attr to response
        returned from URL.

        Args: url string
        """
        # TODO: add specific Exceptions
        # add headers to session in get

        try:
            self.response = self.session.get(self.url, stream=True)
            logger.info('Response from %s: \n %s', self.url, self.response)
            return self
        except Exception:
            logger.exception("Exception occured", exc_info=True)

    def get_soup(self):
        """ Set soup attr to Beautiful Soup Object using response.

        Args: 
            response.content: string
        """
        # TODO: add specific exceptions
        # No response content Exception
        try:
            return BeautifulSoup(self.response.content, 'lxml')
        except Exception:
            logger.exception("Exception occured", exc_info=True)

    def __repr__(self):
        return fr'DataManager({self.url})'

    def __str__(self):
        return fr'DataManager({self.url})'


class ConcertDataManager():
    """
    A class for managing the extraction and transformation of concert data
    from Beautiful Soup objects. Creates Dictionary of data from Beautiful Soup object.

        Attributes:
            url: string
            concert_soup: (BeautifulSoup) From DataManager

        Owns:
            DataManager
    """

    url = 'http://www.flagpole.com/events/live-music'

    def __init__(self):

        self.data_mgr = DataManager(url=ConcertDataManager.url)
        self.concert_soup = self.data_mgr.start_session().get_response().get_soup()
        # self.soup = soup

    def parse_concert_soup(self):
        """ Return dictionary of upcoming shows in Athens, Ga.

            Args:
                self.concert_soup

            Return:
                concert: dict
                    keys: Date, Event Count, Show Location, Artists, 
                    and Show information.
        """

        # logger.info(' Building Concert Dict. ')

        events = self.concert_soup.find(class_='event-list').findAll('h2')
        #TODO: change to list of dicts for pandas
        concert_dict = {}
        for event in events:

            concert_date = event.text
            concert_date = fr'{concert_date} {datetime.today().year}'
            concert_datetime = datetime.strptime(concert_date, '%A, %B %d %Y')

            event_count = event.findNext('p')
            venues = event.findNext('ul').findAll('h4')
            concert_dict[concert_date] = {'datetime': concert_datetime,
                                          'Event Count': event_count.text}
            # Event Count for Data Audit
            concert_dict[concert_date]['Shows'] = []
            for venue in venues:
                info = venue.findNext('p')
                bands = info.fetchNextSiblings()
                names = [each.strong.text.replace('\xa0', '')
                         for each in bands if each.strong]
                concert_dict[concert_date]['Shows'].append({'ShowLocation': venue.text,
                                                            'Artists': names,
                                                            'ShowInfo': info.text})

        #TODO: add ability to log range of concert dates
        # logger.info('Concerts found for these dates)
        #TODO: pprint logs
        # logger.info('Concerts Found: \n\n %s', concert_dict)

        return concert_dict

    def __repr__(self):
        return fr'ConcertManager({self.url})'

    def __str__(self):
        return fr'ConcertManager({self.url})'


class ConcertETLManager():
    """
        A class used to transform a dictionary and return DataFrame Objects.

        Attributes:
            data: dict       
    """

    def __init__(self, data=None):
        self.concert_mgr = ConcertDataManager()
        self.data = self.concert_mgr.parse_concert_soup()

        # self.data = data
        # TODO: add check for if data is not none/ready
        # handled by luigi
    def key_to_front(self, df):
        """
        Rearrange dataframe columns so new surrogate key is first.

        Args: df
        """
        columns = list(df.columns)
        columns.insert(0, columns.pop())

        return df[columns]

# Admin functions
    def create_etl_id(self):
        """
        Generate ETLID# used for static ETL gate ID's.
        """
        # use prefix function for col name
        return random.randint(a=1000, b=9999)

    def create_etl_df(self):
        """
        Create Empty ETLID DataFrame with column names.
        Used to keep track of existing tables.
        """
        return pd.DataFrame(columns=['TableName', 'ETLID'])

    def update_etl_df(self, df, tbl_name, etl_id):
        """
        Update ETL DataFrame if Table Name and ID not in DataFrame.

        Args:
            df
            tbl_name
            etl_id
        """
        # TODO: figure out how to update existing tables

        # if etl_df.isin({'ETLID':[etl_id]}):
        pass

    # TODO:
    # check foreign key generation practices
    def set_gate_index(self, df, primary_id='primary_key'):
        """
        Set primary index label.
        """

        df.set_index(primary_id, verify_integrity=True, inplace=True)

        return df
    def stage_df(self):
        """
            Return Staging Dataframe

            Arguments: self.data

            Return: stage_df
        """
        # TODO: Refactor using JMESPATH
        schema = {'artist': [],
                  'show_date': [],
                  'show_location': [],
                  'show_info': []}
                #   ['artist', 'show_date', 'show_location', 'show_info']

        for date, events in self.data.items():
            for show in events['Shows']:
                for artist in show['Artists']:
                    schema['show_date'].append(date)
                    schema['show_location'].append(show['ShowLocation'])
                    schema['show_info'].append(show['ShowInfo'])
                    schema['artist'].append(artist)

        df = pd.DataFrame(data=schema)
        df.loc[:, 'etl_id'] = 1000
        primary_id = 'source_row_id'
        #TODO: add to gate index if this is done for all gates
        df[primary_id] = df.index
        stage_df = self.key_to_front(df)
        # stage_df = self.set_gate_index(stage_df, primary_id='source_row_id')
        # save column for data lineage
        return stage_df

    def gate1_df(self, df):
        """ 
        Return Spotify DataFrame.

        Args: df

        """

        gate1_df = df.copy()
     
        gate1_df.drop(
            columns=['show_date', 'show_location', 'show_info'], inplace=True)
        gate1_df.drop_duplicates(subset='artist', inplace=True)
        gate1_df.loc[:, "spotify_key"] = gate1_df['etl_id'] + \
            gate1_df.iloc[::-1].index
        gate1_df.loc[:, "etl_id"] = 4000
        gate1_df = gate1_df[['spotify_key', 'source_row_id', 'artist', 'etl_id']]

        return gate1_df

    def gate2_df(self, df):
        """
        Return Concert Table DataFrame.

        Args: df

        """

        gate2_df = df
        gate2_df.ShowDate = pd.to_datetime(gate2_df.ShowDate)
        days = gate2_df.ShowDate.apply(lambda x: x.day).astype(str)
        key = gate2_df.index.astype(str)
        key_col = key + days
        key_col = key_col.astype(int)
        gate2_df['ShowKey'] = key_col
        gate2_df.loc[:, "ETLID"] = 2000
        gate2_df = gate2_df[['ShowKey', 'SourceRowID',
                             'ShowDate', 'ShowLocaton', 'ETLID']]

        return gate2_df

    def gate2a_df(self, df):
        """
        Return Upcoming Shows DataFrame.

        Args: df gate2 DataFrame

        Returns:
        """

        today = datetime.datetime.today()
        current = df[df['ShowDate'] > today]
        end = ', '.join(list(current.columns)[:-1])
        gate2a_df = df[fr'{list(current.columns)[-1]}, {end}']

        return gate2a_df

    def record_data(self, data):
        """
        Return multi-indexed dataframe of all collected concert data.

        Args: data

        Returns:
        """

        # Where, When, Who, How Much?
        # Columns: Venue, Showtime, Artist, Price
        # Stores All Data
        # Not really necessary if just trying to keep track of artists in playlist

        labels = ['Venue', 'Artists', 'Price']
        conc_df = pd.DataFrame()

        for date in data:
            concerts = data[date]['Shows']
            df = pd.DataFrame(data=concerts)

            tuples = list(zip([date] * 3, list(labels)))
            index = pd.MultiIndex.from_tuples(
                tuples, names=['Date', 'Details'])
            df.columns = index

            conc_df = pd.concat([conc_df, df], axis=1)

        return conc_df

    def dates_artists(self, data):
        """
        Return dataframe of artists indexed by show date.

        Args: data

        Returns:

        """

        date_artists = []
        for date, event in data.items():
            artists = [art for show in event['Shows'] for art in show['Artists']
                       if art.lower() != 'open mic']
        if artists:
            date_artists.append({date: artists})

        # TODO: make helper function for growing dfs from list
        da_df = pd.DataFrame()
        for show_date in date_artists:
            df = pd.DataFrame(data=show_date)
            da_df = pd.concat([df, da_df], axis=1)

        return da_df

    def artists_df(self, data):
        """
        Return dataframe of list of showdates indexed by artists.

        Args: data
        """

        # Unique set of Artists
        artists = {each for k, v in data.items()
                   for show in v['Shows']
                   for each in show['Artists']}
        artists = sorted(list(artists))

        # Lists of all Show Dates for each Artist
        a_dict = {each: [] for each in artists}
        for date, event in data.items():
            for show in event['Shows']:
                for artist in show['Artists']:
                    a_dict[artist].append(date)

        df_data = {'Artists': list(a_dict.keys()),
                   'Dates': list(a_dict.values()),
                   'Spotify': False,
                   'Future Shows': False}
        df = pd.DataFrame(data=df_data)
        df = df.astype({'Artists': str,
                        'Dates': list,
                        'Spotify': bool,
                        'Future Shows': bool})

        return df

    def __repr__(self):
        return fr'DataFrameManager()'

    def __str__(self):
        return fr'DataFrameManager()'\

def df_to_db(df):
    pass
