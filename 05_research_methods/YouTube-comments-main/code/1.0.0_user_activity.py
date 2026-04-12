#!/usr/bin/env python
# coding: utf-8

# In[1]:


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

data_directory = os.getcwd()[:-4] + 'data/'
figure_directory = os.getcwd()[:-4] + 'figures/'

text_font = 18
mpl.rcParams.update({'font.size': text_font, 'font.style': 'normal', 'font.family':'sans-serif'})


# In[2]:


channel_names = ['ABC', 'CBS', 'CNN', 'FOX', 'Newsmax', 'OAN']


# In[3]:


def axis_decor(ax, text_font, major_length, minor_length, linewidth):

    ax.spines['top'].set_linewidth(0)
    ax.spines['right'].set_linewidth(0)
    ax.spines['bottom'].set_linewidth(linewidth)
    ax.spines['left'].set_linewidth(linewidth)

    ax.tick_params(axis='both', which='major', labelsize=text_font, length=major_length, width=linewidth)
    ax.tick_params(axis='both', which='minor', labelsize=text_font, length=minor_length, width=linewidth)


# In[10]:


for channel in channel_names:

        # paper data 
        all_files = glob.glob(data_directory + channel + '/*')

        for vid in tqdm(all_files):
            

            with open(vid, 'rb') as f:
                data = pickle.load(f)

            print(data['INSULT'])

            break

        break


# In[5]:


def save_user_video_stats():
    #empty lists to store temporary dfs
    temp_vid_counts, temp_user_counts = [], []
    
    for channel in channel_names:

        # paper data 
        all_files = glob.glob(data_directory + channel + '/*')

        for vid in tqdm(all_files):
            
            try:
                with open(vid, 'rb') as f:
                    data = pickle.load(f)

                #### COMMENT COUNTS PER VIDEO ####
                totComm = 0
                replies = 0
                topComm = 0
                
                
                # get replies counts
                if 'reply' in np.unique(data['activityType']):
                    i_temp = list(np.unique(data['activityType'],return_counts=True)[0]).index('reply')
                    replies = np.unique(data['activityType'],return_counts=True)[1][i_temp]
                
                
                # get main level comment counts
                if 'topLevelComment' in np.unique(data['activityType']):
                    i_temp = list(np.unique(data['activityType'],return_counts=True)[0]).index('topLevelComment')
                    topComm = np.unique(data['activityType'],return_counts=True)[1][i_temp]
                
                
                # calculate total counts 
                totComm = topComm+replies
                # get unique users counts
                uniqueU = len(np.unique(data['authorChannelId']))
                
                
                # append comment count to large dataset
                df_temp = pd.DataFrame([(channel,
                                        data['videoId'][0],totComm,
                                        topComm, replies, uniqueU)],
                                columns =['Channel', 
                                        'VideoID', 'TotalComments',
                                        'MainLevel','Replies','UniqueUsers'])
                temp_vid_counts.append(df_temp)

                

                #### POST PER USER & VIDEO COUNTS ####
                temp = np.unique(data['authorChannelId'],return_counts=True)
                df_temp = pd.DataFrame({'ChannelID': [channel] * len(temp[0]),
                                        'VideoID': [data['videoId'][0]] * len(temp[0]),
                                        'AuthorID': temp[0],
                                        'PostCount': temp[1]})
                temp_user_counts.append(df_temp)
                
            except:
                pass

    # combine all dataframes
    vid_counts = pd.concat(temp_vid_counts).reset_index(drop=True)
    user_counts = pd.concat(temp_user_counts).reset_index(drop=True)

    # save to csv
    vid_counts.to_csv(data_directory + 'video_comment_stats.csv', index=False)
    user_counts.to_csv(data_directory + 'user_comment_stats.csv', index=False)

# save_user_video_stats()


# In[6]:


user_df = pd.read_csv(data_directory + 'user_comment_stats.csv')
video_df = pd.read_csv(data_directory + 'video_comment_stats.csv')


# In[7]:


def get_power_law_fit_for_user_distribution(user_df):
    author_post_counts = user_df.groupby('AuthorID')['PostCount'].sum().reset_index()
    # Sort the DataFrame by 'PostCount' in ascending order
    author_post_counts = author_post_counts.sort_values(by='PostCount', ascending=False)
    # Reset Index 
    author_post_counts.reset_index(drop=True, inplace=True)
    #calculate the power law fit
    _user_activity_distribution = author_post_counts['PostCount']

    fit = powerlaw.Fit(_user_activity_distribution, discrete=True)

    return fit, _user_activity_distribution

fit, _user_activity_distribution = get_power_law_fit_for_user_distribution(user_df=user_df)


# In[8]:


def user_activity_distribution_plot(_fit, _user_activity_distribution):

    powerlaw_exponent = np.round(_fit.alpha,2)

    fig, ax = plt.subplots(1,1, figsize=(8,4))

    bin_edges = np.logspace(np.log10(min(_user_activity_distribution)), np.log10(max(_user_activity_distribution)), num=40)
    density, _ = np.histogram(_user_activity_distribution, bins=bin_edges, density=True)

    plt.loglog(bin_edges[:-1], density, marker='o', linestyle=None, linewidth=0,  color='#E3A242',label='data', markersize=7.5)

    ### trying to guess the exponent just by looking a the log-log plot
    x_new = bin_edges[bin_edges>10]
    plt.loglog(x_new, (4e2)*x_new**(-powerlaw_exponent), linestyle='dashed', color='#0E384D', label=fr'$\alpha^{{-{powerlaw_exponent}}}$')

    ax.set_ylabel(r'$P(\alpha)$', fontsize=text_font)
    ax.set_xlabel(r'user activity, $\alpha$', fontsize=text_font)

    axis_decor(ax, text_font, 5, 3, 1)

    ax.legend(frameon=False, fontsize=text_font)

    plt.tight_layout()
    plt.savefig(figure_directory+'user_activity_distribution.png', dpi=300, bbox_inches='tight', format='png')
    plt.show()

user_activity_distribution_plot(_fit=fit, _user_activity_distribution=_user_activity_distribution)


# In[ ]:




