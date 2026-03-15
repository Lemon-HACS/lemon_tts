"""Constants for Lemon TTS."""

DOMAIN = "lemon_tts"

CONF_API_URL = "api_url"
CONF_API_KEY = "api_key"
CONF_SPEAKERS = "speakers"
CONF_ENABLE_ENTITY = "enable_entity"
CONF_ENABLE_STATE = "enable_state"

DEFAULT_ENABLE_STATE = "on"

SUPPORTED_LANGUAGES = ["ko", "en", "ja", "zh"]
DEFAULT_LANGUAGE = "ko"

TTS_OPTIONS = [
    "sdp_ratio",
    "noise",
    "noisew",
    "length",
    "style_text",
    "style_weight",
    "translation_prompt",
]
