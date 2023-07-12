import json
SETTINGS = {
    "max_video_duration": 600,
    "framerate": 24,
    "video_width": 1920,
    "video_height": 1080,
    "output_options": {
        "vcodec": "libx264",
        "crf": "18",
        "acodec": "aac",
        "f": "nut"
    },
    "clip_options": {
        "vcodec": "h264",
        "acodec": "aac"
    },
    "include_community_video": False,
    "clips_to_get": 20,
    "members_to_get": 30,
    "include_member_video": False,
    "member_clips_to_get": 30,
    "member_top_members": 30,
    
    "communities_atlas": "https://twitchatlas.com/data.json",
    "aspect_ratio_num": 16,
    "aspect_ratio_den": 9,
    "video_output": "-",
    "output_folder": "",
    "transition": "./inputs/transition_1s.mp4",
    "firestore-keys-path": "./firestore-key.json",
    "community_title_template": "Best Clips of {creator1}, {creator2} and more! - week {week_num} of {month} {year}",
    "streamer_title_template": "{streamer}'s Best Clips of {month} {year}",
    "description_template": "Check out the best clips of {streamers}! Don't forget to show some love to the creators of these clips.\n\nTimestamps:\n",
    "tags": ["best_clips", "twitch", "stream_highlights"],
    "save_in_firebase": True,
    "use_cached_communities": False,
    "communities_cache_path": "./data/",
    "communities_cache_filename": "comunity_ids.pickle",
    "gcp":{
        "bucket-name":"clip-manager-videos"
    },
    "quick_video_settings":False
}
YOUTUBE_UPLOAD_SETTINGS = {
    "start-port":8085,
    "retries":24,
    "cloud-run-url": "https://clip-manager-upload-server-xmpigou3sq-uc.a.run.app/upload",
    "channels-json-path": "./channels.json",
    "single_thread" : False,
    "test":False,
    "delete_from_bucket":True
}
    
QUICK_VIDEO_SETTINGS = {
    "include_community_video": True,
    "include_member_video": False,
    "member_clips_to_get": 5,
    "use_cached_communities": True,
    "save_in_firebase": False,
    
    "clips_to_get": 20,
    "members_to_get": 3,
}

with open("./secrets/firebase-credentials.json", "r") as f:
    SETTINGS["firebase-key"] = json.load(f)

with open("./secrets/twitch.json", "r") as f:
    for key, value in json.load(f).items():
        SETTINGS[key] = value
    