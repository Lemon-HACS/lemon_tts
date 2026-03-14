"""Constants for Lemon TTS."""

DOMAIN = "lemon_tts"

CONF_API_URL = "api_url"
CONF_API_KEY = "api_key"
CONF_DEFAULT_SPEAKER = "default_speaker"

DEFAULT_SPEAKER = "Arona"

# 입력 텍스트는 언어 무관, 출력은 항상 일본어
SUPPORTED_LANGUAGES = ["ja"]
DEFAULT_LANGUAGE = "ja"

TTS_OPTIONS = [
    "speaker_name",
    "sdp_ratio",
    "noise",
    "noisew",
    "length",
    "style_text",
    "style_weight",
    "translation_prompt",
]
