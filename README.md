# Community Highlights Bot

The Community Highlights Bot is a Python script that automatically generates highlight videos for Twitch communities and their members. It uses the Twitch API to retrieve data about the top clips from each community and member, and then uses FFmpeg to edit the clips together into a single video.

# Technologies used
It uses python, firestore, streamlit, FFmpeg, the twitch api, and the data analisys done in this github project [VisualizingTwitchCommunities
](https://github.com/KiranGershenfeld/VisualizingTwitchCommunities).

## settings.py
In this file you load the default settings for the project, and it also loads the secret settings from the streamlit secrets

## youtube_metadata.py
In this file there is a function that creates the youtube title description and tags from the clips 

## get_videos.py
This file first uses the twitch api to  find the twitch IDs from the streamers in the atlas website, then there are 2 functions both are used to find the best clips from each streamer

## firestore.py
This file is used to communicate with the Firestore server for both writing and reading.

## /ui/render.py
This file is used to render the website using Streamlit.

## /editing/clip.py /editing/video.py
These are classes that represent clips and videos, respectively. They use FFmpeg to retrieve data from the videos, such as video duration. The video.py file generates the FFmpeg command that creates the video.

## /data_collection/communities.py
this is a class that represents the communities from the atlas website

## /data_collection/helix.py
this file is were the twitch api is used

#### Video Demo:  <https://www.youtube.com/watch?v=zlAnIl0_3QY&feature=youtu.be&ab_channel=GabrielAyala>
