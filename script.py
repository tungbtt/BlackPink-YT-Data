#!/usr/bin/env python
# coding: utf-8

#


#from google.colab import drive
#drive.mount('/content/gdrive')


#


import pandas as pd
import requests
import json

#

API_KEY  = 'AIzaSyAbQn4u-4k2yKXHyGn-l_P2rB4UoPXCQ9M'
CHANNEL_ID = 'UCOmHUn--16B90oW2L6FRR3A'


# https://developers.google.com/youtube/v3/getting-started?hl=vi

# Blackpink

#


from datetime import datetime

now = datetime.now()


#


url = f'https://www.googleapis.com/youtube/v3/channels/?part=snippet,contentDetails,statistics&id={CHANNEL_ID}&key={API_KEY}'


#


channel_info = requests.get(url)


#


data = json.loads(channel_info.text)


#


total = data['items'][0]['statistics']
total['dateCount'] = str(now)

df_total = pd.DataFrame([total])


#


#df_total


#


#file_path = f'/content/gdrive/MyDrive/Documents/BlackpinkData/channel_data.json'
file_path = f'channel_data.json'

with open(file_path, 'a') as f:
    df_json = df_total.to_json(orient='records', lines=True)
    f.write(df_json + '\n')


#


import time


#


# Get all video

# API bị block :<

"""

maxResults = 20
nextPageToken = None
video_ids = []

# Continue fetching video IDs while there are more pages
while True:
    # Define the API endpoint to get channel videos
    url = f'https://www.googleapis.com/youtube/v3/search?channelId={CHANNEL_ID}&order=date&part=snippet&type=video&maxResults={maxResults}'
    if nextPageToken:
        url += f'&pageToken={nextPageToken}'
    url += f'&key={API_KEY}'

    print(url)

    # Make the API request
    response = requests.get(url)
    data = response.json()

    # Check if the request was successful
    if response.status_code == 200:
        # Extract video IDs from the response
        for item in data['items']:
            if item['id']['kind'] == 'youtube#video':
                video_ids.append(item['id']['videoId'])

        # Check if there are more pages
        nextPageToken = data.get('nextPageToken')

        if not nextPageToken:
            break  # Stop if there are no more pages

        #time.sleep(0.5)
    else:
        print('Failed to retrieve video IDs. Status code:', response.status_code)
        print('Error message:', data)
        break

# Print the video IDs
print('Video IDs:', video_ids)

"""


#


from typing import NoReturn
# Get from playlist
playlist_ids = ['PLNF8K9Ddz0kKfujG6blfAxngYh_C66C_q','PLNF8K9Ddz0kI4uLrV7BYrdcebUuMf06z1','PLNF8K9Ddz0kKKkPixGOA_xfLYqUG1QXlF']
video_ids = []
nextPageToken = None


for playlist_id in playlist_ids:

    while True:

        url = f'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet,contentDetails&maxResults=25&playlistId={playlist_id}'

        if nextPageToken:
            url += f'&pageToken={nextPageToken}'
        url += f'&key={API_KEY}'

        response = requests.get(url)
        data = response.json()

        #print(url)

        if response.status_code == 200:
          # Extract video IDs from the response
          for item in data['items']:
            if item['kind'] == 'youtube#playlistItem':

                temp = {}
                temp['videoId'] = item['contentDetails']['videoId']

                if playlist_id == 'PLNF8K9Ddz0kKfujG6blfAxngYh_C66C_q':
                    temp["kind"] = 'Music Video'
                elif playlist_id == 'PLNF8K9Ddz0kI4uLrV7BYrdcebUuMf06z1':
                    temp["kind"] = 'Dance Practice Video'
                else:
                    temp["kind"] = 'Performance'

            video_ids.append(temp)

            # Check if there are more pages
        nextPageToken = data.get('nextPageToken')


        if not nextPageToken:
            break  # Stop if there are no more pages


#


videos_data = []

# Batch video IDs into groups of 20 (maximum allowed by the YouTube API)
max_videos_per_request = 20
video_id_batches = [video_ids[i:i + max_videos_per_request] for i in range(0, len(video_ids), max_videos_per_request)]

