import threading
from data_collection.helix import Twitch
from data_collection.communities import Community, load_community
from editing.clip import Clip
from editing.video import Video
import json
import os
import time

finished_adding_clips = False

# open settings.json
with open("settings.json", "r") as f:
    settings = json.load(f)
    community_path = settings["communities"]["save_path"]

video_queue = []


def run_video_queue():
    while True:
        if video_queue:
            video: Video = video_queue.pop(0)
            print("Running video: {}".format(video.title))
            video.make_video()
            print("Finished video: {}".format(video.title))
        elif finished_adding_clips and not video_queue:
            break
        else:
            time.sleep(3)


# run run_video_queue in a separate thread
th = threading.Thread(target=run_video_queue)
th.start()

YOUTUBE_DATA_PATH = "./youtube_data/{}/".format(time.strftime("%Y-%m-%d"))
VIDEO_OUTPUT_PATH = "./videos/{}/".format(time.strftime("%Y-%m-%d"))

if not os.path.exists(YOUTUBE_DATA_PATH):
    os.makedirs(YOUTUBE_DATA_PATH)

if not os.path.exists(VIDEO_OUTPUT_PATH):
    os.makedirs(VIDEO_OUTPUT_PATH)

def create_youtube_info(video: Video, type: str) -> dict:
    if not video.clips:
        print("Video has no clips")
        return {}

    video_json = video.to_json()
    video_json["youtube_data"] = {}
    if video.community:
        community_name = video.community.name
        language = video.community.language
    else:
        community_name = "twitch"
        language = "en"

    streamer_name = community_name
    for clip in video.clips:
        clip: Clip
        if clip.twitch_metadata:
            streamer_name = clip.twitch_metadata["broadcaster_name"]

    if type == "bcd":
        title = settings["youtube"]["templates"][language]["title_template_bcd"].format(
            community_name, time.strftime("%Y-%m-%d"))
        desciption_templates = settings["youtube"]["templates"][language]["description_templates_bcd"]
        Header = desciption_templates["Header"].format(community_name)
        clip_template = desciption_templates["clip_template"]
        footer = desciption_templates["footer"]

    elif type == "bmd":
        title = settings["youtube"]["templates"][language]["title_template_bmd"].format(
            streamer_name, time.strftime("%Y-%m-%d"))
        desciption_templates = settings["youtube"]["templates"][language]["description_templates_bmd"]
        Header = desciption_templates["Header"].format(streamer_name)
        clip_template = desciption_templates["clip_template"]
        footer = desciption_templates["footer"]

    for clip in video.clips:
        clip: Clip
        if clip.twitch_metadata:
            clip_name = clip.twitch_metadata["title"]
            clip_url = clip.twitch_metadata["url"]
            Header += clip_template.format(clip_name, clip_url)

    video_json["youtube_data"]["title"] = title
    video_json["youtube_data"]["description"] = Header + footer

    return video_json

transition = Clip("./inputs/transition.mp4")
transition.open_clip()


# make bmd videos for all communities
for file in os.listdir(community_path):

    curr_community = load_community(community_path + "/" + file)

    clips = curr_community.get_best_member_clips(
        clips_to_get=50, top_members=30)

    title = "bmd-{}-{}".format(
        curr_community.name, time.strftime("%Y-%m-%d"))

    logs_path = "./logs/bmd-{}-{}".format(
        curr_community.name, time.strftime("%Y-%m-%d"))

    # video creation
    new_video = Video(max_duration=60*3,
                      framerate=24,
                      output_options={"vcodec": "libx264", "crf": "18", 
                                      "acodec": "aac", "f": "mp4"},
                      path=VIDEO_OUTPUT_PATH,
                      title= title,
                      community=curr_community,
                      logs_path=logs_path,
                      transition=transition)

    # add clips until video duration is reached
    for clip in clips:

        nuevo = Clip(clip["video_path"], clip)
        if nuevo.probe == False:
            continue

        nuevo.open_clip(options={"vcodec": "h264", "acodec": "aac"})

        if not new_video.add_clip(nuevo):
            break

    video_queue.append(new_video)

    # create youtube info
    youtube_info = create_youtube_info(new_video, "bmd")

    with open(YOUTUBE_DATA_PATH + title + ".json", "w") as f:
        json.dump(youtube_info, f, indent=4)

# make bcd videos for all communities
for file in os.listdir(community_path):

    curr_community = load_community(community_path + "/" + file)

    clips = curr_community.get_best_community_clips(
        clips_to_get=50, members_to_get=30)

    title = "bcd-{}-{}".format(
        curr_community.name, time.strftime("%Y-%m-%d"))

    logs_path = "./logs/bcd-{}-{}".format(
        curr_community.name, time.strftime("%Y-%m-%d"))

    # video creation
    new_video = Video(max_duration=60*10,
                      width=1920,
                      height=1080,
                      framerate=60,
                      output_options={"vcodec": "libx264",
                                      "acodec": "aac", "f": "flv"},
                      community=curr_community,
                      title=title,
                      logs_path=logs_path)

    # add clips until video duration is reached

    for clip in clips:

        nuevo = Clip(clip["video_path"], clip)
        if nuevo.probe == False:
            continue
        nuevo.open_clip(options={"vcodec": "h264", "acodec": "aac"})

        if not new_video.add_clip(nuevo):
            break

    youtube_info = create_youtube_info(new_video, "bcd")

    with open(YOUTUBE_DATA_PATH + title + ".json", "w") as f:
        json.dump(youtube_info, f, indent=4)

finished_adding_clips = True

#wait th to finish
th.join()
