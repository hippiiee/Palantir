#!/usr/bin/env python
# coding: utf-8
# Clustering Github users

# Import
import pandas as pd
from pandas.io.json import json_normalize
import json
import matplotlib.pyplot as plt
import re
import os
import logging


# ML import
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.cluster.hierarchy import linkage
import scipy.cluster.hierarchy as shc
from scipy.cluster.hierarchy import fcluster
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, leaves_list
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_distances
import seaborn as sns
import warnings


# Path: app/core/clustering.py
def get_data(path):
    # Read the JSON file
    with open(path, 'r') as f:
        data = json.load(f)

    # Extract the desired item from the JSON data
    item = data['stargazers']

    # Flatten the JSON data into a Pandas DataFrame
    df = pd.json_normalize(item)
    df = df.loc[:, ['name', 'starred', 'followers', 'following']]
    return df

def clean_data(df):
    # Clean data
    df['following'] = df['following'].apply(lambda x: " ".join(x).lower())
    df['following'] = df['following'].apply(lambda x: re.sub(r'[^a-z0-9 ]', '', x))
    df['followers'] = df['followers'].apply(lambda x: " ".join(x).lower())
    df['followers'] = df['followers'].apply(lambda x: re.sub(r'[^a-z0-9 ]', '', x))
    df['starred'] = df['starred'].apply(lambda x: " ".join(x).lower())
    df['starred'] = df['starred'].apply(lambda x: re.sub(r'[^a-z0-9 ]', '', x))
    return df
    
def tfidf(df):
    # TF-IDF implementation
    tfidf = TfidfVectorizer()

    # Following
    tfidf_matrix_following =  tfidf.fit_transform(df['following'])
    following_df = pd.DataFrame(tfidf_matrix_following.toarray(), columns=tfidf.get_feature_names_out())

    # Followers
    tfidf_matrix_followers =  tfidf.fit_transform(df['followers'])
    followers_df = pd.DataFrame(tfidf_matrix_followers.toarray(), columns=tfidf.get_feature_names_out())

    # Starred
    tfidf_matrix_starred =  tfidf.fit_transform(df['starred'])
    followers_df = pd.DataFrame(tfidf_matrix_starred.toarray(), columns=tfidf.get_feature_names_out())
    return tfidf_matrix_following, tfidf_matrix_followers, tfidf_matrix_starred
    
def distance_matrix(tfidf_matrix_following, tfidf_matrix_followers, tfidf_matrix_starred, df):
    # Distance matrix
    distance_matrix_fing = cosine_distances(tfidf_matrix_following)
    distance_df_following = pd.DataFrame(distance_matrix_fing, index=df['name'], columns=df['name'])

    distance_matrix_fer = cosine_distances(tfidf_matrix_followers)
    distance_df_followers = pd.DataFrame(distance_matrix_fer, index=df['name'], columns=df['name'])

    distance_matrix_starred = cosine_distances(tfidf_matrix_starred)
    distance_df_starred = pd.DataFrame(distance_matrix_starred, index=df['name'], columns=df['name'])
    return distance_matrix_fing, distance_matrix_fer, distance_matrix_starred
    
def global_distance(distance_matrix_fing, distance_matrix_fer, distance_matrix_starred, df):
    global_distance = (70*distance_matrix_fing + 23*distance_matrix_fer + 7*distance_matrix_starred)/100
    distance_df = pd.DataFrame(global_distance, index=df['name'], columns=df['name'])
    return global_distance
    
def linkage_matrix(global_distance, df):
    # Suppress warnings
    warnings.simplefilter(action='ignore')
    # Linkage matrix
    link_matrix = shc.linkage(global_distance, method='ward')
    indices = leaves_list(link_matrix)
    labels = df.iloc[indices]['name']
    return link_matrix, indices, labels
    
def export_dendrogram(link_matrix):
    dendrogram(link_matrix)
    # Dendrogram
    plt.savefig('../out/dendrogram.png', format='png')
    
def cluster(link_matrix, global_distance, df):
    # Cluster
    cluster = fcluster(link_matrix, 0.5*global_distance.max(), criterion='distance')
    df['cluster'] = cluster
    return df
    
def export_cluster(link_matrix, df):
    clusters = fcluster(link_matrix,t=1.3, criterion='distance')
    df_clust = pd.DataFrame({'Cluster':clusters, 'Features':df['name']})
    df_clust = df_clust.sort_values(by=['Cluster'])
    df_clust.to_csv('../out/cluster.csv', index=False)
    
def file_clustering_process(path):
    # Get data
    df = get_data(path)
    # Clean data
    df = clean_data(df)
    # TF-IDF implementation
    tfidf_matrix_following, tfidf_matrix_followers, tfidf_matrix_starred = tfidf(df)
    # Distance matrix
    distance_matrix_fing, distance_matrix_fer, distance_matrix_starred = distance_matrix(tfidf_matrix_following, tfidf_matrix_followers, tfidf_matrix_starred, df)
    # Global distance
    gdistance = global_distance(distance_matrix_fing, distance_matrix_fer, distance_matrix_starred, df)
    # Linkage matrix
    link_matrix, indices, labels = linkage_matrix(gdistance, df)
    # Dendrogram
    export_dendrogram(link_matrix)
    # Cluster
    df = cluster(link_matrix, gdistance, df)
    # Export cluster
    export_cluster(link_matrix, df)

def global_clustering():
    for file in os.listdir('../download/'):
        if file.endswith(".json"):
            path = '../download/' + file
            file_clustering_process(path)
        else:
            logging.info('No JSON file found')