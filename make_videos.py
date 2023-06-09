from firestore import get_clips_from_firestore
import subprocess as sp
from typing import Dict, Tuple, Optional, IO, List
import sys
import io
import select
from settings import SETTINGS
from google.cloud import storage
from datetime import datetime
bucket_name = "clip-manager-videos"
client = storage.Client()


def copy_process_streams(process: sp.Popen):
    def raw(stream: Optional[IO[bytes]]) -> IO[bytes]:
        assert stream is not None
        if isinstance(stream, io.BufferedIOBase):
            stream = stream.raw
        return stream

    p_stdout, p_stderr = raw(process.stdout), raw(process.stderr)
    stream_by_fd: Dict[int, Tuple[IO[bytes], io.StringIO, IO[str]]] = {
        p_stdout.fileno(): (p_stdout, sys.stdout),
        p_stderr.fileno(): (p_stderr, sys.stderr),
    }
    fds = list(stream_by_fd.keys())

    while fds:
        # `select` syscall will wait until one of the file descriptors has content.
        ready, _, _ = select.select(fds, [], [])
        for fd in ready:
            p_stream, std = stream_by_fd[fd]
            raw_buf = p_stream.read(2 ** 16)
            if not raw_buf:
                fds.remove(fd)
                continue
            # buf = raw_buf.decode()
            std.write(str(raw_buf))
            std.flush()

def stream_stdout_to_bucket(process: sp.Popen, filename: str, bucket: str):
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)
    bucket_stream = blob.open("wb")
    
    def raw(stream: Optional[IO[bytes]]) -> IO[bytes]:
        assert stream is not None
        if isinstance(stream, io.BufferedIOBase):
            stream = stream.raw
        return stream

    p_stdout, p_stderr = raw(process.stdout), raw(process.stderr)
    stream_by_fd: Dict[int, Tuple[IO[bytes], io.StringIO, IO[str]]] = {
        p_stdout.fileno(): (p_stdout, sys.stdout),
        p_stderr.fileno(): (p_stderr, sys.stderr),
    }
    fds = list(stream_by_fd.keys())

    while fds:
        # `select` syscall will wait until one of the file descriptors has content.
        ready, _, _ = select.select(fds, [], [])
        for fd in ready:
            p_stream, std = stream_by_fd[fd]
            raw_buf = p_stream.read(2 ** 16)
            if not raw_buf:
                fds.remove(fd)
                continue
            if p_stream == p_stdout:
                bucket_stream.write(raw_buf)
            elif p_stream == p_stderr:
                buf = raw_buf.decode()
                std.write(buf)
                std.flush()
    bucket_stream.close()

def main():
    clips_to_make = get_clips_from_firestore()

    for clip in clips_to_make:
        ffmpeg_command: List[str] = clip["ffmpeg_command"].split()
        
        if "output.mp4" in ffmpeg_command:
            index = ffmpeg_command.index("output.mp4")
            ffmpeg_command[index] = "-"

        p = sp.Popen(ffmpeg_command, stdout=sp.PIPE, stderr=sp.PIPE)
        date = datetime.now().strftime("%Y/%m/%d")
        title_with_date = f"{date}/{clip['title']}"
        stream_stdout_to_bucket(p, title_with_date, bucket_name)

if __name__ == "__main__":
    main()
