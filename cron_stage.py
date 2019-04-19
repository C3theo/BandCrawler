"""
    Temp file to test cron job scheduling on Raspberry Pi.

"""
import pandas as pd
from sqlalchemy import create_engine
from config import Config
from concert_etl import DataFrameManager, ConcertDataManager


def del_staging_tbl(df, engine):
    """
        Delete staging table prior to first load. 
    """
    empty_df = df[0:0]
    empty_df.to_sql('staging', engine, index=True, if_exists='replace')


def main():
    concert_mgr = ConcertDataManager()
    concert_data = concert_mgr.parse_concert_soup()
    df_mgr = DataFrameManager(data=concert_data)
    stage_df = df_mgr.stage_df()

    connection_str = 'sqlite:///app.db'
    engine = create_engine(connection_str, echo=True)
    del_staging_tbl(stage_df, engine)
    stage_df.to_sql('staging', engine, index=True, if_exists='replace')

if __name__ == 'main':
    main()
