from sys import stdin
import ffmpeg
from data_collection.communities import Community
from editing.clip import Clip
import subprocess
import json
import os

class Video():

    def __init__(self,
                 max_duration=0,
                 framerate=60,
                 width=1920,
                 height=1080,
                 aspect_ratio_num=9,
                 aspect_ratio_den=16,
                 output_options: dict = {},
                 output="./out.mp4") -> None:

        self.max_duration = max_duration
        self.framerate = framerate
        self.width = width
        self.height = height
        self.aspect_ratio_num = aspect_ratio_num
        self.aspect_ratio_den = aspect_ratio_den
        self.output_options = output_options
        self.transition = None
        self.outro = None
        self.output = output
        self.clips = []

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
            joined[0], joined[1], self.output, **self.output_options).overwrite_output()

        args:list = ffmpeg.compile(out, cmd="ffmpeg", overwrite_output=False)

        # join args to string
        #args_str:str = " ".join(args)
        # write args to stdin

        return args

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

