"""
    Search through local websites finding upcooming concerts
    Return concert date, price, and all

"""
import urllib.request
from bs4 import BeautifulSoup

import json 
import spotipy
import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError

import pdb
import pprint

from collections import defaultdict



band_link = 'http://www.flagpole.com/events/live-music'
source = urllib.request.urlopen(band_link).read()
concert_soup = BeautifulSoup(source, 'lxml')


username = '1221978947'
client_id = 'c6eb3116302b4a34bc648de103980ca4'
client_secret = 'f03d18348d954510aa8ebdbc3a9b380c'
redirect_uri = 'http://google.com/'
scope = 'playlist-read-private playlist-modify-private'



def get_local_artists(soup):
    """Return set of local artists """
    
    event_list = soup.find('div',class_='event-list')
    future_concerts = defaultdict(list)
    dates = [date.string for date in event_list.find_all('h2')]
       
    for date in dates:
        for child in date.find_next('li').children:
            if child.name == 'p' and child.find('strong'):
                if child.next_element.string is not None:
                    fixed_child = child.next_element.string.replace('\xa0', ' ')
                    future_concerts[date].append(fixed_child)

    ##https://stackoverflow.com/questions/716477/join-list-of-lists-in-python
    return future_concerts, set([j for i in future_concerts.values() for j in i])


def get_uri(string):
    """ """
    str_list = string.split(':')
    return str_list[-1]

def get_playlist_id(string):
    """ """
    usr_playlists = sp.current_user_playlists(limit=50)
    for item in usr_playlists['items']:
        if item['name'] == "2018":
            return  get_uri(item["uri"])
        

if __name__ == '__main__':

    concert_dates , unique_artists = get_local_artists(concert_soup)
    artists_top_songs = defaultdict(list)
    token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)
                                       
    if token:
        sp = spotipy.Spotify(auth=token)
        #Get Artist ID
        results = [sp.search(q='artist:' + artist_name, type='artist') for artist_name in unique_artists]

        ## Put together dictionary of local artists and their top songs
        for res in results:
            if res['artists']['items'] == []:
                results.remove(res)
            else:
                if isinstance(res, list):
                    artist_info = res['artists']['items'][0]
                elif isinstance(res, dict):
                   artist_info = res['artists']['items']
                   
                artist_name = artist_info[0]['name']
                artist_uri = get_uri(artist_info[0]['uri'])
                top_tracks = sp.artist_top_tracks(artist_info[0]["uri"])
                top_tracks_uri = [get_uri(item["uri"]) for item in top_tracks['tracks']]
                artists_top_songs[artist_name] = top_tracks_uri

        track_ids = [j for i in artists_top_songs.values() for j in i]
        playlist_id = get_playlist_id('2018')

        results = sp.user_playlist_add_tracks(username, playlist_id, track_ids)
                                       
                                       

            
        

            
