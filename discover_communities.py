import csv, pdb
from collections import defaultdict, Counter
import json
from igraph import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from community_measures import *


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
    


def create_year_graph(songs, year, print_stats=False):
    
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
    
    if print_stats:
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
    
    genres_by_communities = []

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
                print("The following artist couldn't be found: {} - {}".format(artist, artist_name)) # the artist wasn't in the file

        genres_by_communities.append(filter_genres(community_genres)) 
        
        for artist in community:
            artist_name = graph.vs[artist]["name"]
            #community_genres = set(community_genres) #remove duplicates
            community_genres = filter_genres(community_genres) # use the filter to convert all the sub-genres in the main genres

            artists_story[artist_name][year] = community_genres

 
    return genres_by_communities
        


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
    list_of_genres = []
    
    for year in artists_story[artist]:
        community = artists_story[artist][year]
        counts = Counter(community)
        
        occurences = counts.most_common()
        most_common_counts = occurences[0][1]
  
        dominant_genres = []
        i = 0
        while i < len(occurences) and occurences[i][1] == most_common_counts:
            dominant_genres.append(occurences[i][0])
            i += 1
        
        for genre in dominant_genres:
            #pdb.set_trace()
            if genre not in years_of_genres:
                list_of_genres.append(genre)
                years_of_genres[genre] = []
                years_of_genres[genre].append(year)
            elif year not in years_of_genres[genre]:
                years_of_genres[genre].append(year)
               
    # create graph points
    xs = []
    ys = []
    for genre in years_of_genres:
        years = years_of_genres[genre]
        for year in years:
            xs.append(year)
            y =list_of_genres.index(genre) + 1
            ys.append(y)
                 
    sorted_points = sorted(zip(xs,ys), key=lambda x:x[0])
    xs = [x[0] for x in sorted_points]
    ys = [x[1] for x in sorted_points]
    
    # plot
    import seaborn as sns
    plt.ylim([0, len(set(ys))+1])
    plt.plot(xs, ys, color='black', alpha=1, zorder=1)
    plt.scatter(xs, ys, color='blue', alpha=1, label='start', zorder=2)
     
    # add title and axis names
    plt.hlines(range(1, len(set(ys))+1), min(xs), max(xs), linestyle='dashed', alpha=0.1)
    plt.yticks(range(1, len(set(ys))+1), list_of_genres)
    plt.title("{}'s music genres over years".format(artist), loc='center')
    plt.xlabel('Active years')
    plt.ylabel('Genres')
    plt.show()


def analyze_communities(communities):
    most_common_genres = []
    for community in communities:
        if community:
            most_common = max(set(community), key=community.count)
            most_common_genres.append(most_common)
       
    print(most_common_genres)
        



songs, artists_genre = prepare_songs()

artists_story = {}

