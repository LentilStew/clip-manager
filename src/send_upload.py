from firestore.firestore import get_clips_from_firestore
import json
from settings import SETTINGS, YOUTUBE_ID_TO_COMMUNITY_ID, YOUTUBE_UPLOAD_SETTINGS
from youtube_upload.youtube import try_refresh_tokens,get_youtube_tokens, upload_video_from_server
from google.oauth2.credentials import Credentials


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
    
    for channel in channels:
        for brand_channel in channel["channels"]:

            if isinstance(brand_channel["client-token"],str):
                brand_channel["client-token"] = json.loads(brand_channel["client-token"])

            credentials:Credentials = try_refresh_tokens(brand_channel["client-token"],["https://www.googleapis.com/auth/youtube.upload"])
            
            if credentials is None:
                print("\n\n*****************************************\n\n")
                print("Log into account assosiated with ", brand_channel["channel-id"])
                print("\n\n*****************************************\n\n")

                credentials = get_youtube_tokens(channel["client-config"], port,retries=nb_retries)
                if credentials is None:
                    return None
                
                with open(YOUTUBE_UPLOAD_SETTINGS["channels-json-path"],"w") as f:
                    json.dump(channels,f)

            community_id = YOUTUBE_ID_TO_COMMUNITY_ID.get(brand_channel["channel-id"])
            
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
                
                upload_video_from_server(credentials.to_json(),request_body,SETTINGS["gcp"]["bucket-name"],video["id"],YOUTUBE_UPLOAD_SETTINGS["gcloud-key"],YOUTUBE_UPLOAD_SETTINGS["cloud-run-url"])

            channel["credentials"] = credentials.to_json()



if __name__ == "__main__":
    main()
