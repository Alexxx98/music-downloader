import requests
from .utils import get_api_data


class Playlist():
    def __init__(self, data, token):
        self.data = data
        self.token = token

    def __str__(self):
        return str(self.data)

    @property
    def image(self):
        try:
            return self.data['images'][0]['url']
        except IndexError:
            return None
    
    @property
    def title(self):
        return self.data['name']

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