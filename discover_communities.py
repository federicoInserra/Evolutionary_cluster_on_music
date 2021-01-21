import csv, pdb
from collections import defaultdict
import json
from igraph import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



CSV_FILE_NAME = 'artists-collabs.csv'

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
        
        # create the dict that contains all the songs divided by year
        for collab in collabs:

            year = collab[0]
            title = collab[2]
            
            artists = collab[1].strip("[]").split(',')
            artists = [artist.replace("\'", "").strip() for artist in artists]
            artists = set(artists)
            
            song = Song(year, artists, title)
            
            songs_by_year[year].append(song)


    # load the file that contains the genres of every artist
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
    
    # create a graph for the year given in input

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
            
            if (artist != collaborator):  # doesn't create self-loop
                
                g.add_edges([(artist,collaborator)])
    
    print('Total graph has {} vertices and {} edges.'.format(g.vcount(), g.ecount()))
    print('The artists with most collaborations are:')
    sorted_degrees = np.argsort(g.degree())
    for i in range(1,11):
        print('- {} with {} collaborations'.format(g.vs[sorted_degrees[-i]]['name'], g.degree(sorted_degrees[-i])))
        
    return g




def find_communities(graph, year):

    # Run the community algorithm on the graph to find the communities for that year
    communities = graph.community_walktrap()

    # create the story of collaboration for every artist and every year
    # so in artists_story for a particular artist and a particular year
    # we will have the list of the genres of the artists that were in the same community that particular years
    # so for example if the algorithm find a community in the graph for the year 2015 that contains Eminem,Rhianna and Shakira
    # then artists_story[Eminem][2015] = [rap, pop, latin] or something similar

    for community in communities.as_clustering():
        
        community_genres = []
        for artist in community:
            artist_name = graph.vs[artist]["name"]
            if artist_name not in artists_story:
                artists_story[artist_name] = {year : [] }
            
            else:
                artists_story[artist_name][year] = []
            
            try:
                community_genres += artists_genre[artist_name] # get the genres of the artist from the file
            except:
                print("The following artist couldn't be found") # the artist wasn't in the file
                print(artist)
                print(artist_name)

        
        for artist in community:
            artist_name = graph.vs[artist]["name"]
            community_genres = set(community_genres) #remove duplicates
            community_genres = filter_genres(community_genres) # use the filter to convert all the sub-genres in the main genres

            artists_story[artist_name][year] = community_genres

    
    return communities
        


def filter_genres(community_genres):

    # map the sub-genres in main genres
    # for example the sub-genre "modern rock" will be substitued by "rock"
    filtered_genres = []
    for gen in community_genres:
        for filt in genre_filter:
            if gen in genre_filter[filt]:
                filtered_genres.append(filt)
    
    return filtered_genres




def show_artist_history(artist):

    for year in artists_story[artist]:
        print("YEAR: ", year)
        print("COMMUNITY: ", artists_story[artist][year])
        
def plot_artist_story(artist):
    
    # creates dictionary which has genres as keys and list of years as value
    years_of_genres = {}
    for year in artists_story[artist]:
        community = artists_story[artist][year]
        for genre in community:
            if genre not in years_of_genres:
                years_of_genres[genre] = []         
            elif year not in years_of_genres[genre]:
                years_of_genres[genre].append(year)
    
    # create active year intervals for each genre
    start = []
    end = []
    music = []
    for genre in years_of_genres:
        years = years_of_genres[genre]
        start_of_interval = True
        for year in years:
            if start_of_interval or int(year) - end[-1] != 1:
                start.append(int(year))
                end.append(int(year))
                music.append(genre)
                start_of_interval = False
            else:
                end[-1] = int(year)
    
                
    # create a dataframe
    df = pd.DataFrame({'group':music, 'start':start , 'end':end })
     
    # reorder it following the values of the first value
    ordered_df = df.sort_values(by='start')
    group_indices = dict([(y,x+1) for x,y in enumerate((set(ordered_df['group'])))])
    positions = [group_indices[x] for x in ordered_df['group']]
     
    import seaborn as sns
    plt.hlines(y=positions, xmin=ordered_df['start'], xmax=ordered_df['end'], color='lightblue', alpha=0.8, linewidth=5.0)
    plt.ylim([0, len(group_indices)+1])
    plt.scatter(ordered_df['start'], positions, color='black', alpha=1, label='start')
    plt.scatter(ordered_df['end'], positions, color='black', alpha=1 , label='end')
     
    # Add title and axis names
    plt.yticks(positions, ordered_df['group'])
    plt.title("{}'s music genres over years".format(artist), loc='center')
    plt.xlabel('Active years')
    plt.ylabel('Genres')
    plt.show()


def analyze_communities(communities):
    pass

songs, artists_genre = prepare_songs()

artists_story = {}

genre_filter = {
    "rock": ["new rave", "british indie rock", "rock", "post-hardcore", "modern rock", "screamo"],
    "house": ["progressive house", "brostep", "electro house", "tropical house", "progressive electro house", "house" ],
    "hip hop": ["kentucky hip hop", "portland hip hop", "brooklyn drill", "trap", "memphis hip hop", "ohio hip hop", "detroit trap", "trap latino", "chicago drill", "atl trap", "vapor trap", "australian hip hop", "latin hip hop", "polynesian hip hop", "uk hip hop", "underground hip hop", "dark trap", "east coast hip hop", "new york drill", "crunk", "hip hop", "drill", "miami hip hop", "queens hip hop", "atl hip hop", "conscious hip hop", "trap queen", "southern hip hop", "canadian hip hop", "minnesota hip hop", "tennessee hip hop" ],
    "rap": ["rap", "st louis rap", "gangster rap", "dfw rap", "sad rap", "alabama rap", "nyc rap", "viral rap", "florida rap", "toronto rap", "rap conscient", "melodic rap", "baton rouge rap", "meme rap", "chicago rap", "dirty south rap", "emo rap", "philly rap", "rap rock"],
    "indie": ["indietronica", "indie soul", "indie poptimism", "indie"],
    "jazz": ["smooth saxophone", "smooth jazz", "jazz"],
    "tropical": ["tropical"],
    "pop": ["barbadian pop", "canadian pop", "pop rap", "dance pop", "social media pop", "etherpop", "scandipop", "indie pop rap", "post-teen pop", "pop edm", "pop", "pop dance", "electropop"],
    "r&b": ["alternative r&b", "pop r&b", "r&b", "neo soul", "escape room", "canadian contemporary r&b", "urban contemporary"],
    "dance": ["dance", "uk dance", "edm", "german dance"],
    "reggae": ["reggae", "dancehall", "reggae fusion"],
    "latin": ["latin", "reggaeton flow", "reggaeton"]

}



all_communities = []
for year in songs:

    graph = create_year_graph(songs, year)
    communities = find_communities(graph, year)
    all_communities.append(communities)
    
            
# save the artists story as a json file
with open("artists_story.json", "w") as out:
    json.dump(artists_story, out)


artist_name = "Wiz Khalifa"
#show_artist_history(artist_name)
plot_artist_story(artist_name)





