import spotipy
from spotipy.oauth2 import SpotifyOAuth
from json import load
from operator import itemgetter
from time import sleep, time
from pprint import pprint
import pandas as pd
from numpy.random import choice


MAX_LEN = 90
WINDOW = int(MAX_LEN / 2)
with open('creds.json', 'r') as f:
    creds = load(f)
    CLIENT_ID = creds['CLIENT_ID']
    CLIENT_SECRET = creds['CLIENT_SECRET']
    REDIRECT_URI = creds['REDIRECT_URI']

# client_credentials_manager = SpotifyClientCredentials(
#     client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

# access_token = client_credentials_manager.get_access_token()
# spotify = spotipy.Spotify(auth=access_token)
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope='streaming playlist-read-private user-read-playback-state'))
# print(spotify.get_authorize_url())

playlists = list(map(lambda p: {
    'name': p['name'], 'url': p['href'].split('/')[-1], 'id': p['id']}, spotify.current_user_playlists()['items']))

for i, p in enumerate(list(map(itemgetter('name'), playlists))):
    print(i + 1, ')', p)

index = int(input('Choose a playlist: '))

playlist = playlists[index - 1]
tracks = list(map(lambda t: t['track']['id'], spotify.user_playlist_tracks(
    spotify.me(), playlist['id'])['items']))
tracks_ids = choice(tracks, size=len(tracks)).tolist()

# spotify.shuffle(False)
# spotify.volume(0)
# spotify.start_playback(
#     context_uri=f"spotify:playlist:{playlist['url']}")
# spotify.pause_playback()

track_id = tracks_ids[0]
analysis = spotify.audio_analysis(track_id)
analysis_data = pd.json_normalize(analysis['sections'])
next_position = max(0, int(
    analysis_data.loc[analysis_data['loudness'] == analysis_data['loudness'].max(), 'start'].values[0] * 1000) - WINDOW)

for track_id in tracks_ids[1:-1]:
    spotify.volume(10)
    spotify.start_playback(
        uris=[f"spotify:track:{track_id}"], position_ms=next_position)
    for i in range(5):
        spotify.volume(50 + 10 * (i + 1))
        sleep(1)

    start = time()
    track_id = tracks_ids[tracks_ids.index(track_id) + 1]
    analysis = spotify.audio_analysis(track_id)
    analysis_data = pd.json_normalize(analysis['sections'])
    next_position = max(0, int(
        analysis_data.loc[analysis_data['loudness'] == analysis_data['loudness'].max(), 'start'].values[0] * 1000) - WINDOW)
    sleep(WINDOW - int(time() - start) - 10)
    for i in range(9):
        spotify.volume(100 - 10 * (i + 1))
        sleep(1)

spotify.start_playback(
    uris=[f"spotify:track:{track_id}"], position_ms=next_position)
sleep(WINDOW)
spotify.next_track()
