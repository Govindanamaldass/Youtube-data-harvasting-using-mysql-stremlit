# Import necessary libraries
import streamlit as st# A Python library for creating web apps
import pandas as pd  # A library for data manipulation and analysis
import numpy as np  # A library for numerical computations
from pprint import pprint
 # Import libraries for Google Sheets API
import googleapiclient.discovery  # A library for Google API client
 
api_key = 'AIzaSyAh_ajCgEPccQR1DgsateTWWmYbXLAcYIY'
api_service_name = "youtube"
api_version = "v3"
 
youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)
 
 
import mysql.connector
 
conn = mysql.connector.connect(host='localhost',username='root',password='',database='youtube_project')
cursor = conn.cursor()
conn.commit()
 
 
cursor.execute('''create table if not exists channel_details(channel_name VARCHAR(225),
                                                            publish_at VARCHAR(225),
                                                            playlist_id VARCHAR(225),
                                                            sub_count VARCHAR(225),
                                                            vid_count VARCHAR(225))''')
conn.commit()
 
 
cursor.execute('''create table if not exists video_ids(video_id VARCHAR(150))''')
conn.commit()
 
 
cursor.execute('''create table if not exists video_detail(channel_name VARCHAR(225),
                                                           video_id VARCHAR(225),
                                                           title VARCHAR(225),
                                                           published_date VARCHAR(225),
                                                           duration VARCHAR(225),
                                                           views VARCHAR(225),
                                                           likes VARCHAR(225),
                                                           commments VARCHAR(225)                                      
                                                            )''')
conn.commit()
 
 
cursor.execute('''create table if not exists comment_detail(comment_Text text,
                                                            comment_Author VARCHAR(225),
                                                            comment_Published VARCHAR(225),
                                                            video_id VARCHAR(225))''')
conn.commit()
 
 
def get_channel_detail( channel_id ):
   request = youtube.channels().list(
       part="snippet,contentDetails,statistics",
       id = channel_id
       )
   response = request.execute()
 
   channel_data = {
    "channel_name" : response['items'][0]['snippet']['title'],
    "publish_at" : response['items'][0]['snippet']['publishedAt'],
    "playlist_id" : response['items'][0]['contentDetails']['relatedPlaylists']['uploads'],
    "sub_count" : response['items'][0]['statistics']['subscriberCount'],
    "vid_count" : response['items'][0]['statistics']['videoCount'],
    }
 
   return channel_data

 
def get_videos_ids(channel_id):
    video_ids=[]
    response=youtube.channels().list(id=channel_id,
                                    part='contentDetails').execute()
    Playlist_Id=response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
 
    next_page_token=None
 
    while True:
        response1=youtube.playlistItems().list(
                                            part='snippet',
                                            playlistId=Playlist_Id,
                                            maxResults=50,
                                            pageToken=next_page_token).execute()
        for i in range(len(response1['items'])):
            video_ids.append(response1['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token=response1.get('nextPageToken')
 
        if next_page_token is None:
            break
    return video_ids
 
 
def get_video_detail(video_ids):
    video_data=[]
    for video_id in video_ids:
        request=youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id,
        )
        response=request.execute()
        for item in response["items"]:
            data =  {"channel_name":item['snippet']['channelTitle'],
                     "video_id":item['id'],
                     "title":item['snippet']['title'],
                     "published_date":item['snippet']['publishedAt'],
                     "duration":item['contentDetails']['duration'],
                     "views":item['statistics'].get('viewCount'),
                     "likes":item['statistics'].get('likeCount'),
                     "comments":item['statistics'].get('commentCount')
            }
            video_data.append(data)
    return video_data
 
 
def get_comment_detail(video_ids):
        comment_data=[]
        for video_id in video_ids:
            request=youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=50
            )
            response=request.execute()
 
            for i in range(len(response['items'])):
                data={
                        "comment_Text":response['items'][i]['snippet']['topLevelComment']['snippet']['textDisplay'],
                        "comment_Author":response['items'][i]['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                        "comment_Published":response['items'][i]['snippet']['topLevelComment']['snippet']['publishedAt'],
                        "video_id":response['items'][i]['snippet']['topLevelComment']['snippet']['videoId']
                     }
                comment_data.append(data)
        return comment_data
 
 
def channel_tables(channel_id):
    channel_data = get_channel_detail(channel_id)
    # To insert the channel data in its respective SQL table :
    cursor = conn.cursor()
 
 
    sql_ch = '''INSERT INTO channel_details(channel_name ,
                                        publish_at ,
                                        playlist_id ,
                                        sub_count ,
                                        vid_count) VALUES (%s,%s,%s,%s,%s)'''
    val_ch = tuple(channel_data.values())
    cursor.execute(sql_ch, val_ch)
    conn.commit()
    return channel_data
 
def video_tables(channel_id):
    video_ids=get_videos_ids(channel_id)
    video_data = get_video_detail(video_ids)
 
    # To insert the video data into its respective SQL table :
    vid_detail=[]
    for i in video_data:
        vid_detail.append(tuple(i.values()))
    cursor = conn.cursor()
 
    sql_vi = '''INSERT INTO video_detail(channel_name ,
                                        video_id ,
                                        title ,
                                        published_date ,
                                        duration ,
                                        views ,
                                        likes ,
                                        commments) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'''
 
 
    val_vi = vid_detail
    cursor.executemany(sql_vi, val_vi)
    conn.commit()
    return video_data
 
def comment_tables():
    video_ids= get_videos_ids(channel_id)
    comment_data=get_comment_detail(video_ids)
    # To insert the comment data into its respective SQL table ;
    comment_detail=[]
    for i in comment_data:
        comment_detail.append(tuple(i.values()))
    cursor = conn.cursor()
 
    sql_co = '''INSERT INTO comment_detail(comment_Text,
                                        comment_Author,
                                        comment_Published,
                                        video_id) VALUES (%s,%s,%s,%s)'''
    val_co = comment_detail
    cursor.executemany(sql_co,val_co)
    conn.commit()
 
    return comment_data

st.set_page_config(page_title='Amaldass Streamlit')
st.header('YOUTUBE DATA HARVESTING PROJECT')
st.markdown('_Python scripting, Data Collection, Streamlit, API integration, Data Management using SQL_')
channel_id=str(st.text_input("ENTER CHANNEL ID👉: "))
submit=st.button('Submit channel id')
options = ['select option','show channel details','show video details','show comments']
with st.sidebar:
  selected = st.selectbox("Select table to show", options=options)
 
if selected==options[0]:
    None
 
if selected==options[1]:
    data=channel_tables(channel_id)
    st.dataframe(data)
 
if selected==options[2]:
    data=video_tables(channel_id)
    st.dataframe(data)    
 
if selected==options[3]:
    data=comment_tables()
    st.dataframe(data)