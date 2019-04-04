#TODO Where did this come from and what's it for?
# try:
#     import context 
# except ModuleNotFoundError:
#     import tests.context

import os

from PlaylistBuilder import DataManager, ConcertDataManager, DataFrameManager, PlaylistManager
from PlaylistBuilder import AuthorizationError, ArtistNotFoundError, BeautifulSoup, spotipy


from betamax import Betamax
from betamax_serializers import pretty_json

import unittest
from unittest.mock import patch, PropertyMock

#Setup Cassette configuration
Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
with Betamax.configure() as config:
    config.cassette_library_dir = 'tests/fixtures/cassettes'
    config.default_cassette_options['serialize_with'] = 'prettyjson'
    # TODO Fix session authentication cassette
    # config.define_cassette_placeholder('<AUTH_TOKEN>', api_token)

# TODO Testing Base Class with "Domain Specific Knowledge"

class DataManagerTestCase(unittest.TestCase):
    """
    A class used to test the Manager Base Class
    """

    def setUp(self):
        url =  'https://stackoverflow.com/questions/15115328/python-requests-no-connection-adapters'
        self.new_manager = DataManager(url=url)
        self.new_manager.start_session()

    def tearDown(self):
        self.new_manager.session.close()

    def test_get_response_case1(self):
        """ Case1: Good Response. """

        self.new_manager.get_response()

        self.assertTrue(self.new_manager.response.ok)

    def test_recv_message_case2(self):
        """Case2: Bad Response"""

        ## Need to test exception raised in app not requests
        ## or catch requests exception
        # Patch bad response to test how it's handled
        
        self.new_manager.get_response()

        self.assertTrue(self.new_manager.response.ok)

    def test_start_session_case1(self):
        """Case1: Session Exists"""

        self.assertIsNotNone(self.new_manager.session)

    def test_start_session_case3(self):
       """ Case3: Error Handling. """

       ## Response Status code
       self.assertRaises(AuthorizationError)

    #TODO Mock Data with timestamps
    def test_record_data(self):
        """ """
        #TODO mock dictionary
        pass
    
    def test_keep_time_case2(self):
        """ Case2: Expired data. """
        
        pass
        # self.assertGreater()

    def test_keep_time_case3(self):
        """ Case3: all data up to date. """

        #TODO Mock Data with timestamps
        pass

class ConcertDataManagerTestCase(unittest.TestCase):
    """
    A class used to test ConcertDataManager class.

    """
    
    def setUp(self):
        self.new_concerts = ConcertDataManager()

    def test_parse_concert_soup(self):
        """ Test Athens Web scraper. """

        # TODO use Unit test object
        concert = ConcertDataManager()
        recorder = Betamax(concert.data_mgr.session)
        with recorder.use_cassette('athens',
                                serialize_with='prettyjson',
                              record='new_episodes'):

            concerts = concert.parse_concert_soup()

            self.assertIsInstance(concerts, dict)

    
class PlaylistManagerTestCase(unittest.TestCase):
    """ A class used to test PlaylistManger objects. """

    def setUp(self):
        
        self.ply_manager = PlaylistManager()

        Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
        self.recorder = Betamax(self.ply_manager.session)

    def tearDown(self):
        self.ply_manager.session.close()

    def test_authenticate_spotify(self):
        """ Test Spotify API authentication code flow.  """
        # TODO Better docstring

        with self.recorder.use_cassette(cassette_name='spotify', serialize_with='prettyjson'):
             self.ply_manager.authenticate_spotify()
             self.assertIsNotNone(self.ply_manager.sp)
             self.assertIsInstance(self.ply_manager.sp, spotipy.client.Spotify)

    def test_get_playlists(self):
        """"""
        
        with self.recorder.use_cassette(cassette_name='Playlist Cassete',
            serialize_with='prettyjson'):
            self.ply_manager.authenticate_spotify()
            self.ply_manager.get_playlists()

            self.assertIs(type(self.ply_manager.usr_playlists), dict)
            self.assertIsNotNone(self.ply_manager.usr_playlists)

    def test_get_playlist_id(self):
        """ . """

        ply_name = "Music Midtown"
        with self.recorder.use_cassette(cassette_name='Playlist Cassete',
            serialize_with='prettyjson'):
            self.ply_manager.authenticate_spotify()
            self.ply_manager.get_playlists()
            self.ply_manager.get_playlist_id(name=ply_name)

            self.assertIsNotNone(self.ply_manager.ply_id)

    def test_get_artist_ids(self):
        """ """

        with self.recorder.use_cassette(cassette_name='ArtistID Cassete', serialize_with='prettyjson', record='new_episodes'):
            self.ply_manager.authenticate_spotify()
            self.ply_manager.get_artist_ids()

            self.assertIsNotNone(self.ply_manager.artist_ids)

    def test_get_top_tracks(self):
        """ """

        with self.recorder.use_cassette(cassette_name='Track Cassete', serialize_with='prettyjson', record='new_episodes'):
            self.ply_manager.authenticate_spotify()
            self.ply_manager.get_playlists()
            self.ply_manager.get_playlist_id("Music Midtown 2018")
            self.ply_manager.get_artist_ids()
            self.ply_manager.get_top_tracks()
 

if __name__ == '__main__':
    unittest.main(exit=False)
   


