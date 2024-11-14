

import io
from pathlib import Path
import base64
from datetime import datetime
import random

from ffmpeg import FFmpeg

from .config import AUDIO_FORMAT, AUDIO_BITRATE, AUDIO_SAMPLERATE, AUDIO_CODEC


RANDOM_SEQUENCE_LEN = 6

def generate_unique_name() -> str:
    n = datetime.now()
    return base64.urlsafe_b64encode(bytes(n.isoformat(), "ascii") + b":" + random.randbytes(RANDOM_SEQUENCE_LEN)).decode("ascii")


def audio_file_to_bytes(file: Path) -> bytes:
    ff = (
        FFmpeg()
        .option("y")
        .input(file)
        .output("pipe:1", 
                {"b:a": AUDIO_BITRATE, "codec:a": AUDIO_CODEC},
                f=AUDIO_FORMAT,
                ar=str(AUDIO_SAMPLERATE),
                ac=1
                )
    )
    return ff.execute(timeout=8)