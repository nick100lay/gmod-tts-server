

from typing import Any, Literal, Optional, Union
from pydantic import BaseModel


class TTSOptions(BaseModel):
    speed: int = 0
    volume: int = 0


class TTSRequestSchema(BaseModel):
    text: str
    voice: str
    language: str
    options: Optional[TTSOptions] = None


class TTSResponseSchema(BaseModel):
    play_url: str
    duration: float
    play_url_expires_at: str


class VoiceInfo(BaseModel):
    description: str
    languages: dict[str, bool]


class InfoSchema(BaseModel):
    project: str
    version: str
    voices: dict[str, VoiceInfo]


class EdgeTTSVoiceConfig(TTSOptions):
    voice: str
    language: str
    description: str


class RVCVoiceConfigEdgeTTSParams(TTSOptions):
    voice: str


class RVCParams(TTSOptions):
    method: Literal["harvest", "crepe", "rmvpe", "pm"] = "rmvpe"
    protect: float = 0.5
    pitch: int = 0
    rms_mix_rate: float = 0.25


class RVCVoiceConfig(TTSOptions):
    index: str
    model: str
    rvc_version: Literal["v1", "v2"]
    rvc_params: Optional[RVCParams] = None
    languages: dict[str, Union[RVCVoiceConfigEdgeTTSParams, str]]
    description: str