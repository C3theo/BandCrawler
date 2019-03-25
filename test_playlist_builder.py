# try:
#     import context 
# except ModuleNotFoundError:
#     import tests.context

import os

from PlaylistBuilder import Manager, ConcertManager, PlaylistManager
from PlaylistBuilder import AuthorizationError, ArtistNotFoundError, BeautifulSoup, spotipy
# import PlaylistBuilder

from betamax import Betamax
from betamax_serializers import pretty_json

import unittest
from unittest.mock import patch, PropertyMock

Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
with Betamax.configure() as config:
    config.cassette_library_dir = 'tests/fixtures/cassettes'
    config.default_cassette_options['serialize_with'] = 'prettyjson'
    # config.define_cassette_placeholder('<AUTH_TOKEN>', api_token)

class ManagerTestCase(unittest.TestCase):
    """Tests for Base Manager Class"""

    def setUp(self):
        self.new_manager = Manager()
        self.new_manager.start_session()

    def tearDown(self):
        self.new_manager.session.close()

    def test_get_response_case1(self):
        "Case1: Good Response"

        url =  'https://stackoverflow.com/questions/15115328/python-requests-no-connection-adapters'
        response = self.new_manager.get_response(url)
        self.assertTrue(response.ok)

    def test_recv_message_case2(self):
        "Case2: Bad Response"
        url =  'BAD SITE'
        response = self.new_manager.get_response(url)
        self.assertFalse(response.ok)

    def test_start_session_case1(self):
        "Case1: Session Exists"
        self.assertIsNotNone(self.new_manager.session)

    def test_start_session_case3(self):
        "Case3: Error Handling"
        ## Response Status code
        self.assertRaises(AuthorizationError)

    #TODO Mock Data with timestamps
    def test_record_data(self):
        #TODO mock dictionary
        pass
    
    def test_keep_time_case1(self):
        "Case1: today attribute exists"

        # TODO mock object with times
        # print(f'\n{self.new_manager.today}')
        self.assertIsNotNone(self.new_manager.today)
    
    def test_keep_time_case2(self):
        "Case2: Expired data."
        
        pass
        # self.assertGreater()

    def test_keep_time_case3(self):
        "Case3: all data up to date."
        #TODO Mock Data with timestamps
        pass

class ConcertManagerTestCase(unittest.TestCase):
    """
    ConcertManager Tests

    """
    
    def setUp(self):
        self.new_concerts = ConcertManager()
        self.new_concerts.start_session()

    def tearDown(self):
        self.new_concerts.session.close()
    
    def test_start_session_case1(self):
        "Session Started"

        recorder = Betamax(self.new_concerts.session)

        with recorder.use_cassette('arist-ids',
                                serialize_with='prettyjson',
                              record='new_episodes'):

            self.new_concerts.get_response()
            self.assertIsNotNone(self.new_concerts.session)
            self.assertEqual(self.new_concerts.response.ok, True)

    def test_start_session_case2(self):
        "Case2: Session Authentication"
        # self.assertListEqual(self.new_concerts.session.auth, self.api_dict)
        pass
    
    def test_concert_found(self):
        "Website Crawler exists"
        #TODO choose randomly from list,
        ## Check Null condition
        ## broken right now
        recorder = Betamax(self.new_concerts.session)
        with recorder.use_cassette('bonnaroo',
                                serialize_with='prettyjson',
                              record='new_episodes'):
            self.new_concerts.get_response()
            self.new_concerts.get_concert_soup()
            # self.assertEqual(self.new_concerts.url, 'http://www.flagpole.com/events/live-music')
            self.assertEqual(self.new_concerts.url, 'https://www.bonnaroo.com/lineup/interactive/')
            # ONLY TESTS WHETHER CONCERTMANAGER HAS CORRECT URL ATTRIBUTE

    def test_get_response_case1(self):

        recorder = Betamax(self.new_concerts.session)
        with recorder.use_cassette('RESPONSE',
                                serialize_with='prettyjson',
                              record='new_episodes'):

            self.new_concerts.get_response()
            self.assertIsNotNone(self.new_concerts.response)

    def test_concert_soup(self):
        recorder = Betamax(self.new_concerts.session)
        with recorder.use_cassette(cassette_name='Concerts',
                    serialize_with='prettyjson', record='new_episodes'):
            self.new_concerts.get_response()
            self.new_concerts.get_concert_soup()
            self.assertIsNotNone(self.new_concerts.soup)
            self.assertIsInstance(self.new_concerts.soup, BeautifulSoup)
    
    def test_athens_concerts(self):
        "Test scraping functionality for Athens concerts"

        concert = ConcertManager(concert='Athens')
        concert.start_session()
        recorder = Betamax(concert.session)
        with recorder.use_cassette('athens',
                                serialize_with='prettyjson',
                              record='new_episodes'):
            concert.get_response()
            concert.get_concert_soup()
            concerts = concert.athens_concerts()

            self.assertIsInstance(concerts, dict)
    
    def test_athens_lineup(self):
        pass

    
    def test_bonnaroo_lineup(self):
        
        recorder = Betamax(self.new_concerts.session)
        with recorder.use_cassette('bonnaroo',
                                serialize_with='prettyjson',
                              record='new_episodes'):
            self.new_concerts.get_response()
            self.new_concerts.get_concert_soup()
            self.assertEqual(self.new_concerts.url, 'https://www.bonnaroo.com/lineup/interactive/')

            self.new_concerts.get_concert_soup()
            concerts = self.new_concerts.athens_concerts()

            self.assertIsInstance(concerts, dict)
        

    # def test_concert_response(self):
    #     with self.recorder.use_cassette(cassette_name='Concert Cassete', serialize_with='prettyjson', record='new_episodes'):
    #         self.new_concerts.get_concert_html()

    #     # print(type(self.new_concerts.response))
    #     self.assertIsNotNone(self.new_concerts.response)
    #     # self.assertIsInstance(self.new_concerts.response, PlaylistBuilder.requests.models.Response)


    # def test_find_artists(self):
    #     with self.recorder.use_cassette(cassette_name='Concert Cassete', serialize_with='prettyjson', record='new_episodes'):
    #         self.new_concerts.get_concert_html()
    #         self.new_concerts.get_concert_soup()
            # self.new_concerts.search()

        # self.assertIs(type(self.new_concerts.artists), set)

        
