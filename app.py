from dotenv import load_dotenv
import base64
import requests
import json
import os
from googleapiclient.discovery import build
import googleapiclient.errors
from settings import playlist_id
from pytube import YouTube


load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


def get_token():
    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode("ascii")
    base64_bytes = base64.b64encode(auth_bytes)
    auth_base64 = base64_bytes.decode("ascii")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials"}

    # Post creadentials to obtain a token
    response = requests.post(url, headers=headers, data=data)
    token_info = json.loads(response.content)
    return token_info["access_token"]

def get_authorization_header(token):
    return {"Authorization": "Bearer " + token}

def get_playlist_tracks_info(playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    header = get_authorization_header(token)
    response = requests.get(url, headers=header)
    data = json.loads(response.content)
    return data['tracks']['items']

def track_list(tracks_info):
    return [track['track'] for track in tracks_info]

def get_artists(tracks):
    return [track['artists'][0]['name'] for track in tracks]

def get_songs(tracks):
    return [track['name'] for track in tracks]

def get_playlist_name(playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    header = get_authorization_header(token)
    response = requests.get(url, headers=header)
    data = json.loads(response.content)
    return data['name']

token = get_token()

tracks_info = get_playlist_tracks_info(playlist_id)
tracks = track_list(tracks_info)

artists = get_artists(tracks)
songs= get_songs(tracks)


# Get YouTube songs addresses
api_key = os.getenv("API_KEY")

youtube = build("youtube", "v3", developerKey=api_key)

def get_song_data(artist, song):
    request = youtube.search().list(
        part = "snippet",
        maxResults = 1,
        q = artist + " " + song
    )
    response = request.execute()
    return response

def get_song_url(data):
    id = data['items'][0]['id']['videoId']
    return f"https://www.youtube.com/watch?v={id}"

def main():
    # Get urls for all songs
    songs_urls = []
    for i, artist in enumerate(artists):
        data = get_song_data(artist, songs[i])
        url = get_song_url(data)
        songs_urls.append(url)
    
    # Download songs
    music_folder = os.path.expanduser('~/Music')
    playlist_name = get_playlist_name(playlist_id)
    destination = os.path.join(music_folder, playlist_name)
    os.mkdir(destination)
    for url in songs_urls:
        yt = YouTube(url)
        audio = yt.streams.filter(only_audio=True).first()

        # download song
        file = audio.download(output_path=destination)

        # change song extension
        mp3_file = file.replace(".mp4", ".mp3")
        os.rename(file, mp3_file)

        # print result
        print(mp3_file.split('/')[-1] + " Successfully downloaded.")

if __name__ == "__main__":
    main()
