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

data_directory = os.getcwd()[:-4] + 'data/Sentiment_counts/'
figure_directory = os.getcwd()[:-4] + 'figures/'

text_font = 18
latex_preamble = r"\usepackage{times} \usepackage{amsmath} \usepackage{amssymb}"
mpl.rcParams.update({'text.usetex': True,
                            'font.size': 18, 
                            'font.style': 'normal',
                            'font.family':'serif',
                            'text.latex.preamble': latex_preamble,
                            'font.serif': ['Times']})


# In[2]:


channel_names = ['ABC', 'CBS', 'CNN', 'FOX', 'Newsmax', 'OAN']

threshold = [0.5, 0.6, 0.7, 0.8, 0.9]

sentiment = ['TOXICITY', 'INSULT', 'SEVERE_TOXICITY', 'IDENTITY_ATTACK', 'PROFANITY', 'THREAT']


# In[3]:


def axis_decor(ax, text_font, major_length, minor_length, linewidth):

    ax.spines['top'].set_linewidth(0)
    ax.spines['right'].set_linewidth(0)
    ax.spines['bottom'].set_linewidth(linewidth)
    ax.spines['left'].set_linewidth(linewidth)

    ax.tick_params(axis='both', which='major', labelsize=text_font, length=major_length, width=linewidth)
    ax.tick_params(axis='both', which='minor', labelsize=text_font, length=minor_length, width=linewidth)


# In[4]:


df = pd.read_csv(data_directory + f'sentiCounts_ABC.csv')

df


# In[5]:


def channel_toxicity_sentiment(axis_scale):

    for this_channel in channel_names:

        fig, ax = plt.subplots(1,1, figsize= (15, 4))

        df = pd.read_csv(data_directory + f'sentiCounts_{this_channel}.csv')

        xshift = 0.3
        x_shift_marks = [-2*xshift, -xshift, 0, xshift, 2*xshift]
        color_list = ['#ffffb2','#fecc5c','#fd8d3c','#f03b20','#bd0026'][::-1]

        for ts, this_sentiment in enumerate(sentiment):

            for tt, this_threshold in enumerate(threshold):

                this_df = df[df['sentiment'] == this_sentiment+'_'+str(this_threshold)]

                this_data = this_df['N_sentiment'].values[0]
                this_prop = str(np.round(this_df['proportion'].values[0]*100,1))

                ax.bar(2*ts+x_shift_marks[tt], this_data, width = xshift, color = color_list[tt])
                if axis_scale == 'log':
                    ax.text(2*ts+x_shift_marks[tt],this_data*1.1, this_prop, fontsize = text_font-5, ha = 'center', va = 'bottom', rotation = 0)
                elif axis_scale == 'linear':
                    ax.text(2*ts+x_shift_marks[tt],this_data+1e4, this_prop, fontsize = text_font-5, ha = 'center', va = 'bottom', rotation = 0)
                    

        if axis_scale == 'log':
            ax.set_yscale('log')

        ax.set_ylabel('Number of comments', fontsize = text_font)
        xlabels = ['Toxicity', 'Insult', 'Severe\ntoxicity', 'Identity\nattack', 'Profanity', 'Threat']
        xmarks = 2*np.arange(len(sentiment))

        ax.set_xticks(xmarks, xlabels, fontsize = text_font, rotation = 0, ha = 'center')

        axis_decor(ax, text_font, 10, 5, 1)


        plt.tight_layout()
        plt.savefig(figure_directory + f'{this_channel}_sentiment_threshold_{axis_scale}.pdf', dpi=300, format='pdf', bbox_inches='tight')
        # plt.show()
        plt.close()

# channel_toxicity_sentiment('linear')
# channel_toxicity_sentiment('log')


# In[ ]:




