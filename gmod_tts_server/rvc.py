

from typing import Any
from pathlib import Path
import logging
import json

from .edge_tts import RawEdgeTTSVoice
from rvc_python.infer import RVCInference

from .schemas import RVCVoiceConfig, RVCParams, TTSOptions
from .voices import Voice, register_voice
from .utils import generate_unique_name
from .config import AUDIO_TMP, VOICES_DIR, RVC_DEVICE, AUDIO_SAMPLERATE

logger = logging.getLogger(__name__)


class RVCVoice(Voice):
    edge_tts: dict[str, RawEdgeTTSVoice]
    rvc_inference: RVCInference

    def __init__(self, description: str, languages: dict[str, RawEdgeTTSVoice], rvc_inference: RVCInference):
        super().__init__(description=description, languages=list(languages.keys()))
        self.edge_tts = dict(languages)
        self.rvc_inference = rvc_inference

    async def text_to_speech(self, text: str, language: str, options: TTSOptions) -> Path:
        base_file = await self.edge_tts[language].text_to_speech(text, language, options)
        output_file = AUDIO_TMP / f"rvc_{generate_unique_name()}.wav"
        try:
            self.rvc_inference.infer_file(str(base_file), str(output_file))
        except Exception:
            base_file.unlink()
            output_file.unlink(missing_ok=True)
            raise
        base_file.unlink()
        return output_file
    

def load_rvc_model(config_file: Path):
    logger.info(f"Loading RVC model from config {config_file}...")
    voice_data: Any = json.loads(config_file.read_text())
    voice_config = RVCVoiceConfig.model_validate(voice_data)

    languages: dict[str, RawEdgeTTSVoice] = {}
    for language, language_config in voice_config.languages.items():
        if isinstance(language_config, str):
            languages[language] = RawEdgeTTSVoice(voice=language_config)  
        else:
            languages[language] = RawEdgeTTSVoice(
                voice=language_config.voice, 
                base_options=TTSOptions(**language_config.model_dump(include=TTSOptions.model_fields))
            )
    
    model_path = config_file.parent / voice_config.model
    index_path = config_file.parent / voice_config.index
    rvc_inference = RVCInference(device=RVC_DEVICE, version=voice_config.rvc_version, index_path=index_path)
    rvc_params = voice_config.rvc_params if voice_config.rvc_params is not None else RVCParams()
    rvc_inference.set_params(
        f0method=rvc_params.method,
        f0up_key=rvc_params.pitch,
        rms_mix_rate=rvc_params.rms_mix_rate,
        protect=rvc_params.protect
    )
    rvc_inference.load_model(str(model_path), version=voice_config.rvc_version, index_path=str(index_path))

    voice_name = config_file.stem
    voice = RVCVoice(description=voice_config.description, languages=languages, rvc_inference=rvc_inference)
    register_voice(voice_name, voice)
    logger.info(f"RVC voice {voice_name} is successfully registered.")


def load_rvc_models():
    logger.info("Loading RVC voices...")
    for config_file in (VOICES_DIR / "rvc_models").glob("**/*.json"):
        load_rvc_model(config_file)
    logger.info("All RVC voices are successfully registered.")