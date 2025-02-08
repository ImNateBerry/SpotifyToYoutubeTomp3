from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
from googleapiclient.discovery import build
import yt_dlp as youtube_dl

load_dotenv()

youtube_api_key = os.getenv("YOUTUBE_API_KEY")
youtube = build('youtube', 'v3', developerKey=youtube_api_key)
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
song_list = [] #stores list of song names from spotify playlist
artist_list = [] #stores list of artist names from spotify playlist
search_list = [] #stores values of song and artist to be searched for on YouTube

#creates authorization token for spotify api use
def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type":"client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

#creates authorization header for spotify api use
def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

#searches for playlist on spotify given the name of the playlist and gives the playlist id value
#string playlist_name: name of the playlist to be searched on spotify
def search_for_playlist(token, playlist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={playlist_name}&type=playlist&limit=1"
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)['playlists']['items']
    if len(json_result) == 0:
        print("Oops, no playlist found")
        return None
    return json_result[0]

#gets track names from spotify playlist given the playlist id value
#string id: spotify playlist id value
def get_tracks(token, id):
    url = "https://api.spotify.com/v1/playlists"
    headers = get_auth_header(token)
    query = f"/{id}/tracks?fields=items(track(name(name)))"
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)['items']
    return json_result

#gets artist names from spotify playlist given the playlist id value
#string id: spotify playlist id
def get_artists(token, id):
    url = "https://api.spotify.com/v1/playlists"
    headers = get_auth_header(token)
    query = f"/{id}/tracks?fields=items(track(artists(name)))"
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)['items']
    return json_result

#searches for videos on YouTube using YouTube api given a term to search for and returns the most relevant video's video id
#string video_search: the term to be searched on YouTube
def search_for_video(video_search):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={video_search}&type=video&key={youtube_api_key}&fields=items(id(videoId))"
    result = get(url)
    json_result = json.loads(result.content)['items'][0]['id']['videoId']
    return json_result

#downloads the video as an mp3 from Youtube given a valid YouTube url
#string yt_url: valid Youtube url
def download_audio(yt_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'verbose': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'postprocessor_args': [
            '-ar', '16000'
        ],
        'prefer_ffmpeg': True,
    }
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([yt_url])

token = get_token()
# playlist = search_for_playlist(token, "Today's Top Hits")
playlist_id = input("Enter your playlist id: ") #playlist['id']
songs = get_tracks(token, playlist_id) #creates an unfiltered list of track data
artists = get_artists(token, playlist_id) #creates an unfiltered list of artist data

#iterates through songs and filters it into a new list to only have the names of tracks
for song in songs:
    song_list.append(song['track']['name'])

#iterates through artists and filters it into a new list to only have the names of artist
for artist in artists:
    artist_list.append(artist['track']['artists'][0]['name'])

#combines the ith terms of both song and artist list to create a search term to be used in the YouTube api
for i in range(len(song_list)):  
   search_term = song_list[i] + " by " + artist_list[i]
   search_list.append(search_term) 

#searches for and downloads the ith video in the search_list list
for i in range(len(search_list)):
    searched_video_id = search_for_video(search_list[i])
    final_url = f"https://www.youtube.com/watch?v={searched_video_id}"
    download_audio(final_url)





