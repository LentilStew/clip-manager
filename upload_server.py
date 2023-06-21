from typing import Union
import os
import datetime
from firestore import get_clips_from_firestore
import json
from flask import Flask, request
from googleapiclient.discovery import build, MediaFileUpload
from google.oauth2.credentials import Credentials
app = Flask(__name__)


def upload_video_to_youtube(credentials: Credentials, media: MediaFileUpload, body: dict) -> str:

    # Create a service object for the YouTube Data API.
    try:
        service = build('youtube', 'v3', credentials=credentials)
        response = service.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        ).execute()
        return response['id']

    except Exception as e:
        print("UNEXEPECTED ERROR\n", e)
        return ""


GCP_BUCKET_PATH = ""

def get_date_path(date: datetime.date = None):
    if date is None:
        date = datetime.date.today()
    return "{}/{:02d}/{:02d}/".format(date.year, date.month, date.day)
    # Rest of the function code


@app.route('/upload-video', methods=['POST'])
def upload_video():
    upload_info = json.loads(request.get_json())
    token_str: str = upload_info.get("temp-credentials", None)

    community_id: int = upload_info.get("community-id", None)
    channel_id: str = upload_info.get("channel-id", None)
    if (community_id is None or channel_id is None or token_str is None):
        return 'Invalid request.', 400

    token: dict = json.loads(token_str)
    get_date_path()
    #print(community_id, channel_id)
    #print(json.dumps(token, indent=4))

    today_videos_info = get_clips_from_firestore()
    #today_video_paths = os.listdir(os.path.join( GCP_BUCKET_PATH,get_date_path()))
    today_video_paths = ["Attackerdota's Best Clips of June 2023", "Autophil's Best Clips of June 2023", "BoomerNA's Best Clips of June 2023", "ClintStevens's Best Clips of June 2023", "Genburten's Best Clips of June 2023", "GloriaMatvien's Best Clips of June 2023", "GreenishMonkey's Best Clips of June 2023", "Grimnax's Best Clips of June 2023", "Heideltraut's Best Clips of June 2023", "Kephrii's Best Clips of June 2023", "Lazvell's Best Clips of June 2023", "MSStudio's Best Clips of June 2023",
                         "Mazarin1k's Best Clips of June 2023", "PavelskiBH's Best Clips of June 2023", "RedBeard's Best Clips of June 2023", "Sick_Nerd's Best Clips of June 2023", "Tealzlol's Best Clips of June 2023", "TenZ's Best Clips of June 2023", "brycent's Best Clips of June 2023", "demonzz1's Best Clips of June 2023", "goncho's Best Clips of June 2023", "gskianto's Best Clips of June 2023", "iamSometimes's Best Clips of June 2023", "itmeJP's Best Clips of June 2023", "xChocoBars's Best Clips of June 2023"]
    for video in today_videos_info:
        if not (video["title"] in today_video_paths and video["community_class"] == str(community_id)):
            continue
        request_body = {
            'snippet': {
                'title': video.get("title", None),
                'description': video.get("description", None),
                "tags": video.get("tags", []),
                'category': '22'
            },
            'status': {
                'privacyStatus': 'public'
            }
        }
        
        full_path = os.path.join(GCP_BUCKET_PATH,get_date_path(), video["title"])
        media = MediaFileUpload(full_path, chunksize=1024 * 1024, mimetype='video/mp4')
        upload_video_to_youtube()
    return "", 200

    """
    "channel-id": "@ClipsENG-nb7kx",
    "community-id": 0,
    "temp-credentials
    msg: dict = json.loads(request.get_json())

    temporary_credentials = msg.get('credentials', None)
    community = msg.get('community-number', None)

    if temporary_credentials is None and community is None:
        return 'Invalid request.', 400

    
    # files = get_video_files_from_today()
    files = [os.path.dirname(
        os.path.abspath(__file__))
        + "/2023_06_16_BALEROSTYLE's Best Clips of June 2023"]

    for clip in today_videos_info:

        if clip["community_class"] != str(community):
            continue

        clip["title"] = files[0]
        if clip["title"] not in files:
            continue

        file_index = files.index(clip["title"])
        clip["file_name"] = files[file_index]

        request_body = {
            'snippet': {
                'title': clip.get("title", None),
                'description': clip.get("description", None),
                "tags": clip.get("tags", []),
                'category': '22'
            },
            'status': {
                'privacyStatus': 'public'
            }
        }
        print(GCP_BUCKET_PATH+clip["file_name"])
        media = MediaFileUpload(GCP_BUCKET_PATH+clip["file_name"], chunksize=1024 * 1024, mimetype='video/mp4')

        try:
            print("Uploading !!!!")
            upload_video_to_youtube(Credentials(**temporary_credentials), media, request_body)
        except Exception as e:
            return e,401
        
    return 200
    """


if __name__ == '__main__':
    app.run(debug=True)
