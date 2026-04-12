#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 11:30:01 2023

@author: gabrielajuncosa
"""

import os
import pickle
import pandas as pd
import numpy as np 
from datetime import datetime, timedelta
from time import process_time
import random
import matplotlib.pyplot as plt
import matplotlib

latex_preamble = r"\usepackage{times} \usepackage{amsmath} \usepackage{amssymb}"
matplotlib.rcParams.update({'text.usetex': True,
                            'font.size': 18, 
                            'font.style': 'normal',
                            'font.family':'serif',
                            'text.latex.preamble': latex_preamble,
                            'font.serif': ['Times']})

# os.chdir('/Users/gabrielajuncosa/Desktop/YouTube/')
os.chdir('/Users/gabrielajuncosa/Downloads/plot-sentiments/')
path = os.getcwd() 
# results 
#path_results = path + '/results/'
# paths to files to check 
#path_allData = path + '/data_for_paper/'

# path_auxFiles = '/Users/gabrielajuncosa/Desktop/TopicModeling/auxFiles/'
path_auxFiles = '/Users/gabrielajuncosa/Documents/YouTube/auxFiles/'
path_files = path + '/csv_data/'


with open(path_auxFiles+'dates.json', 'rb') as fp:
    dates = pickle.load(fp)
        
def dayIndex(row):    
    dayIndex = dates[row['year']][row['month']][row['day']]
    return dayIndex

def listDIR(path):
    aux = os.listdir(path)
    try:
        aux.remove('.DS_Store') # FOR MAC ONLY
    except:
        pass
    return aux

breonna_taylor = dates[2020][9][24]
election_day = dates[2020][11][3]
biden_wins = dates[2020][11][7]
trump_questions = dates[2020][11][14]
bidens_transition = dates[2020][11][23]
safe_harbor = dates[2020][12][8]
electoral_votes = dates[2020][12][14]
capitol_attack = dates[2021][1][6]
inauguration = dates[2021][1][20]
daunte_wright = dates[2021][4][11]
dereck_chauvin = dates[2021][4][20]

a=dates.items()

important_dates ={}
important_dates['Breonna Taylor protests']=breonna_taylor
important_dates['Election Day']=election_day
important_dates['Biden declared projected winner']=biden_wins
important_dates['Trump questions results']=trump_questions
important_dates['Biden\'s transition starts']=bidens_transition
important_dates['Safe harbor deadline']=safe_harbor
important_dates['Official electoral voting']=electoral_votes
important_dates['Jan 6 U.S. Capitol Attack']=capitol_attack
important_dates['Biden\'s Inauguration']=inauguration
important_dates['Daunte Wright shot by police']=daunte_wright
important_dates['Dereck Chauvin found guilty']=dereck_chauvin


# READ DIRECTORY AND FILES 
SOURCE_directory = path_files
SOURCE_videolist = listDIR(SOURCE_directory)

allConvs = pd.DataFrame() 
for datafile in SOURCE_videolist:
    df = pd.read_csv(path_files+datafile,sep=',')
    # append to global dataset
    allConvs = pd.concat([allConvs, df], ignore_index=True, sort=False)
    allConvs = allConvs.reset_index(inplace = False)
    del allConvs['index']
print(allConvs.shape)

"""
allConvs = pd.DataFrame()  
for i in range(1,10):
    datafile = 'allConversations_ABC{0}.csv'.format(i)
    df = pd.read_csv(path_results+datafile,sep=',')
    # append to global dataset
    allConvs = pd.concat([allConvs, df], ignore_index=True, sort=False)
    allConvs = allConvs.reset_index(inplace = False)
    del allConvs['index']
print(allConvs.shape)
"""

#umbral = '0.5'
umbrales = np.arange(0.5, 1.0, 0.1)
sentiments = ['TOXICITY','SEVERE_TOXICITY','IDENTITY_ATTACK','INSULT','PROFANITY',
              'THREAT']
vars_to_plot = []
for s in sentiments:
    for u in umbrales:
        varname = str(s) +'_' + str(round(u,1))
        vars_to_plot.append(varname)

"""
colors = ['lightcoral','yellowgreen','darkorange','lightseagreen',
          'firebrick','deepskyblue','gold','mediumorchid']
"""
colors = ['red','blue','green','orange','mediumorchid','yellowgreen','lightcoral']

for s in sentiments:
    s = sentiments[0]
    fig, ax = plt.subplots(layout='constrained',figsize=(15, 5))
    x_label = list(np.arange(1, 242, 7))
    x_time = [datetime(2020,9,1)]
    x_time +=  [x_time[0]+timedelta(int(t)-1) for t in x_label[1:]]
    x_time = [t.strftime('%b %d, %Y') for t in x_time]

    
    # we start with u = 0.5
    u = umbrales[0]
    DF = pd.DataFrame()  
    varname = str(s) +'_' + str(round(u,1))
    z = pd.crosstab(allConvs[varname], allConvs['dayIndex'], dropna=False,normalize='columns')
    DF['days'] = list(z.columns)
    DF['sentiment_prop'] = list(z.iloc[1])
    DF['Rolling'] = DF['sentiment_prop'].rolling(7).mean()
    #x = list(z.columns)
    #data = list(z.iloc[1])
    x = DF['days']
    y = DF['sentiment_prop']
    y2 = DF['Rolling']
    
    ax.plot(x, y,color='k',linewidth=0.7, alpha=.6,label='Daily proportion')
    ax.plot(x, y2,color='#ef8a62',linewidth=1.4, alpha=1,label='Rolling average 10-day window')
    
    # X-AXIS
    ax.set_xticks(x_label)
    ax.set_xticklabels(x_time,rotation=30, fontsize = 10, ha='right')
    
    # Y-AXIS 
    # axis-range and axis-ticks 
    y_max = np.max(y)+0.1
    y_label = [round(y,1) for y in list(np.arange(0.0, y_max, 0.1))]
    ax.set_yticks(y_label)
    ax.set_yticklabels(y_label)#, fontsize = 8)
    # axis text and label
    y_label_text = '\% of '+s+' comments'
    ax.set_ylabel(y_label_text, fontsize=15)
    
    # FIGURE SETTINGS 
    title = 'Timeseries of '+s+' in comments'
    ax.set_title(title, pad=20) # fontsize=16)
    #ax.set(xlim=(0, 243),ylim=(0,y_max))
    ax.set(xlim=(0, 243))

    yannot = ax.get_ylim()[1]
    for k,key in enumerate(list(important_dates.keys())):
        ax.axvline(x = important_dates[key], color = 'gray', 
                   lw=0.7, alpha=.7,linestyle='dashdot')

        if key in ['Biden\'s Inauguration','Dereck Chauvin found guilty']:
            ha='left'
        else:
            ha = 'right'
            
        ax.annotate(key.replace(' ','\n'),
                    (important_dates[key],yannot),
                    fontsize = 11,
                    va='top',
                    ha = ha)
    
    ax.legend(loc='center',bbox_to_anchor=(.5,-.25),fontsize=12,ncols=2)
    

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    figure_name = s+'.pdf'    

    plt.tight_layout()
    plt.savefig(path+'/'+figure_name,format='pdf', dpi=1200)
    #plt.show()
    plt.close()
