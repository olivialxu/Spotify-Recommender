## ################################## ##
##    Spotify Recommendation System   ##
## ################################## ##
#
# 
# Authors: Olivia Xu, Julia Xi, Roshen Nair
# Date: January 29, 2025
#
#

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
import numpy as np

# This function loads and preprocesses the song database
# using a min-max scaler (most features are not normally
# distributed), then applying principal component analysis
# (PCA) with two components.
#
# @param  filename - path to song database as a csv file
#
# @return df - song database as a dataframe 
#         features - names of relevant features as an array
#         pca_components - principal components from PCA model
#         pca - PCA model fit to df
def load_data(filename):

    # Read data from filename
    df = pd.read_csv(filename)

    # Identify relevant features
    features = ['Energy','Danceability','Liveness','Valence','Acousticness','Speechiness']

    # Normalize data using MinMaxScaler, which sends range of data to [0, 1]
    scaler = MinMaxScaler()
    df[features] = scaler.fit_transform(df[features])

    # Apply PCA with two components
    pca = PCA(n_components=2)
    pca_components = pca.fit_transform(df[features])

    return df, features, pca_components, pca

# This function uses matplotlib.pyplot to display three plots
# to visualize data and features from the database.
#
# @param  df - song database as a dataframe
#         features - names of relevant features as an array
#         pca - PCA model fit to df
#
# @return Plot 1 - displays histogram visualizing distribution of each feature
#         Plot 2 - displays bar graph comparing PCA coefficients
#         Plot 3 - displays bar graph comparing explained variance ratio of
#                  PCA coefficients
def print_data(df, features, pca):

    # Plot distributions of features
    plt.figure(figsize=(12, 8))
    # Iterate over six features and create histograms to visualize distribution of each feature
    for i, feature in enumerate(features, 1):
        plt.subplot(2, 3, i)
        df[feature].hist()
        plt.title(feature)
    plt.tight_layout()
    plt.show()

    # Plot PCA coefficients
    pca_coef = pd.DataFrame(pca.components_, columns=features, index=['PC1', 'PC2'])
    plt.figure(figsize=(10, 6))
    pca_coef.T.plot(kind='bar')
    plt.title('PCA Coefficients')
    plt.tight_layout()
    plt.show()

    # Plot explained variance ratio of principal components
    plt.figure(figsize=(6, 4))
    plt.bar(range(2), pca.explained_variance_ratio_)
    plt.ylabel('Explained Variance Ratio')
    plt.xlabel('Principal Components')
    plt.xticks([1, 2]);
    plt.tight_layout()
    plt.show()

# This function recommends songs to the user given an input song.
# First, the song and its features are extracted from the dataframe.
# Then, we compute the Euclidean distance (in the space of the principal
# components) between the query song and each song in the database.
# Finally, we print the songs closest in distance to the query song.
#
# @param song_title - query song name as a string
#        df - song database as a dataframe
#        features - names of relevant features as an array
#        pca_components - principal components of database from model
#        n - top number of songs recommended; default value is 5
def recommend_songs(song_title, df, features, pca_components, n=5):

    # Convert song title to lowercase for easier comparison
    song_title = song_title.lower()

    # Check that song is in database
    if song_title not in df['Title'].str.lower().values:
        print(f"'{song_title}' not in song database")
        return
    
    # Search for song title in database
    for index, row in df.iterrows():
        if row['Title'].lower() == song_title:
            query_index = index
            break

    # Extract PCA coefficients of query song
    query_pca = pca_components[query_index]

    # Create list to store pairs (song index, distance between song and query song)
    distances = []
    # Iterate through songs in database
    for index, row in df.iterrows():
        # Exclude the query song itself
        if index != query_index:
            # Extract principal components of current song
            song_pca = pca_components[index]
            # Compute Euclidean distance in space of principal components
            dist = np.linalg.norm(song_pca - query_pca)
            # Append index and distance
            distances.append((index, dist))

    # Sort songs in ascending order of distance
    distances = sorted(distances, key=lambda x:x[1])

    # Print features of query song
    # print("FEATURES")
    # print(df.loc[query_index][features])
    # print("\n")

    # Print song recommendations
    print("\nBased on your liked song, we recommend:")
    # Iterate through top n closest songs
    for i, (index, _) in enumerate(distances[:n], 1):
        # Extract row corresponding to current song
        song = df.loc[index]
        # Print title and artist of song
        print(f"{song['Title']}, {song['Artist']}")
        # print("FEATURES")
        # print(song[features].transpose())
        # print("\n")