class PlaylistManagerTestCase(unittest.TestCase):

    def setUp(self):
        
        con_manager = ConcertManager(concert='Athens')
        self.ply_manager = PlaylistManager(con_manager)
        self.ply_manager.start_session()

        Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
        self.recorder = Betamax(self.ply_manager.session)

    def tearDown(self):
        self.ply_manager.session.close()

    def test_authenticate_spotify(self):

        with self.recorder.use_cassette(cassette_name='spotify', serialize_with='prettyjson'):
             self.ply_manager.authenticate_spotify()
             self.assertIsNotNone(self.ply_manager.sp)
             self.assertIsInstance(self.ply_manager.sp, spotipy.client.Spotify)

    def test_get_playlists(self):
        "Returns list of user playlist names"
        
        with self.recorder.use_cassette(cassette_name='Playlist Cassete',
            serialize_with='prettyjson'):
            self.ply_manager.authenticate_spotify()
            self.ply_manager.get_playlists()

            self.assertIs(type(self.ply_manager.usr_playlists), dict)
            self.assertIsNotNone(self.ply_manager.usr_playlists)

    def test_get_playlist_id(self):

        ply_name = "Music Midtown"
        with self.recorder.use_cassette(cassette_name='Playlist Cassete',
            serialize_with='prettyjson'):
            self.ply_manager.authenticate_spotify()
            self.ply_manager.get_playlists()
            self.ply_manager.get_playlist_id(name=ply_name)

            self.assertIsNotNone(self.ply_manager.ply_id)

            

#     # @unittest.skip('')
#     def test_get_playlist_id(self):
#         ply_name = "Music Midtown 2018" 
#         with self.recorder.use_cassette(cassette_name='PlaylistID Cassete', serialize_with='prettyjson'):
#             self.ply_manager.authenticate_spotify()
#             self.ply_manager.get_playlists()
#             self.ply_manager.get_playlist_id(name=ply_name)
#         self.assertIsNotNone(self.ply_manager.ply_id)
#         # self.AssertEqual(self.ply_manager.ply_id, " ")
#  # self.assertDictContainsSubset(a, b)self.ply_manager.ply_id
#     # @unittest.skip('')
#     def test_get_artist_ids(self):
#         with self.recorder.use_cassette(cassette_name='ArtistID Cassete', serialize_with='prettyjson', record='new_episodes'):
#             self.ply_manager.authenticate_spotify()
#             self.ply_manager.get_artist_ids()

#         self.assertIsNotNone(self.ply_manager.artist_ids)

