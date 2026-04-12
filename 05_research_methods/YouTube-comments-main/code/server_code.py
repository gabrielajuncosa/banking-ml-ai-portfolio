from sbmtm import sbmtm
import graph_tool.all as gt

import pandas as pd
import os
import sys


samp = str(sys.argv[1])


data_directory = os.getcwd()[:-4] + 'data/'

## load the data
user_df = pd.read_csv(data_directory + 'user_comment_stats.csv')

if samp == 'yes':
    user_df = user_df.sample(n=1000)
    print(len(user_df))
print("data loaded")


## we create an instance of the sbmtm-class
model = sbmtm()



## we have to create the word-document network from the corpus
model.make_graph_new(user_df)
print("graph created")



## save the graph for future use
if samp == 'yes':
    model.save_graph(filename=data_directory+f'/user_graph_samp_{samp}.gt.gz')
else:
    model.save_graph(filename=data_directory+'/user_graph.gt.gz')


## fit the model
gt.seed_rng(42)
model.fit()
print("model fitted")


## save the model
if samp == 'yes':
    model.save_model(data_directory+f'/user_model_samp_{samp}.pkl')
else:
    model.save_model(data_directory+'/user_model.pkl')