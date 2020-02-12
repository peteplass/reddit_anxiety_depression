import math
import json
import requests
import itertools
import numpy as np
import time
import re
import pickle
import nltk
import matplotlib.pyplot as plt
import seaborn as sns
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
import pandas as pd
from time import sleep
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import StandardScaler, FunctionTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from nltk.sentiment.vader import SentimentIntensityAnalyzer

#I always add this when graphs are goign to be exported
%matplotlib inline
%config InlineBackend.figure_format = 'retina'

#set a seed so that these results have a foundation
np.random.seed(42)

#define the function:
def get_posts(subreddit1, subreddit2, posts):
    """
    subreddit = name of the subreddit as a string
    posts = number of posts for each subreddit NOTE: post request must be greater than or equal to 1000.
    example: posts = 1000 will pull 1000 posts for each subreddit, totalling 2000 posts
    
    """
    if int(posts) < 1000:
        print("Post request exceeds minimum, please enter a post request of 1000 or greater")
        return
    
#     setting a timer
    t0 = time.time()
    base_url = 'https://api.pushshift.io/reddit/search/submission'
    json_list = []
    
#     note: these anchor dates are pulled from the most recent reddit postings
    sub1_anchor_date = 1580143995
    sub2_anchor_date = 1580143995
    post_count = posts
    
#     Here I'm using a while loop that checks in every 1000 posts. 1000 is the max number of posts that Reddit will let me pull at once. 
    while post_count >= 1000:
        
#     Because, we'll be pulling from two seperate Reddits, they require different parameters
#     Here we set parameters for the first subreddit pull
#     Note that all json files will be going into the same list. 
        
        params = {
        "subreddit" : subreddit1,
        "size" : 1000,
        'before': sub1_anchor_date
        }

        sub1_data = requests.get(base_url,params)
        print(f'Reddit status code : {sub1_data.status_code}')
        print(f'{post_count} {subreddit1} posts left to fetch')
        try: 
            sub1_anchor_date = sub1_data.json()['data'][-1]['created_utc']
        except:
            pass
        json_list.append(sub1_data)
        
#    Here we are setting parameters for the second subreddit pull 
        params = {
        "subreddit" : subreddit2,
        "size" : 1000,
        'before': sub2_anchor_date
        }
        
        sub2_data = requests.get(base_url,params)
        print(f'{post_count} {subreddit2} posts left to fetch')
        try: 
            sub2_anchor_date = sub2_data.json()['data'][-1]['created_utc']
        except:
            pass
        json_list.append(sub2_data)
        
        
#    Reducing the post count will let the function know when it's done.       
        post_count -= 1000
        
    
#     Collection of data is completed. Now I will convert the data into a dataframe to be more easily explored.   
    reddit_df = []
    for i in range(len(json_list)):
        reddit_df.append(pd.DataFrame(json_list[i].json()['data']))
    
#     Here I am pulling out the columns that I want to see in the dataframe
    relevant_columns = ['title', 'selftext', 'created_utc', 'num_comments', 'subreddit']
    
#     letting the user know the program didn't freeze
    print('wrapping up...')

# Experimental line to binarize subreddit1 in dataframe column as bool(int)
# df['target_sub'] = (df['subreddit'] == f'{subreddit1}').astype(int)
    
    df_output= pd.concat(reddit_df, sort = True)[relevant_columns]
    
#     make sure that our dupicates are dropped
    df_output.drop_duplicates()
    
#     Here I will reset my index so that I don't have multiple instances of index 0 - 999
    df_output.reset_index(inplace = True)
    
    
#     And add some engineered columns that help inform our model. 
    df_output['merged_text'] = df_output['title'] + " " + df_output['selftext']

    
#     Finally, we are returning the output and a print statement that let's us know how long the function was running.   
    print(f'Finished! {len(json_list*1000)} posts collected in {(time.time()-t0)/60} minutes!')
    return df_output
