import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials 
import pandas as pd
import requests
import json

CLIENT_ID = 'b6cc781ec664416cbb87d155453c7c67'
CLIENT_SECRET = '926a90b9d7524d98aa917a56e8f789a4'
APP_REDIRECT_URI = 'http://localhost:8080'

import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=APP_REDIRECT_URI,
                                               scope="user-library-read"))

results = sp.current_user_saved_tracks()
for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], " – ", track['name'])

user = sp.user('loykid')
print(user)

####################################################################################

# POST
AUTH_URL = 'https://accounts.spotify.com/api/token'
auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
})

# convert the response to JSON
auth_response_data = auth_response.json()

# save the access token
access_token = auth_response_data['access_token']

headers = {
    'Authorization': 'Bearer {token}'.format(token=access_token)
}

####################################################################################
# Getting tracks of playlist
# https://open.spotify.com/playlist/6mibwkjdwaksJQPfxRjBbr?si=ddb55bfe25384023

playlist_id = '6mibwkjdwaksJQPfxRjBbr'
BASE_URL = 'https://api.spotify.com/v1/'
r = requests.get(BASE_URL + 'playlists/' + playlist_id + '/tracks', 
                 headers=headers,
                 params={'limit': 50})

d = r.json()
d
with open('playlist.txt', 'w', encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False)

####################################################################################

def call_playlist(creator, playlist_id):
    
# Listing the features that I want

    playlist_features_list = ["artist","album","track_name",
    "track_id","danceability","energy","key","loudness","mode", 
    "speechiness","instrumentalness","liveness","valence","tempo", 
    "duration_ms","time_signature"]
    
    playlist_df = pd.DataFrame(columns = playlist_features_list)
    
# Using a dictionary to get the data for artist, album, track_name and track_id
    
    playlist = sp.user_playlist_tracks(creator, playlist_id)["items"]
    for track in playlist:
        # Create empty dict
        playlist_features = {}
        # Get metadata
        playlist_features["artist"] = track["track"]["album"]["artists"][0]["name"]
        playlist_features["album"] = track["track"]["album"]["name"]
        playlist_features["track_name"] = track["track"]["name"]
        playlist_features["track_id"] = track["track"]["id"]
        
        # Get audio features
        audio_features = sp.audio_features(playlist_features["track_id"])[0]
        for feature in playlist_features_list[4:]:
            playlist_features[feature] = audio_features[feature]
        
        # Concat the dfs
        track_df = pd.DataFrame(playlist_features, index = [0])
        playlist_df = pd.concat([playlist_df, track_df], ignore_index = True)

# Creating a dataframe
        
    return playlist_df

####################################################################################

df = call_playlist("loykid","6mibwkjdwaksJQPfxRjBbr")

# Write to csv
compression_opts = dict(method='zip',
                        archive_name='playlist.csv')  
df.to_csv('playlist.zip', index=False,
          compression=compression_opts) 