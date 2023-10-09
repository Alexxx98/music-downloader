import requests
from .utils import get_api_data


class Playlist():
    def __init__(self, data, token):
        self.data = data
        self.token = token

    def __str__(self):
        return str(self.data)

    def get_image(self):
        ...
    
    def get_title(self):
        ...

    @property
    def tracks(self):
        songs = []
        song = dict()
        url = self.data['tracks']['href']
        tracks_data = get_api_data(url, self.token)
        for track in tracks_data['items']:
            song = song.copy()
            song['artist'] = track['track']['artists'][0]['name']
            song['track'] = track['track']['name']
            songs.append(song)
        return songs