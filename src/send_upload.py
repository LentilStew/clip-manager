from firestore.firestore import get_clips_from_firestore,change_video_status
import json
from settings import SETTINGS,  YOUTUBE_UPLOAD_SETTINGS
from youtube_upload.youtube import try_refresh_tokens,get_youtube_tokens, upload_video_from_server
from google.oauth2.credentials import Credentials
import threading

def _upload_video_from_server( tokens:str, request_body:str,bucket_name:str,bucket_file:str,gcloud_auth,url="localhost:8080/upload",delete_from_bucket:bool=True):
    res = upload_video_from_server(tokens,request_body,bucket_name,bucket_file,gcloud_auth,url,delete_from_bucket=delete_from_bucket)
    if res is not None:
        change_video_status(bucket_file)
    return res
def main():
    today_videos:list = get_clips_from_firestore()
    community_to_videos = {}

    for video in today_videos:
        community_to_videos[video["community_class"]] =  community_to_videos.get(video["community_class"],[])
        community_to_videos[video["community_class"]].append(video)


    with open(YOUTUBE_UPLOAD_SETTINGS["channels-json-path"],"r") as f:
        channels = json.load(f)


    port = YOUTUBE_UPLOAD_SETTINGS["start-port"]
    nb_retries = YOUTUBE_UPLOAD_SETTINGS["retries"]
    
    threads = []

    
    for channel in channels:
        for brand_channel in channel["channels"]:
            community_id = brand_channel["community-number"]
            
            #this checks if there are any videos to upload
            for video in community_to_videos.get(str(community_id),[]):
                if video.get("uploaded",False) is False:
                    break
                    
            else:
                continue
            
            credentials = None
            if brand_channel.get("client-token") is not None:
                credentials:Credentials = try_refresh_tokens(brand_channel["client-token"],["https://www.googleapis.com/auth/youtube.upload"])
            
            if credentials is None:
                print("\n\n*****************************************\n\n")
                print("Log into account assosiated with ", brand_channel["channel-id"])
                print("\n\n*****************************************\n\n")

                credentials = get_youtube_tokens(channel["client-config"], port,retries=nb_retries)
                if credentials is None:
                    return None
                
                brand_channel["client-token"] = json.loads(credentials.to_json())
                
                with open(YOUTUBE_UPLOAD_SETTINGS["channels-json-path"],"w") as f:
                    json.dump(channels,f)

            
            
            for video in community_to_videos[str(community_id)]:
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
                
                new_thread = threading.Thread(target=_upload_video_from_server, args=(
                    credentials.to_json(),
                    json.dumps( request_body),
                    SETTINGS["gcp"]["bucket-name"],
                    video["id"],
                    YOUTUBE_UPLOAD_SETTINGS["gcloud-key"],
                    YOUTUBE_UPLOAD_SETTINGS["cloud-run-url"]))
                
                new_thread.start()
                threads.append(new_thread)
                
    #await for threads
    for thread in threads:
        thread.join()
        
if __name__ == "__main__":
    main()
    