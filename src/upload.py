from firestore.firestore import get_clips_from_firestore
import json
from settings import SETTINGS, YOUTUBE_ID_TO_COMMUNITY_ID, YOUTUBE_UPLOAD_SETTINGS
from youtube_upload.youtube import pipe_bucket_to_youtube, try_refresh_tokens,get_youtube_tokens
from google.oauth2.credentials import Credentials
import time
import socket

def wait_until_port_is_available(port: int,max_wait_time:int = 5) -> bool:

    start_time = time.perf_counter()
    
    while True:
        try:
            with socket.create_connection(("localhost", port), timeout=1):
                return True
        except OSError as ex:
            time.sleep(0.01)
            if time.perf_counter() - start_time >= max_wait_time:
                return False



def main():
    today_videos:list = get_clips_from_firestore()
    community_to_videos = {}

    for video in today_videos:
        video_community:list =  community_to_videos.get(video["community_class",[]])
        video_community.append(video)


    with open("./channels.json","r") as f:
        channels = json.load(f)


    port = YOUTUBE_UPLOAD_SETTINGS["start-port"]
    
    for channel in channels:
        for brand_channel in channel["channels"]:
            
            if isinstance(brand_channel["client-token"],str):
                brand_channel["client-token"] = json.loads(brand_channel["client-token"])

            credentials:Credentials = try_refresh_tokens(brand_channel["client-token"],["https://www.googleapis.com/auth/youtube.upload"])
            
            if credentials is None:
                if wait_until_port_is_available(port) == False:
                    port += 1

                print("\n\n*****************************************\n\n")
                print("Log into account assosiated with ", channel["channel-id"])
                print("\n\n*****************************************\n\n")
                
                credentials = get_youtube_tokens(brand_channel["channel-id"],port)
                
            
            community_id = YOUTUBE_ID_TO_COMMUNITY_ID[brand_channel["channel-id"]]
            
            for video in community_to_videos[community_id]:
                request_body = {
                    'snippet': {
                        'title': video["title"],
                        'description': video["description"],
                        "tags": video["tags"],
                        'category': '22'
                    },
                    'status': {
                        'privacyStatus': 'public'
                    }
                }
                print(SETTINGS["gcp"]["bucket-name"])
                print(video["video-id"])
                print(credentials)

                #pipe_bucket_to_youtube(SETTINGS["gcp"]["bucket-name"],video["video-id"],credentials,request_body)


            channel["credentials"] = credentials.to_json()

    with open("./channels.json","w") as f:
        json.dump(channels,f)

if __name__ == "__main__":
    main()
