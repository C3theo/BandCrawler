"""
Concert ETL Classes
"""

import numpy as np
import pandas as pd
import os



# Singleton
class Concert_Manager:

    concerts = []

    def __init__(self):

        self.week = week
    
    def create_weekly_schedule():

        return week_concerts

class Artist(dict):

    def__init__(self):

        self.name_spotify_id = dict()
        self.top_5_songs = dict() 

# Singleton
class Playlist:

    last_updated = None

    spotify_id = ''

    artists = artist

    self.schedule = Concert_Manager

    def get_artists()
        """
            Get list of Artist Objects for next week.
        """

class DatabaseTemplate:
    def connect():

    def query():




# Template for Concert & Spotify Dataframe Transformations
class PandasETLManager:
    """
        A class used to manage DataFrame Objects.

        Attributes:
            data: dict       
    """

    def __init__(self, data=None):

    def key_to_front(self, df):
        """
        Rearrange dataframe columns so new surrogate key is first.

        Args: df
        """
        columns = list(df.columns)
        columns.insert(0, columns.pop())

        return df[columns]

    def create_etl_id(self):
        """
        Generate ETLID# used for static ETL gate ID's.
        """
        # use prefix function for col name
        return random.randint(a=1000, b=9999)

    def create_etl_df(self):
        """
        Create Empty ETLID DataFrame with column names.
        Used to keep track of ETL Gate Dataframes Dataframes.
        """
        # Should you keep track of weekly updates. Check ETL best practes website

        # TODO: Refactor
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
    
    def stage_df():
        raise NotImplementedError()

class ConcertETL():

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

