import json
from data_collection.communities import Community, Member
import urllib.request
from editing.clip import Clip
from editing.video import Video
from data_collection.helix import Twitch
from youtube_metadata import generate_youtube_data
from settings import SETTINGS
import pickle

# Get communities from Twitch Atlas API or local file
with urllib.request.urlopen(SETTINGS['communities_atlas']) as url:
    data = json.loads(url.read().decode())

# Initialize Twitch API client
twitch = Twitch(client_id=SETTINGS['twitch_client_id'],
                client_secret=SETTINGS['twitch_client_secret'])

#this should be stored in firebase

def load_cached_communities():
    try:
        with open(SETTINGS["communities_cache_path"], "rb") as file:
            return pickle.load(file)
        
    except FileNotFoundError:
        return update_communities_cache()
    
def update_communities_cache():
    
    with open(SETTINGS["communities_cache_path"], "wb") as file:
        communities = get_communities()
        pickle.dump(communities, file)
    
        return communities
    
def get_communities():
    # Process communities and their members
    communities = {}
    for streamer_data in data["nodes"]:
        communities[streamer_data["attributes"]["Modularity Class"]] = communities.get(streamer_data["attributes"]["Modularity Class"],
                                                                                       Community(name=streamer_data["attributes"]["Modularity Class"],
                                                                                                 members=[],
                                                                                                 twitch=twitch))
        new_member = Member()
        new_member.name = streamer_data["label"]
        new_member.size = streamer_data["size"]
        communities[streamer_data["attributes"]
                    ["Modularity Class"]].add_member(new_member)

    # Get member IDs for each community
    for community in communities.values():
        community.get_member_ids()

    return communities

# Process clips for each community


def make_community_general_videos(settings, communities):
    for community_name, community in communities.items():

        clips = community.get_best_community_clips(
            clips_to_get=settings['clips_to_get'], members_to_get=settings['members_to_get'])

        new_video = Video(
            max_duration=settings['max_video_duration'],
            framerate=settings['framerate'],
            width=settings['video_width'],
            height=settings['video_height'],
            aspect_ratio_num=settings['aspect_ratio_num'],
            aspect_ratio_den=settings['aspect_ratio_den'],
            output_options=settings['output_options'],
            output=settings['video_output'])

        if (settings.get("transition", False)):
            new_video.add_transition(Clip(settings["transition"]))

        clips_used = []
        for clip_data in clips:

            new_clip: Clip = Clip(clip_data["video_path"])

            if new_clip.probe == False:
                continue

            new_clip.open_clip(options=settings['clip_options'])

            if not new_video.add_clip(new_clip):
                break

            clips_used.append(clip_data)

        if len(new_video.clips) == 0:
            continue

        video_data = generate_youtube_data(clips_used)

        video_data["ffmpeg_command"] = " ".join(
            new_video.create_ffmpeg_command())
        video_data["community_class"] = community_name

        yield video_data



def make_community_member_videos(settings, communities):

    for community_name, community in communities.items():

        if (not settings["member_video"]):
            break

        community: Community
        clips = community.get_best_member_clips(
            clips_to_get=settings["member_clips_to_get"], top_members=settings["member_top_members"])

        new_video = Video(
            max_duration=settings['max_video_duration'],
            framerate=settings['framerate'],
            width=settings['video_width'],
            height=settings['video_height'],
            aspect_ratio_num=settings['aspect_ratio_num'],
            aspect_ratio_den=settings['aspect_ratio_den'],
            output_options=settings['output_options'],
            output=settings['video_output'])

        if (settings.get("transition", False)):
            new_video.add_transition(Clip(settings["transition"]))

        clips_used = []
        for clip_data in clips:

            new_clip: Clip = Clip(clip_data["video_path"])

            if new_clip.probe == False:
                continue

            new_clip.open_clip(options=settings['clip_options'])

            if not new_video.add_clip(new_clip):
                break

            clips_used.append(clip_data)
        if len(new_video.clips) == 0:
            continue

        video_data = generate_youtube_data(clips_used)

        video_data["ffmpeg_command"] = " ".join(
            new_video.create_ffmpeg_command())
        video_data["community_class"] = community_name


        yield video_data