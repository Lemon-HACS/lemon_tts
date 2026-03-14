"""Lemon TTS platform."""
import logging

import httpx
from homeassistant.components.tts import TextToSpeechEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_API_KEY,
    CONF_API_URL,
    CONF_DEFAULT_SPEAKER,
    DEFAULT_LANGUAGE,
    DEFAULT_SPEAKER,
    DOMAIN,
    SUPPORTED_LANGUAGES,
    TTS_OPTIONS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lemon TTS from a config entry."""
    async_add_entities([LemonTTSEntity(config_entry)])


class LemonTTSEntity(TextToSpeechEntity):
    """Lemon TTS entity."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, config_entry: ConfigEntry) -> None:
        self._config_entry = config_entry
        self._attr_unique_id = config_entry.entry_id

    @property
    def default_language(self) -> str:
        return DEFAULT_LANGUAGE

    @property
    def supported_languages(self) -> list[str]:
        return SUPPORTED_LANGUAGES

    @property
    def supported_options(self) -> list[str]:
        return TTS_OPTIONS

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": "Lemon TTS",
            "manufacturer": "Lemon",
        }

    def _get_default_speaker(self) -> str:
        return self._config_entry.options.get(
            CONF_DEFAULT_SPEAKER,
            self._config_entry.data.get(CONF_DEFAULT_SPEAKER, DEFAULT_SPEAKER),
        )

    async def async_get_tts_audio(
        self,
        message: str,
        language: str,
        options: dict | None = None,
    ) -> tuple[str | None, bytes | None]:
        """Generate TTS audio from message."""
        options = options or {}
        data = self._config_entry.data
        api_url = data[CONF_API_URL].rstrip("/")
        api_key = data[CONF_API_KEY]

        params: dict = {
            "text": message,
            "speaker_name": options.get("speaker_name", self._get_default_speaker()),
        }

        # Numeric options — only include if explicitly set
        for key in ("sdp_ratio", "noise", "noisew", "length", "style_weight"):
            if key in options:
                params[key] = options[key]

        # String options — only include if non-empty
        for key in ("style_text", "translation_prompt"):
            if options.get(key):
                params[key] = options[key]

        _LOGGER.info(
            "[LemonTTS] speaker=%s, text=%.80s", params["speaker_name"], message
        )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{api_url}/api/tts",
                    params=params,
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=30,
                )

            if response.status_code != 200:
                _LOGGER.error(
                    "[LemonTTS] API error %s: %s", response.status_code, response.text
                )
                return None, None

            return "wav", response.content

        except Exception as e:
            _LOGGER.error("[LemonTTS] Request failed: %s", e)
            return None, None
