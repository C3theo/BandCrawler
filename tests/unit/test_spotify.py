# """Tests for Spotify Playlist Management. """

# import time

# pylint:disable=redefined-outer-name
# import pytest

# from playlist_builder import PlaylistManager, oauth

# # TODO: add betmax
# # take out real token hashes

# @pytest.fixture
# def playlist_mgr():
#     """Setup Playlist Manger object """
#     return PlaylistManager(playlist='Test')

def test_discover():
    assert 1

# @pytest.fixture
# def spotify_playlist(playlist_mgr):
#     """
#     Spotify Playlist Fixture
#     Calls all methods to set ply_id attr.
#     """
#     playlist_mgr.create_client_mgr()
#     playlist_mgr.get_auth_token()
#     playlist_mgr.create_spotify()
#     playlist_mgr.create_playlist()
#     playlist_mgr.get_playlists().get_playlist_id()

#     yield playlist_mgr

#     playlist_mgr.sp.user_playlist_unfollow(
#         playlist_mgr.username, playlist_mgr.ply_id)


# def test_get_playlist_id(spotify_playlist):
#     """
#     """

#     assert spotify_playlist.ply_id

# # TODO:
# # these all are testing what PlaylistManager object was called with
# # use mock PlaylistManager object w/ spec
# # params with mock objects
# # testing exception handling with spotipy oauth
# # use params here


# token_expired = {'access_token': 'BQDeIu9jE31agz-aZPQlQyyR5wZ9vo-lwzyPfMzUkDADhld5i1NlEmycGSYWTZcK1UsBTL'
#                  'WsL_ckD8GgNGCJuX_b1l5tG0s0ZzDXFjGSEaa5g6FFxBddMFwdtnf-wx95hqn2mMGd148JbSD'
#                  'WoUJIG6E6_QN9ob2Xql_M6I1rJyZ5uR_LWgnkGZsFGfBiXYI',
#                  'token_type': 'Bearer',
#                  'expires_in': 3600,
#                  'refresh_token': 'AQAljYnnDvfv0GBnLKGWfZhMZs0mOflAvs4ZMiejKBbCOVZUTCkL0Svzu12vBMveNRygOnq'
#                  '_HjPzpZqJHMTBHbBb9U9w5UlP_clrK0JGkdJ04UpdJMizDUuSRpyvL0tFWEvV1g',
#                  'scope': 'playlist-modify-private playlist-read-private',
#                  'expires_at': 1554960789}

# token_current = {'access_token': 'BQDeIu9jE31agz-aZPQlQyyR5wZ9vo-lwzyPf'
#                                  'MzUkDADhld5i1NlEmycGSYWTZcK1UsBTLWsL_ckD8GgNGCJuX'
#                                  '_b1l5tG0s0ZzDXFjGSEaa5g6FFxBddMFwdtnf-wx95hqn2mMGd148JbSDWo'
#                                  'UJIG6E6_QN9ob2Xql_M6I1rJyZ5uR_LWgnkGZsFGfBiXYI',
#                  'token_type': 'Bearer',
#                  'expires_in': 3600,
#                  'refresh_token': 'AQAljYnnDvfv0GBnLKGWfZhMZs0mOflAvs4ZMiejKBb'
#                                   'COVZUTCkL0Svzu12vBMveNRygOnq_HjPzpZqJHMTBHbBb'
#                                   '9U9w5UlP_clrK0JGkdJ04UpdJMizDUuSRpyvL0tFWEvV1g',
#                  'scope': 'playlist-modify-private playlist-read-private',
#                  'expires_at': time.time() + 3600}

# test_data = [(token_expired, True), (token_current, False)]

# #TODO: fixture with scope='function' to test token exception handling.
# # tmp directory
# # write these two tokens to file.
# @pytest.mark.parametrize('test_input, expectation', test_data)
# def test_token_expired(test_input, expectation):
#     """Test token auth."""

#     result = test_input['expires_at'] < time.time()
#     assert result == expectation


# def test_cached_token(mocker, playlist_mgr):
#     """Test if cached token available"""

#     mocker.patch.object(oauth.SpotifyOAuth,
#                         'get_cached_token', return_value=True, autospec=True)
#     playlist_mgr.create_client_mgr()

#     assert playlist_mgr.token_info


# # def test_token_expired(mocker, playlist_mgr):
# #     """Test if cached token available"""

# #     mocker.patch.object(oauth.SpotifyOAuth,
# #                         'is_token_expired', return_value=True, autospec=True)

# #     playlist_mgr.get_auth_token()
# #     assert playlist_mgr.token is None


# def test_scope_correct(mocker, playlist_mgr):
#     mocker.patch.object(oauth.SpotifyOAuth,
#                         '_is_scope_subset', return_value=True, autospec=True)
#     # mocker.patch.object(oauth.SpotifyOAuth,
#     #         '_is_scope_subset', return_value=False, autospec=True)

#     playlist_mgr.get_auth_token()
#     assert playlist_mgr.token is not None


# def test_client_mgr(mocker, playlist_mgr):
#     playlist_mgr.create_client_mgr()
