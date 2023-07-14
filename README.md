# Clip-manager

This project is a set of Python scripts that automatically create and upload videos from Twitch to YouTube.

## Apps

The project consists of the following apps:

* `/src/create_videos.py`: This app uses the Twitch API to create ffmpeg commands, YouTube description, title and tags based on the Twitch communities analysis done in this website https://twitchatlas.com/. Everything is saved in Firebase. It is supposed to run on Cloud Run job (once a day), it's used in Dockerfile-daily and Dockerfile-weekly.
  
* `/src/make_videos.py`: This app uses the videos made with `/src/create_videos.py` and runs the ffmpeg commands. The output is saved to a GCP bucket. It is supposed to run on a VM Instance with as cron job. More information is in `/setup_help.txt`.

* `/src/upload_server.py`: This app is a Flask server that waits for uploads. It is supposed to get the video information and upload it from the bucket to YouTube.It runs on Cloud Run (Dockerfile-upload-server).

* `/src/send_upload.py`: This app checks for new videos in Firebase and for each video sends a request to upload the video to the assigned channel in `/channels.json`. If the channel tokens aren't specified, it will open a Chrome tab so you log in. (You are supposed to run this manually every day, because sometimes you need to relog into the YouTube accounts).

* `settings.py`: All settings for the app.

* `streamlit_website.py`: (Very old not updated) This app shows the Firebase videos in a website. It uses Cloud Run as well (Dockerfile-website).

What the website looks like
![Website](./readme_images/video-created-example.png)
See it live at! https://clip-manager-xmpigou3sq-rj.a.run.app/

## One use Apps
`/src/youtube_upload/create_channel_branding.ipynb:`

Creates banners and pfps for each channel
![Banner example](./readme_images/banner.png)
 
## Secrets

You need the Firebase credentials and the Twitch API credentials in the `secrets/` directory. The YouTube credentials go in `channels.json`, (only 6 brand-channels per channel since the api only allows 6 videos a day)

```json
{
    [
        {
            "client-config": {},
            "channels": [
                {
                    "channel-name": "ENG",
                    "community-number": 0,
                    "channel-id": "@ClipsENG-nb7kx",
                },
                {
                    "channel-name": "ESP",
                    "community-number": 16,
                    "channel-id": "@clipsesp7744",
                }
                ]
        },
                {
            "client-config": {},
            "channels": [
                {
                    "channel-name": "GAME",
                    "community-number": 13,
                    "channel-id": "@ClipsGAME-fu3eb"
                },
                {
                    "channel-name": "OTV",
                    "community-number": 9,
                    "channel-id": "@ClipsOTV-gf2dx"
                }
                ]
        }
    ]
}
```

## Usage

To use the project, you need to:

1. Install the dependencies.
2. Create a Firebase project and add the credentials to the `/secrets/` directory.
3. Create a Twitch API key and add it the credentials to the `/secrets/` directory.
4. Create a YouTube API key and add it to the `channels.json` file.
5. Run the `create_videos.py` app.
6. Run the `make_videos.py` app.
7. Run the `upload_server.py` app.
8. Run the `send_upload.py` app.

## More Information

For more information, please see the [setup_help.txt](setup_help.txt) file.
