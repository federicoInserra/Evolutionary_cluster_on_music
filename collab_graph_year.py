import csv
from collections import defaultdict
import json
from igraph import *



CSV_FILE_NAME = 'artists-collabs.csv'
PLOT_NUMBER_OF_SONGS_BY_YEAR = False

class Song:
    def __init__(self, year, artists, name):
        self.year = year
        self.artists = artists
        self.name = name
        
    def __str__(self):
        return self.year + ' - ' + str(self.artists) + ' - ' + self.name


# List of songs
songs_by_year = defaultdict(list)


# Set of artists
artists_vertices = set()


def prepare_songs():
    # Open CSV file and parse the songs into the instances of class Song
    with open(CSV_FILE_NAME, encoding='utf-8') as collabs_file:
        collabs = csv.reader(collabs_file, delimiter=',')
        next(collabs) # Skipping header
        
        
        for collab in collabs:

            year = collab[0]
            name = collab[2]
            
            artists = collab[1].strip("[]").split(',')
            artists = [artist.replace("\'", "").strip() for artist in artists]
            artists = set(artists)
            
            song = Song(year, artists, name)
            
            songs_by_year[year].append({"title":name,"artists":list(artists)})
            
            artists_vertices.update(artists)
    
    return songs_by_year
            




def create_graph_year(songs,year, interval = 5):

    #create list of artists to remember vertices ids

    collabs = {}
    artists_list = []

    for year in songs:
        songs_list = songs[year]
        
        for song in songs_list:
            for artist in song['artists']:
                if artist not in collabs:
                    cobs = song['artists']
                    cobs.remove(artist)
                    collabs[artist] = cobs
                
                else:
                    cobs = collabs[artist]
                    cobs += song['artists']
                    cobs.remove(artist)
                    collabs[artist] = cobs
            

        if year == "1993":
            break
    
    
    g = Graph()
    g.add_vertices(list(collabs.keys()))

    
    for artist in collabs:
        
        for collaborator in set(collabs[artist]):
            
            artist = g.vs.find(artist)
            collaborator = g.vs.find(collaborator)
            g.add_edges([(artist,collaborator)])
    
    print(summary(g))





#----------------------MAIN
songs = prepare_songs()
create_graph_year(songs,"1991")



