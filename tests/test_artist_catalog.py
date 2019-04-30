"""
    Artist Catalog tests.
"""

import pytest

from betamax import Betamax
from betamax_serializers import pretty_json

#Setup Cassette configuration
Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
with Betamax.configure() as config:
    config.cassette_library_dir = 'tests/fixtures/cassettes'
    config.default_cassette_options['serialize_with'] = 'prettyjson'
    config.default_cassette_options['record'] = 'new_episodes'

from datetime import date, timedelta
from app.pipeline import data_collection

@pytest.mark.usefixtures('betamax_session')

@pytest.fixture
def athens_scraper(betamax_session):
    scraper = data_collection.Scraper(session=betamax_session)
    scraper.get_response()
    return scraper

# Factory as fixture
# TODO: currently not working
@pytest.fixture
def make_concert_record():

    def _make_concert_record(venue, date, artists):
        return data_collection.Concert(venue=venue, date=date, artists=artists)

    return _make_concert_record

@pytest.fixture
def concert_mgr():
    # concert_1 = make_concert_record('bar_1', date.today(),['name_1', 'name_2'])
    # concert_2 = make_concert_record('bar_2', date.today() - timedelta(days=7), ['name_3', 'name_4'])
    concert_1 = data_collection.Concert(
        venue='bar_1', date=date.today(), artists=['name_1', 'name_2'])
    concert_2 = data_collection.Concert(venue='bar_1', date=date.today(
    ) - timedelta(days=14), artists=['name_3', 'name_4'])
    return data_collection.ConcertManager(concerts=(concert_1, concert_2))

@pytest.fixture
def catalog_observer(concert_mgr):
    return data_collection.Catalog(concert_manager=concert_mgr)

def test_concert_records(make_concert_record):
    test_concert = make_concert_record('test', 'test', ['test'])

    assert test_concert.venue == 'test'
def test_weekly_concert_schedule(concert_mgr):
    print(f"Concerts: {concert_mgr.weekly_concert_schedule}")
    concert_mgr.create_weekly_schedule()
    print(f"Concerts: {concert_mgr.weekly_concert_schedule}")

    assert len(concert_mgr.weekly_concert_schedule) == 1

def test_concert_mgr_observers(concert_mgr, catalog_observer):
    concert_mgr.attach(catalog_observer)
    concert_mgr.create_weekly_schedule()
    catalog_observer.artists
    print(f"Artists: {catalog_observer.artists}")

    assert len(catalog_observer.artists) >= 1

def test_web_scraper(athens_scraper):
    concert_dict = athens_scraper.get_concerts()
    
    assert concert_dict is not None
