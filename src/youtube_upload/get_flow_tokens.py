import json
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import requests
import socket
import time

from youtube import get_youtube_tokens


def send_upload_request(msg: str, url: str = "http://127.0.0.1:5000/upload-video"):
    try:
        # Send the upload request
        response = requests.post(url, json=msg, headers={
                                 'Content-Type': 'application/json'})

        # Check the response status code
        return response

    except requests.exceptions.RequestException as e:
        print("An error occurred while sending the upload request:", str(e))
    print(msg)
    return requests.Response()


def wait_until_port_is_available(port: int,max_wait_time:int = 5) -> bool:

    start_time = time.perf_counter()
    
    while True:
        try:
            with socket.create_connection(("localhost", port), timeout=1):
                return True
        except OSError as ex:
            time.sleep(0.01)
            if time.perf_counter() - start_time >= max_wait_time:
                return False

def upload_credentials(channel_info: dict) -> float:
    """
    channel_info:
            {
                "youtube-credentials": {},
                "channels": [{ "channel-id": "@ClipsENG-nb7kx","temp-credentials":"" }]
            }
    """
    videos_uploaded = 0

    port = 8081
    for channel in channel_info["channels"]:
        # try with old credentials
        if "temp-credentials" in channel:
            res = send_upload_request(json.dumps(channel))

            if (res.status_code != 401):  # invalid credentials
                videos_uploaded += 1
                continue

            print("invalid temp credentials trying to get new ones")

        # get new credentials
        if (wait_until_port_is_available(port) == False):
            port += 1

        print("\n\n*****************************************\n\n")
        print("Log into account assosiated with ", channel["channel-id"])
        print("\n\n*****************************************\n\n")

        temp_credentials = get_youtube_tokens(
            channel_info["youtube-credentials"], port=port)

        # try uploading with new credentials

        channel["temp-credentials"] = temp_credentials

        res = send_upload_request(json.dumps(channel))

        if (res.status_code != 401):  # invalid credentials
            videos_uploaded += 1
            continue

        print("invalid temp credentials, skiping channel...")

    return len(channel_info["channels"]) / videos_uploaded


def main():
    channels_json = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "channels.json")

    with open(channels_json, "r") as f:
        channels_credentials = json.load(f)

    for channel in channels_credentials:
        upload_credentials(channel)

    with open(channels_json, "w") as f:
        json.dump(channels_credentials, f)


if __name__ == "__main__":
    main()
