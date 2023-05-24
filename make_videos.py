from firestore import get_clips_from_firestore
import subprocess
import datetime
from typing import Union

def run_ffmpeg_commands_for_date(date = datetime.datetime.now()):
    clips = get_clips_from_firestore(date)

    for clip in clips:
        ffmpeg_command = clip.get('ffmpeg_command')
        if ffmpeg_command:
            subprocess.run(ffmpeg_command, shell=True, check=True, stdout=subprocess.PIPE)

