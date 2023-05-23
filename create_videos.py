from get_videos import make_community_general_videos, make_community_member_videos, get_communities, load_cached_communities, update_communities_cache
from firestore import save_clip_to_firestore
import click
from settings import SETTINGS
from tqdm import tqdm
import json
import sys

@click.command()
def promp_video_settings() -> dict:
    new_settings = SETTINGS
    click.echo("Welcome to the YouTube Video Generator!\n")

    # Ask if default settings should be used or interactive fill
    use_default_settings = click.confirm(
        "Do you want to use the default video/audio settings?")
    if not use_default_settings:
        click.echo("Please fill in the settings below:")
        # Prompt for each setting and update the SETTINGS dictionary
        new_settings["max_video_duration"] = click.prompt(
            "Max video duration (seconds)", type=int)
        new_settings["framerate"] = click.prompt(
            "Framerate", type=int, default=new_settings["framerate"])
        new_settings["video_width"] = click.prompt(
            "Video width", type=int, default=new_settings["video_width"])
        new_settings["video_height"] = click.prompt(
            "Video height", type=int, default=new_settings["video_height"])
        new_settings["aspect_ratio_num"] = click.prompt(
            "Aspect ratio numerator", type=int, default=new_settings["aspect_ratio_num"])
        new_settings["aspect_ratio_den"] = click.prompt(
            "Aspect ratio denominator", type=int, default=new_settings["aspect_ratio_den"])
        new_settings["output_options"]["vcodec"] = click.prompt(
            "Output video codec", default=new_settings["output_options"]["vcodec"])
        new_settings["output_options"]["acodec"] = click.prompt(
            "Output audio codec", default=new_settings["output_options"]["acodec"])
        new_settings["clip_options"]["vcodec"] = click.prompt(
            "Clip video codec", default=new_settings["clip_options"]["vcodec"])
        new_settings["clip_options"]["acodec"] = click.prompt(
            "Clip audio codec", default=new_settings["clip_options"]["acodec"])
        new_settings["video_output"] = click.prompt(
            "Video output filename", default=new_settings["video_output"])
        new_settings["output_folder"] = click.prompt(
            "Output folder", default=new_settings["output_folder"])
        new_settings["transition"] = click.prompt(
            "Transition filename", default="")

        if new_settings["transition"] == "":
            new_settings["transition"] = None

    # Ask if a community video should be made
    create_community_video = click.confirm(
        "Do you want to make a community video?")
    
    new_settings["community_video"] = create_community_video
    
    if create_community_video:
        new_settings["clips_to_get"] = click.prompt(
            "Number of clips to get", type=int, default=new_settings["clips_to_get"])
        new_settings["members_to_get"] = click.prompt(
            "Number of members to get", type=int, default=new_settings["members_to_get"])

    # Ask if member videos should be included
    include_member_videos = click.confirm("Do you want to include member videos?")

    new_settings["member_video"] = include_member_videos
    

    if include_member_videos:
        new_settings["member_clips_to_get"] = click.prompt(
            "Number of member clips to get", type=int, default=new_settings["clips_to_get"])

    new_settings["save_in_firebase"] = click.confirm("Do you want to save the videos in firebase?")
    new_settings["used_cached_communities"] = click.confirm("Do you want to used cached communities?")
     
    return new_settings


def main():

    if "ui" in sys.argv:
        user_settings = promp_video_settings(standalone_mode=False)
    else:
        user_settings = SETTINGS
        
    click.echo("Getting communities, this may take some time...")
    
    if(user_settings["used_cached_communities"]):
        
        communities = load_cached_communities()
    else:
        communities = update_communities_cache()

    if user_settings["community_video"]:

        for vid in tqdm(make_community_general_videos(settings=user_settings, communities=communities),
                        total=len(communities), desc='Community General Videos', unit='video'):

            if user_settings["save_in_firebase"]:
                save_clip_to_firestore(vid)
            else:
                print(json.dumps(vid))                

    if user_settings["member_video"]:

        for vid in tqdm(make_community_member_videos(settings=user_settings, communities=communities),
                        total=len(communities), desc='Community Member Videos', unit='video'):

            if user_settings["save_in_firebase"]:
                save_clip_to_firestore(vid)
            else:
                print(json.dumps(vid))    

    print(user_settings)


if __name__ == "__main__":
    main()