#     @unittest.skip('')
#     def test_get_top_tracks(self):
#         with self.recorder.use_cassette(cassette_name='Track Cassete', serialize_with='prettyjson', record='new_episodes'):
#             self.ply_manager.authenticate_spotify()
#             self.ply_manager.get_playlists()
#             self.ply_manager.get_playlist_id("Music Midtown 2018")
#             self.ply_manager.get_artist_ids()
#             self.ply_manager.get_top_tracks()
 

if __name__ == '__main__':
    unittest.main(exit=False)
    # concert_suite = unittest.TestLoader().loadTestsFromTestCase(ConcertManagerTestCase)
    # unittest.TextTestRunner(verbosity=2).run(concert_suite)

    # ply_suite = unittest.TestLoader().loadTestsFromTestCase(PlaylistManagerTestCase)
    # unittest.TextTestRunner(verbosity=2).run(ply_suite)

    # def tearDownClass(cls):
    #     pass
    #     # print('Cleaning up Playlist Tests')

    # @classmethod
    #print(f'\n\n===PlaylistManager Results===\n\nArtist IDs: {cls.manager.artist_ids}\n\n')
    #print(f'\n\nUser Playlists: {cls.manager.usr_playlists}')
    
    # def test_authenticate_spotify(self):
    #     self.mock_spotify
    #     self.ply_manager.authenticate_spotify()

    #     #chck for cached auth
    #     self.assertEqual()

    #     self.assertIsNotNone(self.manager.token)
    #     mock_spotify.assert_called_with(auth=self.manager.token)

    # @unittest.skip('Not Ready')
    # @patch('PlaylistBuilder.spotipy.Spotify.current_user_playlists')
    # def test_get_playlists(self, mock_user_ply):

    #     mock_user_ply.return_value = ['Athens', 'Music Midtown', 'Atlanta']
    #     self.manager.get_playlists()
    #     self.assertIsNotNone(self.manager.usr_playlists)
    #     self.assertEqual(mock_user_ply(), self.manager.usr_playlists) #Could be sorted differently

    # @patch('PlaylistBuilder.PlaylistManager', spec=PlaylistBuilder.PlaylistManager)
    # def test_get_playlist_id(self, mock_manager):

    #         ply_name = 'Music Midtown'
    #         print(mock_manager.username.return_value)       
            # print(self.manager.usr_playlists)
            # print(dir(self.manager))
            # self.manager.get_playlist_id(ply_name)
            # self.assertIsNotNone(self.manager.ply_id, msg='Playlist Not Found')
            # Attribute Error
            # self.assertIn(ply_name, self.manager.usr_playlists())

# *** IndexError: list index out of range
# RETURNS
# <__main__.PlaylistManager object at 0x0000024522E10278>
# 'spotify:artist:70kkdajctXSbqSMJbQO424'
# AttributeError: 'PlaylistManager' object has no attribute 'playist_id'
# error code 4 No internet connections
    # @unittest.skip('Not Ready')
    # def test_get_artist_ids(self):

    #     self.manager.get_artist_ids()
    #     self.assertIsNotNone(self.manager.artist_ids)
        # self.assert

## Needs a PlaylistManager Object with mocked attributes
# username
# ply_id
# artist_ids
## New Mock Object
## Existing object
## Patch attributes into set up class

    # @patch('PlaylistBuilder.PlaylistManager', spec=True)
    # @unittest.skip('Not Ready')
    # def test_add_top_five_songs(self, mock_ply):

    #     mock_ply.artists = self.manager.artists

    #     real = PlaylistBuilder.PlaylistManager()

        # print(dir(real))
        # print(real.username)


        # print(dir(mock_ply))
        # print(mock_ply.artists)

        # ply_obj = mocked_ply.return_value

        # ply_obj.ply_id ='6xaciHvPA3swR27sXfBEH0' #Music Midtown Playlist 
        # # mocked_manager.ply_id = 'TEST'
        # ply_obj.artist_ids = ['spotify:artist:53XhwfbYqKCa1cC15pYq2q', 'spotify:artist:13y7CgLHjMVRMDqxdx0Xdo',\
        #                                 'spotify:artist:4UXqAaa6dQYAk18Lv7PEgX', 'spotify:artist:246dkjvS1zLTtiykXe5h60', \
        #                                 'spotify:artist:21egYD1eInY6bGFcniCRT1']                                             
                # print(real, {real.play_id.return_value})
            # real = PlaylistBuilder.PlaylistManager()
            ## Duplicate tracks
            # self.manager.


