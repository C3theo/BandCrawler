"""
    Temp file to test cron job scheduling on Raspberry Pi.

"""
import pandas as pd
from sqlalchemy import create_engine
from config import Config
from concert_etl import DataFrameManager, ConcertDataManager

def main():
    connection_str = 'sqlite:///app.db'
    engine = create_engine(connection_str, echo=True)

    concert_mgr = ConcertDataManager()
    concert_data = concert_mgr.parse_concert_soup()
    df_mgr = DataFrameManager(data=concert_data)
    stage_df = df_mgr.stage_df()
    stage_df.to_sql('staging', engine, index=True)

if __name__ == 'main':
    main()
