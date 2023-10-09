from django.shortcuts import render, redirect
from django.http import HttpResponse

from spotipy.oauth2 import SpotifyOAuth
from pytube import YouTube
from googleapiclient.discovery import build
from music_downloader.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, YOUTUBE_API_KEY

from .utils import get_api_data
from .classes import Playlist

import time
import os



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

    playlists_items = playlists_data['items']
    playlists = []
    for playlist_data in playlists_items:
        playlists.append(Playlist(playlist_data, token))

    if 'playlists' not in request.session:
        request.session['playlists'] = []

    for playlist in playlists:
        request.session['playlists'].append(playlist.serialize())

    return render(request, "downloader/home.html", {
        "playlists": playlists,
    })

def download(request, playlist_title):
    playlists = request.session['playlists']
    for playlist in playlists:
        if playlist_title in playlist:
            pl = playlist
            tracks = playlist[playlist_title]

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    # generate youtube query
    urls = []
    for track in tracks:
        r = youtube.search().list(
        part = "snippet",
        maxResults = 1,
        q = track['artist'] + " " + track['track']
    )
        # get track data from query
        response = r.execute()
        
        # get video url
        id = response['items'][0]['id']['videoId']
        urls.append(f"https://www.youtube.com/watch?v={id}")  

    music_folder = os.path.expanduser('~/Music')
    destination = os.path.join(music_folder, playlist_title.title())
    try:
        os.listdir(destination)
    except FileNotFoundError:
        os.mkdir(destination)
    
    for url in urls:
        yt = YouTube(url)
        audio = yt.streams.filter(only_audio=True).first()

        # download song
        file = audio.download(output_path=destination)

        # change song extension
        mp3_file = file.replace(".mp4", ".mp3")
        os.rename(file, mp3_file)

    return redirect("success")

def success(request):
    return render(request, "downloader/success.html")
