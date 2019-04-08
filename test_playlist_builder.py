#TODO Where did this come from and what's it for?
# try:
#     import context 
# except ModuleNotFoundError:
#     import tests.context

import os
import unittest
from unittest.mock import PropertyMock, patch

from betamax import Betamax
from betamax_serializers import pretty_json

from PlaylistBuilder import (ArtistNotFoundError, AuthorizationError,
                             BeautifulSoup, ConcertDataManager,
                             DataFrameManager, DataManager, PlaylistManager,
                             spotipy, oauth, Session)

#Setup Cassette configuration
Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
with Betamax.configure() as config:
    config.cassette_library_dir = 'tests/fixtures/cassettes'
    config.default_cassette_options['serialize_with'] = 'prettyjson'
    config.default_cassette_options['record'] = 'new_episodes'
    # TODO Fix session authentication cassette
    # config.define_cassette_placeholder('<AUTH_TOKEN>', api_token)

# TODO Testing Base Class with "Domain Specific Knowledge"

class DataManagerTestCase(unittest.TestCase):
    """
    A class used to test the Manager Class
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

        recorder = Betamax(self.new_concerts.data_mgr.session)
        with recorder.use_cassette('athens',
                                serialize_with='prettyjson',
                              record='new_episodes'):

            self.new_concerts = self.new_concerts.parse_concert_soup()

            self.assertIsInstance(self.new_concerts, dict)

class DataFrameManagerTestCase(unittest.TestCase):

        def setUp(self):
        
            self.dataframe_mgr = DataFrameManager()

            self.recorder = Betamax(self.dataframe_mgr.concert_mgr.data_mgr.session)
            with self.recorder.use_cassette('athens',
                                serialize_with='prettyjson',
                              record='new_episodes'):
                              self.dataframe_mgr = DataFrameManager()

        def test_stage_df(self):

            df = self.dataframe_mgr.stage_df()

            self.assertIsNotNone(df)


class PlaylistManagerTestCase(unittest.TestCase):
    """ A class used to test PlaylistManger objects. """

    def setUp(self):
        
        self.ply_manager = PlaylistManager(ply_name='Test')
        self.recorder = Betamax(self.ply_manager.session)

    def tearDown(self):
        self.ply_manager.session.close()

# auth_url = self.client_mgr.get_authorize_url()
# self.response_code = self.client_mgr.parse_response_code(auth_url)

    def test_create_auth(self):
        """ Test SpotifyOaAuth creation."""
        # TODO Better docstring
        # with self.recorder.use_cassette(cassette_name='Authenticate Spotify'):
        self.ply_manager.create_spotify_auth()
        
        #SPOTIFYOAUTH OBJECT CREATED
        self.assertIsInstance(self.ply_manager.client_mgr,
            spotipy.oauth2.SpotifyOAuth)
        #SCOPE ATTR SET CORRECTLY
        self.assertEqual(self.ply_manager.client_mgr.scope,
            self.ply_manager.scope)
        #VALID REDIRECT URI
        redirect_uri = self.ply_manager.client_mgr.redirect_uri
        self.assertEqual(redirect_uri,
            self.ply_manager.redirect_uri)

    # @patch.object(Session, 'get')
    def test_create_auth_user(self):
        """ Test SpotifyOauth Authorization URL from user."""

        # mock_response.side_effect = print(mock_response.call_args)

        self.ply_manager.create_spotify_auth()
        #VALID PAYLOAD TYPE FOR GET
        # mock_encode.assert_called_with(mock_payload)
        #VALID AUTHORIZATION URL TO USER
            #NOT https://accounts.spotify.com/authorize?
            #TODO: MOCK
        url = self.ply_manager.client_mgr.get_authorize_url()
        self.assertNotEqual(url,
            oauth.SpotifyOAuth.OAUTH_AUTHORIZE_URL+'?')
        #VALID AUTHORIZATION URL FROM USER: CONTAINS HASH FRAGMENT
            # check sesson.get return value
            # ACCESS_TOKEN
            # TOKEN_TYPE = BEARER
        # self.assertEqual(self.ply_manager.session.headers, '')
        mock_resp_auth_url = 'https://www.google.com/?code=AQBK6qfGAr1FcUPvHItgDLornIH3web0Qt872xqjQ8iM5KqUGiD64vqO_InvG6_3l9P6O6hRwg5pDnxdDjyk4fNWKrZFAAeITBh0WhvUVQv-1_zdK1I_cdcjUZFDfUrfzeKi3FBdQcIgUPH5VA1yLMSNjNHA0o3eodqVT_4dhfwqyoVG0zxkuyas8NO9cermW_FWakhRvqAASAyBJanyfKYWPgnWBOXFiDsZ8XZH1HEMZN2n-1wLdexZjMecfHs'
        
        # mock_resp_auth_url = 'https://www.google.com/?code=AQBV1I6b05DaA79fhBeUuqCCr8a3gC4DEjsLrJk_iSwf5wcnxwud3Z8EshinuFlAbxSDbeY3zhWprcCnCF6hlRoH9I8FeO3Pj8BSg0MeTRygZZ5rVVasCKeXAfkbEj8BYUuCuluxbbdjsMA6IqlBNhRyoVpdQd53_cgqvHCtCZq5OmVTXLcIapJGbtJy_F-Yw2kub-I7KXcYBX3eAVWrQ1kFmEbzejChuAvMRYrsj23fXR8Zz2W6BUasNL84hmk'
# https://accounts.spotify.com/login?continue=https%3A%2F%2Faccounts.spotify.com%2Fauthorize%3F%253CMagicMock%2520name%3D%2527urlencode%2528%2529%2527%2520id%3D%25272456521001840%2527%253E
        #missing client_id
        #VALID RESPONSE FROM AUTHORIZATION URL
        # mock_parse.assert_called_with(mock_auth_url.call_args)

        # self.assertIsNotNone(self.ply_manager.response_code)

# GET https://accounts.spotify.com/authorize
# response_type

    @patch.object(oauth.urllibparse, 'urlencode')
    
    def test_create_auth_token(self):
        """Test Auth Token created and valid """
        self.ply_manager.create_spotify_auth()
        
        mock_payload = {'client_id': self.ply_manager.client_id, #* mock_encode.call_args[0]
        'response_type': 'code', 'redirect_uri':
        'https://www.google.com/', 'scope':
        'playlist-modify-private playlist-read-private'}
        #VALID TOKEN CACHE PATH
        self.assertEqual(os.listdir(self.ply_manager.client_mgr.cache_path),
            os.listdir(r"C:\Users\TheoI\OneDrive\Documents\Python Projects\BandCrawler\__pycache__"))
        #TOKEN EXISTS
        token_info = self.ply_manager.token
        self.assertIsNotNone(token_info)
        #TOKEN SCOPE GIVES MAX ACCESS
        self.assertTrue(self.ply_manager.client_mgr._is_scope_subset(self.scope,
            token_info['scope']))

    def test_create_spotify(self):

        # SPOTIFYOAUTH object
        self.assertIsInstance(self.ply_manager.sp.client_credentials_mgr,
            spotipy.oauth2.SpotifyOAuth)

        #VALID SCOPE
        self.assertEqual(self.ply_manager.sp.client_credentials_mgr.scope,
            self.ply_manager.scope)
        # VALID TOKEN CACHE PATH
        self.assertEqual(self.ply_manager.sp.client_credentials_mgr.cache_path,
        r"C:\Users\TheoI\OneDrive\Documents\Python Projects\BandCrawler\__pycache__")
        
        # TOKEN EXISTS
        self.assertIsNotNone(self.ply_manager.sp.client_credentials_mgr.token)
        
        token_info = self.ply_manager.sp.client_credentials_mgr.token
        # TOKEN SCOPE GIVES MAX ACCESS
        self.assertTrue(self.ply_manager.sp.client_credentials_mgr._is_scope_subset(self.scope,
            token_info['scope']))

        # REFRESH_TOKEN



        #SPOTIFY OBJECT
        self.assertIsInstance(self.ply_manager.sp,
            spotipy.client.Spotify)
        

    def test_create_playlist(self):
            """ Test playlist created.
                POST()
                Requires token
                Response code
            """

            with self.recorder.use_cassette(cassette_name='Playlist Create'):
                self.ply_manager.authenticate_spotify()
                self.ply_manager.create_playlist()


                self.assertIsNotNone(self.ply_manager.sp)
                self.assertIsInstance(self.ply_manager.sp, spotipy.client.Spotify)
                self.assertIsNotNone(self.ply_manager.client_mgr.scope)


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
