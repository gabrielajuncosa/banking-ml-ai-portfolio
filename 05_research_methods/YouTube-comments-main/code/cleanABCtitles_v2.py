#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 15:00:12 2023

@author: gabrielajuncosa
"""

import os
import re
import openai
#import pickle
import pandas as pd 
import numpy as np 

os.chdir('/Users/gabrielajuncosa/Documents/YouTube/TopicModeling/')
path = os.getcwd() 
path_videoFiles = path + '/results/allVideoInfo_TopicM/'
path_results = path_videoFiles

def listDIR(path):
    aux = os.listdir(path)
    try:
        aux.remove('.DS_Store') # FOR MAC ONLY
    except:
        pass
    return aux

def hashtagWords(hashtag, instruction):
    messages = [ ]
    message = instruction + hashtag
    messages.append(
        {"role": "user", "content": message},
        )
    chat = openai.ChatCompletion.create(
        model ="gpt-3.5-turbo", messages=messages
        )
    reply = chat.choices[0].message.content
    return reply

filenames = listDIR(path_videoFiles)
file = 'allVideoInfo_TopicM_ABC.csv'

df = pd.read_csv(path_videoFiles+file,sep=',')
textTopics = []
check = []
remove = ['#ABCNewsLiveUpdate', '#ABCNewsLivePrime', '#ABCNewsSpecial',
          '#ABCNEWSPRIME', '#ABCNewsPRIME', '#ABCNewsPride', '#ABCNewsPrime',
          '#ABCNewsLive', '#ABCNLPRIME','#ABCNLPRime', '#ABCNLPrime', 
          '#ABCNLUpdate', '#ABCNPRIME', '#ABNLPrime', '#ABCThisWeek', 
          '#ABC2020', '#ABCNEWS',  '#ABNews', '#ABCNEws','#ABCNL', 
          '#ABCNews','#ABCNewws','#ABCnews','#ABCNew', '#ABC','#WorldNewsTonight', 
          '#BreakingNews', '#Nightline', '#ThisWeek', '#TheBreakdown','#TheRundown', 
          'ThisWeek','ABC News Live Update: ','ABC News Prime: ', 'ABC News', 
          'ABC', 'Nightline', '|', 'WNT', 'GMA', 'BREAKING NEWS: ', "'", "`", 
          ":", "’","‘"]

df['Title'] = df['Title'].str.replace(r'\|.*', '', regex=True)
df['Title'] = df['Title'].str.replace(r' l ', ' ', regex=True)
df['Description'] = df['Description'].apply(lambda x: x.splitlines()[0])
df['Description'] = df['Description'].str.replace(r'\#.*', '', regex=True)
df['Text'] = df['Title']  + ' ' +  df['Description']
# del df['cleanText']

for word in remove:
   df['Text'] = df['Text'].str.replace(word, '', regex=True)


