from get_videos import make_community_general_videos, make_community_member_videos, get_communities, load_cached_communities, update_communities_cache
from firestore import save_clip_to_firestore
import click
from settings import SETTINGS
from tqdm import tqdm
import json
import sys
import argparse

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

def parse_args():
    new_settings = SETTINGS
    parser = argparse.ArgumentParser(description='YouTube Video Generator')
    # Default settings argument
    parser.add_argument('--default-settings', action='store_true', help='Use default video/audio settings')

    # Video/audio settings arguments
    parser.add_argument('--max-video-duration', type=int, help='Max video duration (seconds)')
    parser.add_argument('--framerate', type=int, help='Framerate')
    parser.add_argument('--video-width', type=int, help='Video width')
    parser.add_argument('--video-height', type=int, help='Video height')
    parser.add_argument('--aspect-ratio-num', type=int, help='Aspect ratio numerator')
    parser.add_argument('--aspect-ratio-den', type=int, help='Aspect ratio denominator')
    parser.add_argument('--output-video-codec', help='Output video codec')
    parser.add_argument('--output-audio-codec', help='Output audio codec')
    parser.add_argument('--clip-video-codec', help='Clip video codec')
    parser.add_argument('--clip-audio-codec', help='Clip audio codec')
    parser.add_argument('--video-output', help='Video output filename')
    parser.add_argument('--output-folder', help='Output folder')
    parser.add_argument('--transition', help='Transition filename')

    # Community video arguments
    parser.add_argument('--include-community-video', action='store_true', help='Make a community video')
    parser.add_argument('--clips-to-get', type=int, help='Number of clips to get')
    parser.add_argument('--members-to-get', type=int, help='Number of members to get')

    # Member video arguments
    parser.add_argument('--include-member-videos', action='store_true', help='Include member videos')
    parser.add_argument('--member-clips-to-get', type=int, help='Number of member clips to get')

    # Firebase arguments
    parser.add_argument('--save-in-firebase', action='store_true', help='Save videos in Firebase')
    parser.add_argument('--use-cached-communities', action='store_true', help='Use cached communities')
    parser.add_argument('--ui', action='store_true', help='Enable UI')
    parser.add_argument('--communities-cache-path', type=str, help='communities cache path')
    

    args = parser.parse_args()
    
    if args.max_video_duration:
        new_settings['max_video_duration'] = args.max_video_duration
    if args.framerate:
        new_settings['framerate'] = args.framerate
    if args.video_width:
        new_settings['video_width'] = args.video_width
    if args.video_height:
        new_settings['video_height'] = args.video_height
    if args.aspect_ratio_num:
        new_settings['aspect_ratio_num'] = args.aspect_ratio_num
    if args.aspect_ratio_den:
        new_settings['aspect_ratio_den'] = args.aspect_ratio_den
    if args.output_video_codec:
        new_settings['output_options']['vcodec'] = args.output_video_codec
    if args.output_audio_codec:
        new_settings['output_options']['acodec'] = args.output_audio_codec
    if args.clip_video_codec:
        new_settings['clip_options']['vcodec'] = args.clip_video_codec
    if args.clip_audio_codec:
        new_settings['clip_options']['acodec'] = args.clip_audio_codec
    if args.video_output:
        new_settings['video_output'] = args.video_output
    if args.output_folder:
        new_settings['output_folder'] = args.output_folder
    if args.transition:
        new_settings['transition'] = args.transition
    if args.save_in_firebase:
        new_settings['save_in_firebase'] = args.save_in_firebase
    if args.use_cached_communities:
        new_settings['use_cached_communities'] = args.use_cached_communities
    if args.ui:
        new_settings['ui'] = args.ui
    if args.communities_cache_path:
        new_settings['communities_cache_path'] = args.communities_cache_path
        
    if args.include_member_videos:
        new_settings['include_member_video'] = args.include_member_videos
    if args.member_clips_to_get:
        new_settings['member_clips_to_get'] = args.member_clips_to_get
        
    if args.include_community_video:
        new_settings['include_community_video'] = args.include_community_video
    if args.clips_to_get:
        new_settings['clips_to_get'] = args.clips_to_get
    if args.members_to_get:
        new_settings['members_to_get'] = args.members_to_get
    return new_settings


def main():
    user_settings = parse_args()
    if hasattr(user_settings,'ui'):
        user_settings = promp_video_settings(standalone_mode=False)
    else:
        user_settings = SETTINGS

    click.echo("Getting communities, this may take some time...")
    
    if user_settings['use_cached_communities']:
        communities = load_cached_communities()
    else:
        communities = update_communities_cache()

    if user_settings["include_community_video"]:
        for vid in tqdm(make_community_general_videos(settings=user_settings, communities=communities),
                        total=len(communities), desc='Community General Videos', unit='video'):

            if user_settings["save_in_firebase"]:
                save_clip_to_firestore(vid)
            else:
                print(json.dumps(vid))                

    if user_settings["include_member_video"]:

        for vid in tqdm(make_community_member_videos(settings=user_settings, communities=communities),
                        total=len(communities), desc='Community Member Videos', unit='video'):

            if user_settings["save_in_firebase"]:
                save_clip_to_firestore(vid)
            else:
                print(json.dumps(vid))    



if __name__ == "__main__":
    main()
