import pdb
import csv
import re
import numpy as np
from igraph import *
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import itertools

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

# Open CSV file and parse the songs into the instances of class Song
with open(CSV_FILE_NAME, encoding='utf-8') as collabs_file:
    collabs = csv.reader(collabs_file, delimiter=',')
    next(collabs) # Skipping header
    
    for collab in collabs:
        #pdb.set_trace()
        year = collab[0]
        name = collab[2]
        
        artists = collab[1].strip("[]").split(',')
        artists = [artist.replace("\'", "").strip() for artist in artists]
        artists = set(artists)
        
        song = Song(year, artists, name)
        
        songs_by_year[year].append(song)
        artists_vertices.update(artists)
        
 
# Plotting number of songs by year
if PLOT_NUMBER_OF_SONGS_BY_YEAR:
    years = list(songs_by_year.keys())
    number_of_songs = [len(songs) for year, songs in songs_by_year.items()]

    plt.plot(years, number_of_songs)
    plt.xticks(rotation=75)
    plt.xlabel('Year')
    plt.ylabel('Number of songs')
    plt.title('Number of songs by year')
    plt.show()
 
# Create graph and add artists as vertices
g = Graph()
g.add_vertices(list(artists_vertices))

# Applying clustering algorithms
for year in songs_by_year.keys():
    songs = songs_by_year[year]
    for song in songs:
        artists = song.artists
        for x in itertools.combinations(artists, 2):     
            g.add_edges([x])
    print('Added collaborations for year', year)   
    
# Resulting graph statistics
print('Total graph has {} vertices and {} edges.'.format(g.vcount(), g.ecount()))
print('The artists with most collaborations are:')
sorted_degrees = np.argsort(g.degree())
for i in range(1,6):
    print('- {} with {} collaborations'.format(g.vs[sorted_degrees[-i]]['name'], g.degree(sorted_degrees[-i])))

 
# For debugging
pdb.set_trace()


