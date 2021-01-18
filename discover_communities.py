import csv, pdb
from collections import defaultdict
import json
from igraph import *
import numpy as np



CSV_FILE_NAME = 'artists-collabs.csv'
PLOT_NUMBER_OF_SONGS_BY_YEAR = False

class Song:
    def __init__(self, year, artists, title):
        self.year = year
        self.artists = artists
        self.title = title
        
    def __str__(self):
        return self.year + ' - ' + str(self.artists) + ' - ' + self.title


# List of songs
songs_by_year = defaultdict(list)




def prepare_songs():
    # Open CSV file and parse the songs into the instances of class Song
    with open(CSV_FILE_NAME, encoding='utf-8') as collabs_file:
        collabs = csv.reader(collabs_file, delimiter=',')
        next(collabs) # Skipping header
        
        
        for collab in collabs:

            year = collab[0]
            title = collab[2]
            
            artists = collab[1].strip("[]").split(',')
            artists = [artist.replace("\'", "").strip() for artist in artists]
            artists = set(artists)
            
            song = Song(year, artists, title)
            
            songs_by_year[year].append(song)

    
    with open(r"Dataset\artist_genres.json", encoding="utf-8") as f:

        artist_genres = json.load(f)

    
    return songs_by_year, artist_genres
            




def aggregate_graphs(songs,year, years_range = 1):

    # create graph for every year or a group of year
    # example: if I want to create a graph from year 1991 to 1995
    # just set the years_range to 5
    # To create a graph for a single year just leave years_range as 1

    final_year = str( (int(year) + years_range - 1 ) )    
    collabs = {}
    
    for year in songs:

        songs_list = songs[year]
        
        for song in songs_list:
            
            for artist in song.artists:
                
                if artist not in collabs:
                    
                    collabs[artist] = list(song.artists)
                    
    
                else:
                    
                    collabs[artist] += list(song.artists)
                    
            
        if year == final_year:
            break
    
    
    g = Graph()
    artist_indexes = list(collabs.keys())
    g.add_vertices(artist_indexes)
    

    
    for artist in collabs:
        
        for collaborator in set(collabs[artist]):
            
            if (artist != collaborator): # doesn't create self-loop
                
                g.add_edges([(artist,collaborator)])
    
    print('Total graph has {} vertices and {} edges.'.format(g.vcount(), g.ecount()))
    print('The artists with most collaborations are:')
    sorted_degrees = np.argsort(g.degree())
    for i in range(1,11):
        print('- {} with {} collaborations'.format(g.vs[sorted_degrees[-i]]['name'], g.degree(sorted_degrees[-i])))
        
    return g
    


def create_year_graph(songs, year):

    songs_list = songs[year]
    collabs = {}
        
    for song in songs_list:
        
        for artist in song.artists:
            
            if artist not in collabs:
                
                collabs[artist] = list(song.artists)
                

            else:
                
                collabs[artist] += list(song.artists)


    g = Graph()
    artist_indexes = list(collabs.keys())
    g.add_vertices(artist_indexes)


    for artist in collabs:
        
        for collaborator in set(collabs[artist]):
            
            if (artist != collaborator): # doesn't create self-loop
                
                g.add_edges([(artist,collaborator)])
    
    print('Total graph has {} vertices and {} edges.'.format(g.vcount(), g.ecount()))
    print('The artists with most collaborations are:')
    sorted_degrees = np.argsort(g.degree())
    for i in range(1,11):
        print('- {} with {} collaborations'.format(g.vs[sorted_degrees[-i]]['name'], g.degree(sorted_degrees[-i])))
        
    return g




def find_communities(graph, year):

    communities = graph.community_walktrap()

    for community in communities.as_clustering():
        
        community_genres = []
        for artist in community:
            artist_name = graph.vs[artist]["name"]
            if artist_name not in artists_story:
                artists_story[artist_name] = {year : [] }
            
            else:
                artists_story[artist_name][year] = []
            
            try:
                community_genres += artists_genre[artist_name]
            except:
                print("The following artist couldn't be found")
                print(artist)
                print(artist_name)

        
        for artist in community:
            artist_name = graph.vs[artist]["name"]
            community_genres = set(community_genres) #remove duplicates
            artists_story[artist_name][year].append(list(community_genres))





songs, artists_genre = prepare_songs()

artists_story = {}


for year in songs:

    graph = create_year_graph(songs, year)
    find_communities(graph, year)
    


with open("artist_story.json", "w") as out:
    json.dump(artists_story, out)

