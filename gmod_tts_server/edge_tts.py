

from typing import Optional, Any
from pathlib import Path
import json
import logging

from edge_tts import Communicate
from edge_tts.exceptions import NoAudioReceived

from .schemas import TTSOptions, EdgeTTSVoiceConfig
from .config import AUDIO_TMP, VOICES_DIR
from .utils import generate_unique_name
from .voices import Voice, register_voice, VoiceException

logger = logging.getLogger(__name__) 


class RawEdgeTTSVoice:
    voice: str

    def __init__(self, voice: str, base_options: Optional[TTSOptions] = None):
        self.voice = voice
        self.base_options = base_options if base_options is not None else TTSOptions()

    async def text_to_speech(self, text: str, language: str, options: TTSOptions) -> Path:
        communicate = Communicate(
            text, 
            voice=self.voice, 
            rate=f"{round(self.base_options.speed + options.speed):+d}%",
            volume=f"{round(self.base_options.volume + options.volume):+d}%"
        )
        output_file = AUDIO_TMP / f"edgetts_{generate_unique_name()}.wav"
        try:
            await communicate.save(str(output_file))
        except NoAudioReceived as ex:
            output_file.unlink(missing_ok=True)
            raise VoiceException("Couldn't synthesize the text") from ex
        except Exception:
            output_file.unlink(missing_ok=True)
            raise
        return output_file


class EdgeTTSVoice(RawEdgeTTSVoice, Voice):
    def __init__(self, description: str, language: str, voice: str, base_options: Optional[TTSOptions]):
        super().__init__(voice=voice, base_options=base_options)
        super(RawEdgeTTSVoice, self).__init__(description=description, languages=[language])


def register_edge_tts_voices():
    logger.info("Registering edge-tts voices...")
    edge_tts_voices: dict[str, Any] = json.loads((VOICES_DIR / "edge_tts.json").read_text())
    for voice_name, voice_data in edge_tts_voices.items():
        voice_config = EdgeTTSVoiceConfig.model_validate(voice_data)
        voice = EdgeTTSVoice(
            description=voice_config.description, 
            language=voice_config.language, 
            voice=voice_config.voice, 
            base_options=TTSOptions(**voice_config.model_dump(include=TTSOptions.model_fields))
        )
        register_voice(voice_name, voice)
        logger.info(f"Edge-tts voice {repr(voice_config.voice)} is registered as {repr(voice_name)}.")
    logger.info("All edge-tts are registered.")