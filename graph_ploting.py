import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pdb
 
# Create a dataframe
start = np.array([2015, 2016, 2017, 2019])
end = start + np.array([4, 2, 1, 2])
music = np.array(['pop', 'rock', 'hip hop', 'jazz'])
df = pd.DataFrame({'group':music, 'start':start , 'end':end })
 
# Reorder it following the values of the first value:
ordered_df = df.sort_values(by='start')
my_range=range(1, len(df.index)+1)

#pdb.set_trace()
 
# The vertical plot is made using the hline function
# I load the seaborn library only to benefit the nice looking feature
import seaborn as sns
plt.hlines(y=my_range, xmin=ordered_df['start'], xmax=ordered_df['end'], color='lightblue', alpha=0.8, linewidth=10.0)
plt.ylim([0, len(df.index)+1])
#plt.scatter(ordered_df['start'], my_range, color='red', alpha=1, label='start')
#plt.scatter(ordered_df['end'], my_range, color='red', alpha=1 , label='end')
#plt.legend()
 
# Add title and axis names
plt.yticks(my_range, ordered_df['group'])
plt.title("Music genres over years", loc='center')
plt.xlabel('Active years')
plt.ylabel('Genres')
plt.show()

