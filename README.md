See it live!!
(Video generation doesn't work since the server that is running this app doesn't have ffmpeg installed you can only look at videos already made, Example in 2023/04/26, if you want to create your own, clone the repository)
https://lentilstew-clip-manager-main-8ygncl.streamlit.app/
# Community Highlights Bot

The Community Highlights Bot is a Python script that automatically generates highlight videos for Twitch communities and their members. It uses the Twitch API to retrieve data about the top clips from each community and member, and then uses FFmpeg to edit the clips together into a single video.

![Video settings](./readme_images/settings.png)
![Video created](readme_images/video-created-example.png)
## Features

- Automatically generates highlight videos for Twitch communities and their members
- Uses the Twitch API to retrieve data about the top clips from each community and member
- Uses FFmpeg to edit the clips together into a single video
- Customizable settings for video output, clip selection, and more 

## Technologies Used
- Python 
- Firestore 
- Streamlit 
- FFmpeg 
- Twitch API 
- Data analysis done in this GitHub project: [VisualizingTwitchCommunities](https://github.com/KiranGershenfeld/VisualizingTwitchCommunities)

## settings.py
In this file you load the default settings for the project, and it also loads the secret settings from the streamlit secrets

## youtube_metadata.py
In this file there is a function that creates the youtube title description and tags from the clips 

## get_videos.py
This file first uses the twitch api to  find the twitch IDs from the streamers in the atlas website, then there are 2 functions both are used to find the best clips from each streamer

## firestore.py
This file is used to communicate with the Firestore server for both writing and reading information about, both the video and the youtube metadata generated, this data, is then represented in the .

## /ui/render.py
This file is used to render the website using Streamlit.

## /editing/clip.py /editing/video.py
These are classes that represent clips and videos, respectively. They use FFmpeg to retrieve data from the videos, such as video duration. The video.py file generates the FFmpeg command that creates the video.

## /data_collection/communities.py
this is a class that represents the communities from the atlas website

## /data_collection/helix.py
this file is were the twitch api is used
## /requirements.txt
These are the libraries you need to install to use the app
- ffmpeg-python
- python-twitch-client
- google-cloud-firestore
- streamlit

## Usage
To use the Community Highlights Bot, simply run ```streamlit run main.py``` . The bot will retrieve data about the top clips and members from each community and member, and use FFmpeg to edit the clips together into a single video. (This app doesn't run the ffmpeg commands, it just makes them)

## Settings
To use Twitch API and Firebase, you need to obtain credentials by registering your application on Twitch Developer Console and Firebase Console respectively.

Once you've obtained your credentials, you should create a .streamlit/secrets.toml file in your project's root directory and add the following keys with their corresponding values:
### /.streamlit/secrest.toml
```toml
TWITCH_CLIENT_ID="your_twitch_client_id"
TWITCH_CLIENT_SECRET="your_twitch_client_secret"

[FIREBASE_KEY]
TYPE="service_account"
PROJECT_ID="your_project_id"
PRIVATE_KEY_ID="your_private_key_id"
PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nyour_private_key\n-----END PRIVATE KEY-----\n"
CLIENT_EMAIL="your_client_email"
CLIENT_ID="your_client_id"
AUTH_URI="https://accounts.google.com/o/oauth2/auth"
TOKEN_URI="https://oauth2.googleapis.com/token"
AUTH_PROVIDER_X509_CERT_URL="https://www.googleapis.com/oauth2/v1/certs"
CLIENT_X509_CERT_URL="your_client_x509_cert_url"
```


You can also change the appearence of the website with 
### /.streamlit/config.toml
```toml
[theme]
base="dark"
secondaryBackgroundColor="#141616"
```
