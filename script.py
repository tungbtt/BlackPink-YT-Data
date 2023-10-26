import pandas as pd
import requests
import json
from datetime import datetime
import time
from typing import NoReturn
import pandas as pd
import re
import sys

#

CHANNEL_ID = 'UCOmHUn--16B90oW2L6FRR3A'

def extract_artist(title):
    match = re.match(r'(.+?) ', title)
    if match:
        return match.group(1)
    else:
        return None


def get_data(API_KEY):
    # Blackpink
    
    now = datetime.now()

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
    

            if response.status_code == 200:
              ## Extract video IDs from the response
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

    print(len(video_ids))
    ## Get data from each ID
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


    # Create a DataFrame from the video data
    df = pd.DataFrame(videos_data)


    file_path = f'datasets/videos_count_data.json'

    with open(file_path, 'a') as f:
        df_json = df.to_json(orient='records', lines=True)
        f.write(df_json)



    ## CLEAN VIEWS DATA
    path = f'datasets/videos_count_data.json'
    data_list = []
    with open(path) as f:
        for line in f:
            if line.isspace():
                continue  # Skip empty lines
            data = line
            data_list.append(data)

    df = pd.DataFrame(data_list)


    df['dateCount']= pd.to_datetime(df['dateCount'])
    df['date'] = df['dateCount'].dt.date
    df['time'] = df['dateCount'].dt.time


    df = df.sort_values(['date','time'], ascending=False).drop_duplicates(['id', 'date'])
    df = df.sort_values('dateCount').drop(columns = 'dateCount')
    df = df.reset_index(drop=True)


    df['title'] = df['title'].replace("M\V", "MV")
    df['artist'] = df['title'].apply(extract_artist)
    df['artist'] = df['artist'].replace('BLACKPINK\u200b','BLACKPINK')
    df['date'] = df['date'].astype(str)



    file_path = f'datasets/CLEANED_videos_count_data.xlsx'
    with open(file_path, 'w') as f:
        df.to_excel(file_path, index=False)
        
        

def main(api_key):
    get_data(api_key)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Please provide the API_KEY as a command-line argument.")
        sys.exit(1)

    api_key = sys.argv[1]
    main(api_key)