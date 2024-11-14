

import os
from pathlib import Path


class ConfigurationError(Exception):
    pass


PROJECT = "gmod-tts"
VERSION = "1.0"

ROOT_DIR = Path(__file__).parent.parent

REMOTE_BASE_URL = os.environ.get("GMOD_TTS_REMOTE_BASE_URL", "").strip()
if not REMOTE_BASE_URL:
    raise ConfigurationError("Environment variable GMOD_TTS_REMOTE_BASE_URL is not set.")

SECRET_KEY = os.environ.get("GMOD_TTS_SECRET_KEY", "").strip()

if "GMOD_TTS_VOICES_DIR" in os.environ:
    VOICES_DIR = Path(os.environ.get("GMOD_TTS_VOICES_DIR", "").strip())
else:
    VOICES_DIR = ROOT_DIR / "voices"

AUDIO_TTL = int(os.environ.get("GMOD_TTS_AUDIO_TTL", "5"))
AUDIO_MAX_COUNT = int(os.environ.get("GMOD_TTS_AUDIO_MAX_COUNT", "128"))
AUDIO_CLEANING_JOB_INTERVAL = max(30, AUDIO_TTL + 5)
if "GMOD_TTS_AUDIO_TMP" in os.environ:
    AUDIO_TMP = Path(os.environ.get("GMOD_TTS_AUDIO_TMP", "").strip())
else:
    AUDIO_TMP = ROOT_DIR / "audio_tmp"

AUDIO_FORMAT = os.environ.get("GMOD_TTS_AUDIO_FORMAT", "mp3")
AUDIO_CODEC = os.environ.get("GMOD_TTS_AUDIO_CODEC", AUDIO_FORMAT)
AUDIO_BITRATE = os.environ.get("GMOD_TTS_AUDIO_BITRATE", "48k")
AUDIO_SAMPLERATE = int(os.environ.get("GMOD_TTS_AUDIO_SAMPLERATE", "22050"))

RVC_DEVICE = os.environ.get("GMOD_TTS_RVC_DEVICE", "cuda:0")