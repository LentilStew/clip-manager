import ffmpeg


class Clip:
    def __init__(self, file_path):

        self.file_path = file_path

        self.probe = False
        self.is_open = False
        streams_info,self.format = get_clip_data(self.file_path)
        
        if not streams_info and not self.format:
            print("Invalid input",file_path)
            return None
        self.video_info = None
        self.audio_info = None

        self.probe = True
        for stream in streams_info:
            if stream["codec_type"] == "video":
                self.video_info = stream
            elif stream["codec_type"] == "audio":
                self.audio_info = stream

        self.duration = float(self.format["duration"])

        self.video = None
        self.audio = None

    def to_json(self):
        clip_as_json = {}
        clip_as_json["file_path"] = self.file_path
        clip_as_json["duration"] = self.duration
#        clip_as_json["ffmpeg_data"] = {
#            "format": self.format,
#            "video_stream": self.video_info,
#            "audio_stream": self.audio_info
#        }
        
        return clip_as_json

    def open_clip(self, options = {}):
        
        self.clip = ffmpeg.input(self.file_path, **options)
        
        self.video = self.clip.video
        self.audio = self.clip.audio
        #TODO: Did not test if vnullsrc is a real option
        # and I think this should be done in the video instead of here
        if not self.audio_info:
            #output goes forever without the =cl=mono and the -t 1 , don't know what they mean. Source https://stackoverflow.com/questions/42147512/ffmpeg-adding-silence-struggling-to-use-i-anullsrc-option
            self.audio = ffmpeg.input("anullsrc=cl=mono",f="lavfi", t="1")
        if not self.video_info:
            self.video_info = ffmpeg.input("vnullsrc",f="lavfi")
        
        self.is_open = True

        return self


def get_clip_data(path: str) -> dict:

    try:
        probe = ffmpeg.probe(path)

    except ffmpeg.Error as e:

        print("Failed probing the file")

        return None, None

    return probe['streams'], probe['format']
