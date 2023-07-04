from settings import SETTINGS
from datetime import datetime
from google.cloud import storage
import select
import io
import sys
from typing import Dict, Tuple, Optional, IO, List
import subprocess as sp
from firestore.firestore import get_clips_from_firestore

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


def stream_stdout_to_bucket(process: sp.Popen, write_stream):

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
                write_stream.write(raw_buf)
            elif p_stream == p_stderr:
                buf = raw_buf.decode()
                std.write(buf)
                std.flush()


def main():
    clips_to_make = get_clips_from_firestore(date="03-07-23")
    print(clips_to_make)
    client = storage.Client()
    bucket = client.bucket(SETTINGS["gcp"]["bucket-name"])

    for clip in clips_to_make:
        ffmpeg_command: List[str] = clip["ffmpeg_command"].split()

        if "output.mp4" in ffmpeg_command:
            index = ffmpeg_command.index("output.mp4")
            ffmpeg_command[index] = "-"

        p = sp.Popen(ffmpeg_command, stdout=sp.PIPE, stderr=sp.PIPE)

        blob = bucket.blob(clip['id'])
        bucket_stream = blob.open("wb")
        stream_stdout_to_bucket(p, bucket_stream)
        bucket_stream.close()


if __name__ == "__main__":
    main()
