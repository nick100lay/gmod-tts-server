

from urllib.parse import urljoin

from fastapi import FastAPI, HTTPException, Response
import librosa

from .schemas import TTSRequestSchema, TTSResponseSchema, TTSOptions, InfoSchema
from .auth import AuthDep
from .utils import generate_unique_name, audio_file_to_bytes
from .voices import get_voice, voice_exists, get_voices_info, VoiceException
from .config import REMOTE_BASE_URL, VERSION, PROJECT, AUDIO_FORMAT, AUDIO_TMP
from .edge_tts import register_edge_tts_voices
from .rvc import load_rvc_models
from . import audio_cache


app = FastAPI()

AUDIO_TMP.mkdir(parents=True, exist_ok=True)
audio_cache.clear_audio_cache_job()
register_edge_tts_voices()
load_rvc_models()


async def generate_audio(data: TTSRequestSchema) -> tuple[bytes, float]:
    text = data.text.strip()
    voice = data.voice.strip().lower()
    options = data.options if data.options is not None else TTSOptions()
    language = data.language.strip().lower()
    if not voice_exists(voice):
        raise HTTPException(status_code=400, detail=f"Invalid voice {repr(voice)}")
    voice = get_voice(voice)
    if language not in voice.languages:
        raise HTTPException(status_code=400, detail=f"Language {repr(language)} is not available for voice {repr(voice)}")

    try:
        audio_file = await voice.text_to_speech(text, language, options)
    except VoiceException:
        raise HTTPException(status_code=400, detail=f"Couldn't synthesize text by this voice")
    
    duration = librosa.get_duration(path=audio_file)
    audio = audio_file_to_bytes(audio_file)
    audio_file.unlink()
    return audio, duration


@app.post("/tts",
    responses={
        400: { "description": "Couldn't synthesize the text to speech (invalid text, language or voice)" },
        401: { "description": "Unauthorized (invalid secret key)" },
        429: { "description": "Audio cache is full (too many requests)" }
    }
)
async def text_to_speech(data: TTSRequestSchema, secret_key: AuthDep) -> TTSResponseSchema:
    if audio_cache.audio_cache_is_full():
        raise HTTPException(status_code=429, detail="Audio cache is full")

    text = data.text.strip()
    voice = data.voice.strip().lower()
    options = data.options if data.options is not None else TTSOptions()
    language = data.language.strip().lower()
    if not voice_exists(voice):
        raise HTTPException(status_code=400, detail=f"Invalid voice {repr(voice)}")
    voice = get_voice(voice)
    if language not in voice.languages:
        raise HTTPException(status_code=400, detail=f"Language {repr(language)} is not available for voice {repr(voice)}")

    try:
        audio_file = await voice.text_to_speech(text, language, options)
    except VoiceException:
        raise HTTPException(status_code=400, detail=f"Couldn't synthesize text by this voice")
    
    duration = librosa.get_duration(path=audio_file)
    audio = audio_file_to_bytes(audio_file)
    audio_file.unlink()

    key = generate_unique_name()
    expires_at = audio_cache.add_audio(key, audio)
    expires_at_iso = expires_at.strftime('%Y-%m-%dT%H:%M:%SZ')
    return TTSResponseSchema(
        play_url=urljoin(REMOTE_BASE_URL, "play/" + key),
        duration=duration,
        play_url_expires_at=expires_at_iso
    )


@app.get("/info",
    responses={
        401: { "description": "Unauthorized (invalid secret key)" }
    }
)
async def get_info(secret_key: AuthDep) -> InfoSchema:
    return InfoSchema(project=PROJECT, version=VERSION, voices=get_voices_info())


@app.get("/play/{key}",
    responses={
        200: { "description": "Audio to play", "content": {f"audio/{AUDIO_FORMAT}": {}} },
        404: { "description": "Audio is not found" }
    },
    response_class=Response
)
async def get_audio(key: str):
    if not audio_cache.audio_exists(key):
        raise HTTPException(status_code=404, detail="Audio is not found")
    return Response(content=audio_cache.get_audio(key), media_type=f"audio/{AUDIO_FORMAT}")