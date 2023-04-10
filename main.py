import json
import os
from data_collection.communities import Community, Member
import urllib.request
from alive_progress import alive_it, alive_bar
from editing.clip import Clip
from editing.video import Video
from data_collection.helix import Twitch
from youtube_metadata import generate_youtube_data
import uuid

# Load settings from JSON file
with open('settings.json', 'r') as f:
    settings = json.load(f)

# Get communities from Twitch Atlas API or local file
with urllib.request.urlopen(settings['communities_atlas']) as url:
    data = json.loads(url.read().decode())

# Initialize Twitch API client
twitch = Twitch(client_id=settings['twitch_client_id'], client_secret=settings['twitch_client_secret'])

# Process communities and their members
communities = {}
for streamer_data in data["nodes"]:
    communities[streamer_data["attributes"]["Modularity Class"]] = communities.get(streamer_data["attributes"]["Modularity Class"], Community(name=streamer_data["attributes"]["Modularity Class"], members=[], twitch=twitch))
    new_member = Member()
    new_member.name = streamer_data["label"]
    new_member.size = streamer_data["size"]
    communities[streamer_data["attributes"]["Modularity Class"]].add_member(new_member)

# Get member IDs for each community
for community in communities.values():
    community.get_member_ids()

# Process clips for each community

video_commands = []
for community_name, community in communities.items():
    
    if(not settings["community_video"]):
        break

    print("Finding clips....")
    clips = community.get_best_community_clips(clips_to_get=settings['clips_to_get'], members_to_get=settings['members_to_get'])

    new_video = Video(
        max_duration=settings['max_video_duration'],
        framerate=settings['framerate'],
        width=settings['video_width'],
        height=settings['video_height'],
        aspect_ratio_num=settings['aspect_ratio_num'],
        aspect_ratio_den=settings['aspect_ratio_den'],
        output_options=settings['output_options'],
        output=settings['video_output'])
    
    if(settings.get("transition",False)):
        new_video.add_transition(Clip(settings["transition"]))
        
    print("processing clips...")
    
    clips_used = []
    for clip_data in alive_it(clips):

        new_clip:Clip = Clip(clip_data["video_path"])
        
        if new_clip.probe == False:
            continue

        new_clip.open_clip(options=settings['clip_options'])

        if not new_video.add_clip(new_clip):
            break

        clips_used.append(clip_data)
    
    if len(new_video.clips) == 0:
        print("skiping video because no clips found")
        continue

    video_data = generate_youtube_data(clips_used)

    video_data["ffmpeg_command"] = " ".join(new_video.create_ffmpeg_command())
    video_data["community_class"] =  community_name

    # Convert the data to a JSON string
    json_str = json.dumps(video_data)

    # Save the JSON string to a file
    with open("{outputs}/{id}.json".format(outputs=settings["output_folder"], id=str(uuid.uuid1())), "w") as f:
        f.write(json_str)

video_commands = []
for community_name, community in communities.items():

    if(not settings["member_video"]):
        break

    print("Finding clips....")
    community:Community
    clips = community.get_best_member_clips(clips_to_get=settings["member_clips_to_get"],top_members=settings["member_top_members"])

    new_video = Video(
        max_duration=settings['max_video_duration'],
        framerate=settings['framerate'],
        width=settings['video_width'],
        height=settings['video_height'],
        aspect_ratio_num=settings['aspect_ratio_num'],
        aspect_ratio_den=settings['aspect_ratio_den'],
        output_options=settings['output_options'],
        output=settings['video_output'])

    if(settings.get("transition",False)):
        new_video.add_transition(Clip(settings["transition"]))
    print("processing clips...")
    
    clips_used = []
    for clip_data in alive_it(clips):

        new_clip:Clip = Clip(clip_data["video_path"])
        
        if new_clip.probe == False:
            continue

        new_clip.open_clip(options=settings['clip_options'])

        if not new_video.add_clip(new_clip):
            break

        clips_used.append(clip_data)
    if len(new_video.clips) == 0:
        print("skiping video because no clips found")
        continue


    video_data = generate_youtube_data(clips_used)

    video_data["ffmpeg_command"] = " ".join(new_video.create_ffmpeg_command())
    video_data["community_class"] =  community_name

    # Convert the data to a JSON string
    json_str = json.dumps(video_data)

    # Save the JSON string to a file
    with open("{outputs}/{id}.json".format(outputs=settings["output_folder"], id=str(uuid.uuid1())), "w") as f:
        f.write(json_str)