"""
    Artist Catalog tests.
"""

import pytest
from datetime import date, timedelta
from app.pipeline import data_collection

def test_discovered():
    assert 1

@pytest.fixture
def concert_mgr():
    concert1 = data_collection.Concert(venue='bar_1', date=date.today(),
                       artists=['name_1', 'name_2'])
    last_week_date = date.today() - timedelta(days=7)
    concert2 = data_collection.Concert(venue='bar_1', date=last_week_date,
                       artists=['name_1', 'name_2'])

    return data_collection.ConcertManager(concerts=(concert1, concert2))

def test_weekly_concert_schedule(concert_mgr):
    week_concerts = concert_mgr.weekly_concert_schedule()
    assert len(week_concerts) == 1
