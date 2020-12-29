import pdb
import csv
import re
from igraph import *
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

CSV_FILE_NAME = 'artists-collabs-3.csv'

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
        
        songs_by_year[year].append(song)
        artists_vertices.update(artists)
        
 
# Create graph and add artists as vertices
g = Graph()
g.add_vertices(artists_vertices)
    

# Plotting number of songs by year
years = list(songs_by_year.keys())
number_of_songs = [len(songs) for year, songs in songs_by_year.items()]

plt.plot(years, number_of_songs)
plt.xticks(rotation=75)
plt.xlabel('Year')
plt.ylabel('Number of songs')
plt.title('Number of songs by year')
plt.show()
 
 
# For debugging
pdb.set_trace()


