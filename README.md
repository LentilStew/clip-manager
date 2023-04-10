# Community Highlights Bot

The Community Highlights Bot is a Python script that automatically generates highlight videos for Twitch communities and their members. It uses the Twitch API to retrieve data about the top clips from each community and member, and then uses FFmpeg to edit the clips together into a single video.

## Features
Automatically generates highlight videos for Twitch communities and their members
Uses the Twitch API to retrieve data about the top clips from each community and member
Uses FFmpeg to edit the clips together into a single video
Customizable settings for video output, clip selection, and more
Installation
To install the Community Highlights Bot, follow these steps:

## Configuration
The Community Highlights Bot is highly customizable, and allows you to configure a variety of settings to control how the highlight videos are generated. The following settings are available in the settings.json file:

- **twitch_client_id and twitch_client_secret:** Your Twitch API client ID and client secret
- **communities_atlas:** The URL of the Twitch Atlas API endpoint for communities
- **community_video and member_video:** Whether to generate highlight videos for communities and/or members
- **max_video_duration:** The maximum duration of the generated videos, in seconds
- **framerate:** The framerate of the generated videos, in frames per second
- **video_width and video_height:** The width and height of the generated videos, in pixels
- **aspect_ratio_num and aspect_ratio_den:** The aspect ratio of the generated videos
- **output_options:** Additional options to pass to FFmpeg when generating the videos
- **video_output:** The file path for the generated videos
- **clip_options:** Additional options to pass to FFmpeg when processing individual clips

## Usage
To use the Community Highlights Bot, simply run the script using python main.py. The bot will retrieve data about the top clips and members from each community and member, and use FFmpeg to edit the clips together into a single video. (This app doesn't run the ffmpeg commands, it just makes them)
