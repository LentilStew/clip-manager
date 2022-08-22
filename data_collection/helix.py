
import requests
import json
import datetime

class Twitch:
    def __init__(self, client_id: str, client_secret: str) -> None:

        self.client_id = client_id
        self.client_secret = client_secret

        self.path = "https://api.twitch.tv/helix/"
        self.header = {'Client-ID': client_id,
                       'Authorization': "Bearer " + client_secret}
        
        self.path2 = "https://api.twitch.tv/"
        self.header2 = {
            "Accept": "application/vnd.twitchtv.v5+json; charset=UTF-8",
            "Client-Id": client_id
        }


    def get_top_clips(self, broadcaster: int, clips=10, ended_at:datetime.datetime =datetime.datetime.now(), started_at:datetime.datetime=datetime.datetime.now() - datetime.timedelta(days=7)) -> list:
        """clips = twitch.get_top_clips(broadcaster1, clips=5)
            broadcaster, // broadcaster id int
            clips = 10, // number of clips int
            ended_at = (from today), // max date in days datetime.datetime
            started_at = (7 days ago) // min date in days datetime.datetime
        """

        started_at_str = started_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        ended_at_str = ended_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        url = f'{self.path}clips?broadcaster_id={str(broadcaster)}&first={str(clips)}&started_at={started_at_str}&ended_at={ended_at_str}'

        response = requests.get(url, headers=self.header)
        clips_dict = json.loads(response.text.encode('utf-8'))
        
        clips = []
        
        for clip in clips_dict['data']:
        
            video_path = clip['thumbnail_url'][0:clip['thumbnail_url'].find('-preview')]+'.mp4' 

            clip["video_path"] = video_path
            
            #kracken and v5 are disabled Sadge
            
            #clip = {**self.get_clip_info(clip['video_id'],clip["id"]), **clip}
            
            clips.append(clip)

        return clips

    def get_clip_info(self,video_id,clip_id):
        clip_info = {}        
        url = f"{self.path2}kraken/clips/{clip_id}"

        response = requests.get(url, headers=self.header2)
        
        if not response.ok:
            print("kraken ", end="")
            print(response)

            clip_info["start"] = 0
            clip_info["end"] = 0
            clip_info["chat"] = []


        """
        new_info = json.loads(response.text.encode('utf-8'))

        return {}
        clip_info["start"] = new_info["vod"]["offset"]
        clip_info["end"] = new_info["vod"]["offset"] + new_info["duration"]
        clip_info["chat"] = []
        """

        url = "{}v5/videos/{}/comments/?content_offset_seconds={}".format(self.path2,video_id,clip_info["start"])
        response = requests.get(url,headers=self.header2)

        if not response.ok:
            print("v5 ", end="")
            print(response)

        comments = json.loads(response.text.encode('utf-8'))

        comment_info = {}

        end = False

        while True:
            
            for comment in comments["comments"]:
                if(comment["content_offset_seconds"] > clip_info["end"]):
                    end = True
                    break
                
                comment_info["name"] = comment["commenter"]["name"]
                comment_info["text"] = comment["message"]["body"]
                comment_info["time_stamp"] = comment["content_offset_seconds"]

                clip_info["chat"].append(comment_info)
                comment_info = {}
                      
            if(not end and comments["_next"] != None):

                url = "{}v5/videos/{}/comments?cursor={}".format(self.path2,video_id,comments["_next"])
                response = requests.get(url,headers=self.header2)
                comments = json.loads(response.text.encode('utf-8'))

            else:
                break

        return clip_info
