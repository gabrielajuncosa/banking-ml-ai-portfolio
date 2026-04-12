#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 16:12:55 2024

@author: gabrielajuncosa
"""

import re
import os
import time
import math
import pickle

import pandas as pd 
import numpy as np


def listDIR(path):
    """
    Parameters
    ----------
    path : directory where folder with files is in
    
    Returns
    -------
    aux : list of files in this folder 

    """
    aux = os.listdir(path)
    try:
        aux.remove('.DS_Store') # FOR MAC ONLY
    except:
        pass
    try: 
        aux.remove('.ipynb_checkpoints')# FOR MAC ONLY
    except:
        pass
    return aux


def savedataset(SAVEdirectory, SAVEfilename, SAVEobject):
    save_filename = '%s/%s' % (SAVEdirectory, SAVEfilename)
    pickle.dump(SAVEobject, open(save_filename,'wb'))
    
def openFile(videos_directory,vid):
    filename = '%s/%s' % (videos_directory,vid)
    with open(filename, 'rb') as f:
        file = pickle.load(f)
    return(file)

def partBoolean(row,parte_i):
    label = False
    if row['index'] in parte_i:
        label = True
    return label

os.chdir('/Users/gabrielajuncosa/Documents/YouTube')
path = os.getcwd() 
channels = ['ABC','Fox','CNN','CBS','Newsmax','OAN']

vid_counts = pd.DataFrame()
user_counts = pd.DataFrame()
for channel in channels:
    print(channel)
    # paper data 
    SOURCE_directory = path + '/Data/Comments/' + channel 
    SOURCE_videolist = listDIR(SOURCE_directory)

    for i_, vid in enumerate(SOURCE_videolist):
        k = i_+1
        if k%500 == 0:
            print('%s/%s' % (k,len(SOURCE_videolist)))
        try:
            file = openFile(SOURCE_directory,vid)
            #### COMMENT COUNTS PER VIDEO ####
            activityCounts = np.unique(file['activityType'])
            totComm = 0
            replies = 0
            topComm = 0
            # get replies counts
            if 'reply' in np.unique(file['activityType']):
                i_temp = list(np.unique(file['activityType'],return_counts=True)[0]).index('reply')
                replies = np.unique(file['activityType'],return_counts=True)[1][i_temp]
            # get main level comment counts
            if 'topLevelComment' in np.unique(file['activityType']):
                i_temp = list(np.unique(file['activityType'],return_counts=True)[0]).index('topLevelComment')
                topComm = np.unique(file['activityType'],return_counts=True)[1][i_temp]
            # calculate total counts 
            totComm = topComm+replies
            # get unique users counts
            uniqueU = len(np.unique(file['authorChannelId']))
            # append comment count to large dataset
            df_temp = pd.DataFrame([(channel,file['videoId'][0],totComm,topComm,replies,uniqueU)],
                                   columns =['Channel', 'VideoID', 'TotalComments','MainLevel','Replies','UniqueUsers'])
            vid_counts = pd.concat([vid_counts, df_temp])
            vid_counts.reset_index(drop=True, inplace=True)
            
            #### POST PER USER & VIDEO COUNTS ####
            temp = np.unique(file['authorChannelId'],return_counts=True)
            df_temp = pd.DataFrame({'ChannelID': [channel] * len(temp[0]),
                                    'VideoID': [file['videoId'][0]] * len(temp[0]),
                                    'AuthorID': temp[0],
                                    'PostCount': temp[1]})
            user_counts = pd.concat([user_counts, df_temp])
            user_counts.reset_index(drop=True, inplace=True)
            
        except:
            pass

# Group by 'AuthorID' and sum the 'PostCount' values
author_post_counts = user_counts.groupby('AuthorID')['PostCount'].sum().reset_index()
# Sort the DataFrame by 'PostCount' in ascending order
author_post_counts = author_post_counts.sort_values(by='PostCount', ascending=False)
# Reset Index 
author_post_counts.reset_index(drop=True, inplace=True)
# Display the result
print(author_post_counts)





