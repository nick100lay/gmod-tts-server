

from typing import Any
from pathlib import Path

from .schemas import VoiceInfo, TTSOptions


class VoiceAlreadyExistsException(Exception):
    pass


class VoiceException(Exception):
    pass


class Voice:
    description: str
    languages: frozenset[str]

    def __init__(self, description: str, languages: list[str]):
        self.description = description
        self.languages = frozenset(languages)

    async def text_to_speech(self, text: str, language: str, options: TTSOptions) -> Path:
        pass


voices: dict[str, Voice] = {}


def voice_exists(voice: str) -> bool:
    return voice in voices


def get_voice(voice: str) -> Voice:
    return voices[voice]


def register_voice(voice: str, voice_obj: Voice):
    if voice in voices:
        raise VoiceAlreadyExistsException(f"Voice {repr(voice)} already exists")
    voices[voice] = voice_obj


def get_voices_info() -> dict[str, VoiceInfo]:
    return {
        name: VoiceInfo(
            description=voice.description,
            languages={lang: True for lang in voice.languages}
        ) 
        for name, voice in voices.items()
    }