# Iterate through video ID batches and make API requests
for batch in video_id_batches:
    # Create a comma-separated string of video IDs
    video_id_str=''

    video_id_str = ",".join(entry['videoId'] for entry in batch)
    kind_dict = {entry['videoId']: entry['kind'] for entry in batch}

    # Define the API endpoint to get video details
    url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails,statistics&id={video_id_str}&key={API_KEY}'

    # Make the API request
    response = requests.get(url)
    data = response.json()

    # Check if the request was successful
    if response.status_code == 200:
        # Extract video data
        for video in data['items']:
            now = datetime.now()
            video_data = {
                'dateCount': str(now),
                'id': video['id'],
                'title': video['snippet']['title'],
                'kind' : kind_dict[video['id']],
                'viewCount': int(video['statistics']['viewCount']),
                'likeCount': int(video['statistics']['likeCount']),
                'commentCount': int(video['statistics'].get('commentCount', 0))
            }
            videos_data.append(video_data)
    else:
        print('Failed to retrieve video details. Status code:', response.status_code)
        print('Error message:', data)


#


# Create a DataFrame from the video data
df = pd.DataFrame(videos_data)

# Print the DataFrame
#display(df)


#


#file_path = f'/content/gdrive/MyDrive/Documents/BlackpinkData/videos_count_data.json'
file_path = f'videos_count_data.json'

with open(file_path, 'a') as f:
    df_json = df.to_json(orient='records', lines=True)
    f.write(df_json + '\n')

#


import pandas as pd
import re


# CLEAN VIEWS DATA

#


#path = f'/content/gdrive/MyDrive/Documents/BlackpinkData/videos_count_data.json'
path = f'videos_count_data.json'
data_list = []
with open(path) as f:
    for line in f:
        if line.isspace():
            continue  # Skip empty lines
        data = eval(line)  # Evaluate non-empty lines
        data_list.append(data)

df = pd.DataFrame(data_list)


#


df.head()


#


num_rows, num_columns = df.shape

print("Num rows: ",num_rows)
print("Num colums: ",num_columns)


#


df.dtypes


#


df['dateCount']= pd.to_datetime(df['dateCount'])

df['date'] = df['dateCount'].dt.date
df['time'] = df['dateCount'].dt.time


#


df = df.sort_values(['date','time'], ascending=False).drop_duplicates(['id', 'date'])


#


df = df.sort_values('dateCount').drop(columns = 'dateCount')
df = df.reset_index(drop=True)


#


#display(df)


#


df['title'] = df['title'].replace("M\V", "MV")


#


def extract_artist(title):
    match = re.match(r'(.+?) ', title)
    if match:
        return match.group(1)
    else:
        return None

df['artist'] = df['title'].apply(extract_artist)


# 


#display(df)


# 


df['artist'].unique()


# 


df['artist'] = df['artist'].replace('BLACKPINK\u200b','BLACKPINK')


# 


#file_path = f'/content/gdrive/MyDrive/Documents/BlackpinkData/CLEANED_videos_count_data.xlsx'
file_path = f'CLEANED_videos_count_data.xlsx'

df['date'] = df['date'].astype(str)

with open(file_path, 'w') as f:
    #df_json = df.to_json(orient='records', lines=True)
    #f.write(df_json + '\n')
    df.to_excel(file_path, index=False)


# CLEAN CHANNEL DATA

# 


import json


# 


#path = f'/content/gdrive/MyDrive/Documents/BlackpinkData/channel_data.json'
path = f'channel_data.json'

data_list = []
with open(path) as f:
    for line in f:
        if line.isspace():
            continue  # Skip empty lines

        data = json.loads(line)
        data_list.append(data)

df_2 = pd.DataFrame(data_list)
#df_2


# 


df_2['dateCount']= pd.to_datetime(df_2['dateCount'])

df_2['date'] = df_2['dateCount'].dt.date
df_2['time'] = df_2['dateCount'].dt.time


# 


df_2 = df_2.sort_values(['date','time'], ascending=False).drop_duplicates(['date'])


# 


df_2 = df_2.sort_values('dateCount').drop(columns = 'dateCount')
df_2 = df_2.reset_index(drop=True)


# 


#file_path = f'/content/gdrive/MyDrive/Documents/BlackpinkData/CLEANED_channel_data.xlsx'
file_path = f'CLEANED_channel_data.xlsx'

df_2['date'] = df_2['date'].astype(str)

with open(file_path, 'w') as f:
    #df_json = df.to_json(orient='records', lines=True)
    #f.write(df_json + '\n')
    df_2.to_excel(file_path, index=False)


