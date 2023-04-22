from dotenv import load_dotenv
from streamlit import secrets
load_dotenv()
SETTINGS = {
    "max_video_duration": 600,
    "framerate": 30,
    "video_width": 1920,
    "video_height": 1080,
    "output_options": {
        "vcodec": "libx264",
        "crf": "18",
        "acodec": "aac",
        "f": "mp4"
    },
    "clip_options": {
        "vcodec": "h264",
        "acodec": "aac"
    },
    "community_video": False,    
    "clips_to_get": 20,
    "members_to_get": 30,
    "member_video": True,
    "member_clips_to_get": 30,
    "member_top_members": 30,

    "communities_atlas": "https://twitchatlas.com/data.json",
    "aspect_ratio_num": 16,
    "aspect_ratio_den": 9,
    "video_output": "output.mp4",
    "output_folder": "./outputs",
    "transition": "./inputs/transition_1s.mp4",
    "firestore-keys-path": "./firestore-key.json",
    "community_title_template": "Best Clips of {creator1}, {creator2} and more! - week {week_num} of {month} {year}",
    "streamer_title_template": "{streamer}'s Best Clips of {month} {year}",
    "description_template": "Check out the best clips of {streamers}! Don't forget to show some love to the creators of these clips.\n\nTimestamps:\n",
    "tags": ["best_clips", "twitch", "stream_highlights"]
}

SETTINGS.update(secrets)