# This function prints the songs with the highest and lowest PC1 and PC2 
# coefficients. We take the dot product of the feature values and PC1 and
# PC2 coefficients for each song. Then, we sort the songs by PC1 and PC2
# components to identify the songs with the highest and lowest PC coefficients.
#
# @param df - song database as a dataframe
#        features - names of relevant features as an array
#        pca_components - principal components from PCA model
#        pca - PCA model fit to df
def find_top_pca_songs(df, features, pca_components, pca):

    # Create a dataframe containing PCA component coefficients for each feature
    # Rows are principal components, columns are features
    pca_coef = pd.DataFrame(pca.components_, columns=features, index=['PC1', 'PC2'])

    # Create a list to store tuples (song index, PC1, PC2)
    song_pca = []
    # Iterate through each song in the dataset
    for index, row in df.iterrows():
        # Compute the dot product of song features with PCA component coefficients
        pc1_score = np.dot(df.loc[index, features], pca_coef.iloc[0]).item()
        pc2_score = np.dot(df.loc[index, features], pca_coef.iloc[1]).item()
        
        # Append the computed PC1 and PC2 scores
        song_pca.append((index, pc1_score, pc2_score))
    
    # Sort the list based on PC1 values in ascending order
    song_pca = sorted(song_pca, key=lambda x: x[1])
    # Print the song with the lowest PC1 score
    print(f"The song with the lowest PC1 is '{df.loc[song_pca[0][0]]['Title']}' by '{df.loc[song_pca[0][0]]['Artist']}' with a PC1 coefficient of {song_pca[0][1]:.4f}")
    
    # Sort the list based on PC1 values in descending order
    song_pca = sorted(song_pca, key=lambda x: x[1], reverse=True)
    # Print the song with the highest PC1 score
    print(f"The song with the highest PC1 is '{df.loc[song_pca[0][0]]['Title']}' by '{df.loc[song_pca[0][0]]['Artist']}' with a PC1 coefficient of {song_pca[0][1]:.4f}")
    
    # Sort the list based on PC2 values in ascending order
    song_pca = sorted(song_pca, key=lambda x: x[2])
    # Print the song with the lowest PC2 score
    print(f"The song with the lowest PC2 is '{df.loc[song_pca[0][0]]['Title']}' by '{df.loc[song_pca[0][0]]['Artist']}' with a PC2 coefficient of {song_pca[0][2]:.4f}")
    
    # Sort the list based on PC2 values in descending order
    song_pca = sorted(song_pca, key=lambda x: x[2], reverse=True)
    # Print the song with the highest PC2 score
    print(f"The song with the highest PC2 is '{df.loc[song_pca[0][0]]['Title']}' by '{df.loc[song_pca[0][0]]['Artist']}' with a PC2 coefficient of {song_pca[0][2]:.4f}")

# The main function allows the user to ask for a song recommendation,
# print data relating to the song database, or exit the program.
def main():

    # Load song database
    df, features, pca_components, pca = load_data('spotify.csv')

    # Print PC1, 2 song data
    # find_top_pca_songs(df, features, pca_components, pca)

    while True:
        # Prompt user for a command
        command = input("\nEnter 'song lookup', 'print data', or 'exit': ").strip().lower()

        # Ask user for an input song and provide recommendations
        if command == 'song lookup':
            title = input("what's your favorite song: ").strip()
            recommend_songs(title, df, features, pca_components)

        # Print dataset graphs
        elif command == 'print data':
            print_data(df, features, pca)

        # Exit program
        elif command == 'exit':
            print("adios")
            break

        # Manage invalid input
        else:
            print("try again?")

if __name__ == "__main__":
    main()