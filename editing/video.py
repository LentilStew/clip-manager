from sys import stdin
import ffmpeg
from data_collection.communities import Community
from editing.clip import Clip
import subprocess
import json
import os
title = ""
framerate = ""
max_duration = 0
width = 0
height = 0
aspect_ratio_num = 0
aspect_ratio_den = 0
logs_path = ""
with open("settings.json", "r") as f:
    settings = json.load(f)
    max_duration = settings["video_settings"]["max_duration"]
    width = settings["video_settings"]["width"]
    height = settings["video_settings"]["height"]
    aspect_ratio_num = settings["video_settings"]["aspect_ratio_num"]
    aspect_ratio_den = settings["video_settings"]["aspect_ratio_den"]
    title = settings["video_settings"]["title"]
    framerate = settings["video_settings"]["framerate"]
    logs_path = settings["video_settings"]["logs_path"]


class Video():

    def __init__(self,

                 max_duration=max_duration,
                 title=title,
                 framerate=framerate,
                 width=width,
                 height=height,
                 aspect_ratio_num=aspect_ratio_num,
                 aspect_ratio_den=aspect_ratio_den,
                 output_options: dict = {},
                 transition: Clip = None,
                 outro: Clip = None,
                 path="./",
                 community:Community=None,
                 logs_path=None) -> None:

        self.path = path
        self.max_duration = max_duration
        self.title = title
        self.framerate = framerate
        self.width = width
        self.height = height
        self.aspect_ratio_num = aspect_ratio_num
        self.aspect_ratio_den = aspect_ratio_den
        self.output_options = output_options
        self.transition = transition
        self.outro = outro
        self.community = community
        self.clips = []

        if logs_path:

            if not os.path.exists(logs_path):
                os.makedirs(logs_path)

            self.ffmpeg_stdout = open(logs_path + "/stdout.txt", "wb")
            self.ffmpeg_stdin = open(logs_path + "/stdin.txt", "wb")
            self.ffmpeg_stderr = open(logs_path + "/stderr.txt", "wb")
        else:
            self.ffmpeg_stdout = None
            self.ffmpeg_stdin = None
            self.ffmpeg_stderr = None
            
        return

    def add_transition(self, transition: Clip):

        transition = self.format_clip_audio(transition)
        transition = self.format_clip_video(transition)

        self.transition = transition
        # Not tested yet
        if self.max_duration and self.duration > int(self.max_duration):
            print("Video with this transition exceeds max duration,  trimming last clips")
            while(self.duration < self.max_duration):
                self.clips.pop()

        print("new transition added")

    def add_outro(self, outro: Clip):
        outro = self.format_clip_video(outro)
        outro = self.format_clip_audio(outro)
        self.outro = outro

        # Not tested yet
        if self.max_duration and self.duration > int(self.max_duration):
            print("Video with this outro exceeds max duration,  trimming last clips")
            while(self.duration < self.max_duration):
                self.clips.pop()

        return True

    def add_clip(self, new_clip: Clip) -> bool:

        if not new_clip:
            return False

        if self.max_duration and self.duration + int(float(new_clip.duration)) > int(self.max_duration):
            print("Clip not added because it exceeds max duration")
            return False

        new_clip = self.format_clip_video(new_clip)

        new_clip = self.format_clip_audio(new_clip)

        self.clips.append(new_clip)

        print("new clip added")
        return True

    def format_clip_video(self, video: Clip):

        video.video = video.video.filter(
            'scale', "{}x{}".format(self.width, self.height))

#        video.video = video.video.filter('scale_cuda', "{}x{}".format(self.width, self.height))

        video.video = video.video.filter('fps', "{}".format(self.framerate))

        video.video = video.video.filter(
            "setdar", "{}/{}".format(self.aspect_ratio_den, self.aspect_ratio_num))

        return video

    def format_clip_audio(self, audio):
        return audio

    def make_video(self) -> bool:
        
        command = self.create_ffmpeg_command()
        if not command:
            return False

        self.ffmpeg_stdin.write(" ".join(self.create_ffmpeg_command()).encode())
        process = subprocess.Popen(
            command, stdin=self.ffmpeg_stdin, stdout=self.ffmpeg_stdout, stderr=self.ffmpeg_stderr
        )

        out, err = process.communicate()
        retcode = process.poll()

        return True

    def create_ffmpeg_command(self) -> list:
        if len(self.clips) == 0:
            print("no clips available")
            return False
        
        streams = []

        streams.append(self.clips[0].video)
        streams.append(self.clips[0].audio)

        if self.transition:
            transition_path: str = self.transition.file_path

        for clip in self.clips[1:]:

            if self.transition:
                # Temporary workound for transition FFMPEG doesn't like multiple streams from the same file
                # TODO: fix this

                transition_path = transition_path.replace("/", "//")

                transition = Clip(transition_path)
                transition.open_clip()
                transition = self.format_clip_audio(transition)
                transition = self.format_clip_video(transition)

                streams.append(transition.video)
                streams.append(transition.audio)

            streams.append(clip.video)
            streams.append(clip.audio)

        joined = ffmpeg.concat(*streams, v=1, a=1).node

        out: ffmpeg = ffmpeg.output(
            joined[0], joined[1], self.path + self.title, **self.output_options).overwrite_output()

        args:list = ffmpeg.compile(out, cmd="ffmpeg", overwrite_output=False)

        # join args to string
        #args_str:str = " ".join(args)
        # write args to stdin

        return args


    def to_json(self):
        video_data = {}
        video_data["ffmpeg_command"] = " ".join(self.create_ffmpeg_command())

        video_data["title"] = self.title
        video_data["video_properties"] = {
            "framerate": self.framerate,
            "width": self.width,
            "height": self.height,
            "aspect_ratio_num": self.aspect_ratio_num,
            "aspect_ratio_den": self.aspect_ratio_den
        }

        video_data["expected_duration"] = self.duration
        video_data["clips"] = []
        
        for clip in self.clips:
            video_data["clips"].append(clip.to_json())
        
        if self.transition:
            video_data["transition"] = self.transition.to_json()
        
        if self.outro:
            video_data["outro"] = self.outro.to_json()
        
        return video_data

    @property
    def duration(self) -> int:

        duration = 0.0

        for clip in self.clips:
            duration += clip.duration

        if self.outro is not None:
            duration += self.outro.duration

        if self.transition is not None:
            duration += self.transition.duration * len(
                self.clips) / 2

        return duration

