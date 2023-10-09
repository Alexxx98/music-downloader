from django.shortcuts import render, redirect
from django.http import HttpResponse

from spotipy.oauth2 import SpotifyOAuth
from music_downloader.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

from .utils import get_api_data
import time

from .classes import Playlist


SPOTIFY_SCOPES = 'user-library-read playlist-read-private playlist-read-collaborative'

sp_oauth = SpotifyOAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, scope=SPOTIFY_SCOPES)

# Create your views here.
def connect(request):
    return render(request, 'downloader/connect.html')

def login(request):
    auth_url = sp_oauth.get_authorize_url()
    if 'token_info' not in request.session:
        request.session['token_info'] = ''
    return redirect(auth_url)

def callback(request):
    token_info = sp_oauth.get_access_token(request.GET.get('code'))
    request.session['token_info'] = token_info
    if token_info:
        return redirect('home')
    else:
        return redirect('connect')

def home(request):
    """ 
    Get current user's playlist and render them on the page
    """
    token_info = request.session['token_info']

    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        sp_oauth = SpotifyOAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, scope=SPOTIFY_SCOPES)
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])

    token = token_info['access_token']

    playlists_url = f"https://api.spotify.com/v1/me/playlists"
    playlists_data = get_api_data(playlists_url, token)
    if 'playlists_data' not in request.session:
        request.session['playlists_data'] = playlists_data

    playlists_items = playlists_data['items']
    playlists = []
    for playlist_data in playlists_items:
        playlists.append(Playlist(playlist_data, token))

    return render(request, "downloader/home.html", {
        "playlists": playlists,
        "playlist": playlists[0],
    })
