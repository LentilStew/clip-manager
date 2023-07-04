import io
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError
import subprocess as sp
import google.cloud.storage
from typing import Union


def get_youtube_tokens(client_config: dict, port: int = 8081) -> Credentials:

    flow = InstalledAppFlow.from_client_config(client_config, scopes=[
        "https://www.googleapis.com/auth/youtube.upload"])
    flow.run_local_server(port=port)

    return flow.credentials


def check_youtube_credentials(token:dict,scopes:dict,client_config:dict, port: int = 8081) -> Credentials:
    if token is None:
        print("No token provided, getting new tokens")
        new_credentials = get_youtube_tokens(client_config, port=port)
        return new_credentials

    try:
        new_credentials:Credentials  = Credentials.from_authorized_user_info(token,scopes)
        new_credentials.refresh(Request())
        return new_credentials
    
    except RefreshError as error:
        print(f'Refresh token expired requesting authorization again: {error}')
        new_credentials = get_youtube_tokens(client_config,port=port)
        return new_credentials

def try_refresh_tokens(token:dict,scopes:dict) -> Union[Credentials,None]:
    try:
        new_credentials:Credentials  = Credentials.from_authorized_user_info(token,scopes)
        new_credentials.refresh(Request())
        return new_credentials
    
    except RefreshError as error:
        print(f'Refresh token expired requesting authorization again: {error}')
        return None

def upload_video_to_youtube(credentials: Credentials, media:MediaIoBaseUpload, body: dict) -> str:

    try:
        service = build('youtube', 'v3', credentials=credentials)
        response = service.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        ).execute()
        return response['id']

    except Exception as error:
        print(f'Error uploading video to youtube: {error}')
        return None
    
#Can't figure out how to do this
def pipe_ffmpeg_to_youtube(ffmpeg_command:list,credentials: Credentials, body: dict):
    with io.open("./video_output", "wb") as file:
        sp.Popen(ffmpeg_command, stdout=file)
    media = MediaIoBaseUpload(file, mimetype='video/mp4')
    upload_video_to_youtube(credentials, media, body)
    

def pipe_bucket_to_youtube(bucket_name:str, bucket_file:str, credentials: Credentials, body: dict):
    
    client = google.cloud.storage.Client()

    bucket = client.bucket(bucket_name)

    blob = bucket.blob(bucket_file)
    
    with blob.open("rb")as f:
        media = MediaIoBaseUpload(f, chunksize=1024 * 1024, mimetype='video/mp4')
        upload_video_to_youtube(credentials, media, body)