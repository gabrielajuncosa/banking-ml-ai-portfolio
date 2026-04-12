#!/usr/bin/env python
# coding: utf-8

# In[6]:


from graph_tool.all import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re
import glob
import pickle
from tqdm import tqdm
import powerlaw
import matplotlib as mpl
from collections import Counter,defaultdict


data_directory = os.getcwd()[:-4] + 'data/'
figure_directory = os.getcwd()[:-4] + 'figures/'

text_font = 18
mpl.rcParams.update({'font.size': text_font, 'font.style': 'normal', 'font.family':'sans-serif'})


# In[20]:


deg_thresh = 10


# In[21]:


graph = load_graph(data_directory + 'user_graph.gt.gz')

# Initial number of vertices
initial_num_vertices = graph.num_vertices()

while True:
    deg = graph.degree_property_map('out')
    deg_array = np.array([deg[v] for v in graph.get_vertices()])
    mask = deg_array >= deg_thresh

    # Check if any vertices will be filtered out
    if not np.any(mask):  # If no vertices are being filtered, exit the loop
        break

    vertex_filter = graph.new_vertex_property('bool', mask.tolist())
    graph.set_vertex_filter(vertex_filter)
    graph.purge_vertices()

    current_num_vertices = graph.num_vertices()
    print(graph.num_edges(), current_num_vertices)

    # Break the loop if the number of vertices does not change
    if current_num_vertices == initial_num_vertices:
        break
    else:
        initial_num_vertices = current_num_vertices


# In[ ]:


user_df = pd.read_csv(data_directory + 'user_comment_stats.csv')
video_df = pd.read_csv(data_directory + 'video_comment_stats.csv')


# In[ ]:


#sample 1000 users
user_df_sample = user_df.sample(1000)


# In[ ]:


user_df_sample.head()


# In[ ]:


g = Graph(directed=False)

id = g.vp['id'] = g.new_vp("string")    #Video ID or Author ID
kind = g.vp['kind'] = g.new_vp("int") #Video or User, controls the bipartiteness?

videos_add = defaultdict(lambda: g.add_vertex())
users_add = defaultdict(lambda: g.add_vertex())


#add all videos
for i in range(len(user_df_sample)):
    videoID = video_df['VideoID'].iloc[i]
    v = videos_add[videoID]

#add all users
for i in range(len(user_df_sample)):
    authorID = user_df_sample['AuthorID'].iloc[i]
    u = users_add[authorID]


# add all users and links
for i in range(len(user_df_sample)):
    videoID = user_df_sample['VideoID'].iloc[i]
    authorID = user_df_sample['AuthorID'].iloc[i]

    v = videos_add[videoID]
    id[v] = videoID
    kind[v] = 0

    u = users_add[authorID]
    id[u] = authorID
    kind[u] = 1

    g.add_edge(u, v)

g.videos = [g.vp['id'][v] for v in g.vertices() if g.vp['kind'][v] == 1]
g.users = [g.vp['id'][v] for v in g.vertices() if g.vp['kind'][v] == 0]


# In[ ]:


state = minimize_nested_blockmodel_dl(g)


# In[ ]:


# Ensure the state object is correctly initialized and associated with the graph
print("Number of vertices in the graph:", state.g.num_vertices())

# If the number of vertices is correct, attempt to draw the hierarchy
if state.g.num_vertices() > 0:  # Assuming the graph should have at least one vertex
    try:
        draw_hierarchy(state, layout="bipartite")
    except ValueError as e:
        print("Error drawing hierarchy:", e)
else:
    print("The graph does not contain any vertices.")


# In[ ]:




