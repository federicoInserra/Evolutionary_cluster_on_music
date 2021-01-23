import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import csv
import json

# Code to retrieve all the genres of the artists from the dataset and save them as a json file

CLIENT_ID = "INSERT YOUR CLIENT ID"
CLIENT_SECRET = "INSERT YOUR CLIENT SECRET"

def create_connection():
    spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))
    
    return spotify


def load_dataset(path = r"Dataset\artists-collabs.csv"):
    artists_list = {}
    with open(path, encoding='utf-8')as f:
        data = csv.reader(f)
        line_count = 0
        for row in data:
            try:
                if line_count > 0:
                    
                    r = row[1].replace("'","")
                    r = r.strip('][').split(', ')
                    
                    for artist in r:
                        if artist not in artists_list:
                            artists_list[artist] = []
            
            except:
                pass

            line_count += 1
            
    return artists_list
            



def get_artist_id(artist_name, spotify):

    results = spotify.search(q='artist:' + artist_name, type='artist') #query to retrieve artistID
    items = results['artists']['items']
    if len(items) > 0:
        artist_id = items[0]['id']
    
    return artist_id


def get_artist_genres(artist_id, spotify):

    artist = spotify.artist(artist_id)
    return artist['genres']


dataset = load_dataset()


spotify = create_connection()
c = 0
for artist in dataset:
    
    try:
        artist_id = get_artist_id(artist, spotify)
        genres = get_artist_genres(artist_id, spotify)

        dataset[artist] = genres
        c += 1
        if c % 100 == 0:
            print(c)
    except:
        continue


with open("artist_genres.json", "w") as out:
    json.dump(dataset, out)