genre_filter = {
    "rock": ["modern folk rock", "alternative roots rock", "israeli rock", "hard rock", "argentine rock", "irish rock", "chamber folk", "rock en espanol", "chilean rock", "latin rock", "post-grunge", "spanish pop rock", "classic rock", "pop rock", "rock-and-roll", "rockabilly", "new rave", "british indie rock", "dance rock", "art rock", "folk", "new wave", "rock", "post-hardcore", "modern rock", "screamo", "folk rock", "mellow gold", "soft rock"],
    "house": ["progressive house", "brostep", "electro house", "tropical house", "progressive electro house", "house" ],
    "hip hop": ["bass trap", "dutch hip hop", "mexican hip hop", "desi hip hop", "kentucky hip hop", "portland hip hop", "brooklyn drill", "trap", "memphis hip hop", "ohio hip hop", "detroit trap", "trap latino", "chicago drill", "atl trap", "vapor trap", "australian hip hop", "latin hip hop", "polynesian hip hop", "uk hip hop", "underground hip hop", "dark trap", "east coast hip hop", "new york drill", "crunk", "hip hop", "drill", "miami hip hop", "queens hip hop", "atl hip hop", "conscious hip hop", "trap queen", "southern hip hop", "canadian hip hop", "minnesota hip hop", "tennessee hip hop" ],
    "rap": ["k-rap", "rap underground mexicano", "comedy rap", "rap latina", "rap chileno", "rap", "west coast rap", "st louis rap", "gangster rap", "dfw rap", "sad rap", "alabama rap", "nyc rap", "viral rap", "florida rap", "toronto rap", "rap conscient", "melodic rap", "baton rouge rap", "meme rap", "chicago rap", "dirty south rap", "emo rap", "philly rap", "rap rock"],
    "indie": ["k-indie", "indie rock", "saskatchewan indie", "indie anthem-folk", "indietronica", "indie soul", "indie poptimism", "indie", "indie cafe pop", "spanish indie pop", "indie folk", "indie pop"],
    "jazz": ["sleep", "environmental", "rebel blues", "nu jazz", "easy listening", "deep adult standards", "jazz trumper", "new orleans jazz", "soul", "swing", "vocal jazz", "soul blues", "traditional blues", "blues rock", "smooth saxophone", "smooth jazz", "jazz", "quiet storm", "adult standards", "jazz blues", "swing", "vocal jazz", "french jazz", "italian contemporary jazz", "jazz accordion", "accordion", "bandoneon", "chanson"],
    "tropical": ["tropical", "tropical house"],
    "metal" : ["nu metal", "alternative metal", "symphonic metal"],
    "funk":["funk", "g funk", "instrumental funk", "afrobeat"],
    "spiritual" : ["rap cristiano", "latin worship", "latin christian", "latin worship", "rock cristiano", "latin christian", "latin worship", "christian hip hop", "ccm", "christian alternative rock", "christian music", "worship"],
    "movies" : ["video game music", "talent show", "sufi", "modern bollywood", "filmi", "british comedy", "hollywood", "movie tunes", "show tunes", "broadway", "disney", "video game music"],
    "classical" : ["norwegian classical", "cello", "canadian classical", "classical piano", "hungarian classical performance", "post-romantic era", "british classical piano", "impressionism", "classical", "classical era", "early romantic era", "german romanticism", "violin", "classical performance", "orchestra", "american orchestra"],
    "pop": ["psychedelic pop", "art pop", "nyc pop", "k-pop", "dutch pop", "pop violin", "bow pop", "folk-pop", "uk pop", "viral pop", "mainland chinese pop", "cantopop", "mandopop", "israeli pop", "antiviral pop", "latin pop", "desi pop", "laatin pop", "spanish pop", "bow pop", "pop punk", "socal pop punk", "post-teen pop", "mexican pop", "swedish pop", "classic italian pop", "italian adult pop", "operatic pop", "boy band", "europop", "latin pop", "barbadian pop", "canadian pop", "pop rap", "dance pop", "social media pop", "etherpop", "scandipop", "indie pop rap", "post-teen pop", "pop edm", "pop", "pop dance", "electropop"],
    "r&b": ["korean r&b", "chill r&b", "alternative r&b", "pop r&b", "r&b", "neo soul", "escape room", "canadian contemporary r&b", "urban contemporary", "philly soul"],
    "dance": ["dance", "uk dance", "edm", "german dance", "dance-punk", "alternative dance"],
    "reggae": ["argentine reggae", "reggae", "dancehall", "reggae fusion", "ska argentino"],
    "soundtrack" : ["soundtrack", "german soundtrack", "neoclassical darkwave", "oceania soundtrack", "british soundtrack", "canadian soundtrack"],
    "latin": ["latin alternative", "latintronica", "nueva cancion", "latin", "reggaeton flow", "reggaeton", "vallenato", "vallenato moderno", "vallenato", "latin arena pop"],
    "country" : ["outlaw country", "contemporary country", "country", "country road", "country rock", "bluegrass", "progressive bluegrass"],
    "trance" : ["acid trance", "bubble trance", "dream trance", "german trance"],
    "house" : ["deep euro house", "bleep techno", "electronica", "dubstep", "gaming dubstep",  "filter house", 'chicago house', 'disco', 'diva house', 'post-disco', 'vocal house', 'eurodance', 'hip house', 'tribal house', "german techno"],
    "mexican" : ['banda', 'corrido', 'deep regional mexican', 'norteno', 'nuevo reginal mexicano', 'regional mexican', 'grupera', 'gruperas inmortales', 'ranchera']
}


for year in songs:
    graph = create_year_graph(songs, year)
    genres_by_communities = find_communities(graph, year)
    
    comms = graph.community_walktrap()
    memberships = comms.as_clustering().membership
    exp = expansion(graph, memberships)
    cond = conductance(graph, memberships)
    cc = graph.transitivity_undirected()
    tp = tp_ratio(graph, memberships)

    print('Year {} = Transitivity: {}, Expansion: {}, Conducatance: {}, Triangle participation ratio: {}'.format(year, cc, exp, cond, tp))
    
            
# save the artists story as a json file
with open("artists_story.json", "w") as out:
    json.dump(artists_story, out)

# Plot simple graph for the report:
g = create_year_graph(songs,'1991')
plot(g, 'report-images/graph-1991.png', layout=g.layout("kk"))

artist_name = "Bad Bunny"
#show_artist_history(artist_name)
#plot_artist_story(artist_name)

# If we want to calculate CC

# print('Clustering coefficient of year {} graph with {} vertices: {}.'.format(year, graph.vcount(), cc))

    
    







