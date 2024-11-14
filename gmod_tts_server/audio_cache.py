

import threading
import logging
from datetime import datetime, timedelta, timezone

from cachetools import TTLCache

from .config import AUDIO_CLEANING_JOB_INTERVAL, AUDIO_MAX_COUNT, AUDIO_TTL

logger = logging.getLogger(__name__)

cache = TTLCache(maxsize=AUDIO_MAX_COUNT, ttl=AUDIO_TTL)


def clear_audio_cache_job():
    expired = cache.expire()
    if expired:
        logger.info(f"Clearing {len(expired)} audio from cache.")
    timer = threading.Timer(AUDIO_CLEANING_JOB_INTERVAL, clear_audio_cache_job)
    timer.daemon = True
    timer.start()


def add_audio(key: str, audio: bytes) -> datetime:
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=AUDIO_TTL)
    cache[key] = audio
    return expires_at


def get_audio(key: str) -> bytes:
    return cache[key]


def audio_exists(key: str) -> bool:
    return key in cache 


def audio_cache_is_full() -> bool:
    return len(cache) >= cache.maxsize