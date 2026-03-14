"""Lemon TTS platform."""
import logging

import httpx
from homeassistant.components.tts import TextToSpeechEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_API_KEY,
    CONF_API_URL,
    CONF_SPEAKERS,
    DEFAULT_LANGUAGE,
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
    """Set up one TTS entity per speaker."""
    data = config_entry.data
    speakers: list[str] = data.get(CONF_SPEAKERS, [])

    # 캐시된 화자 목록이 없으면 API에서 새로 조회
    if not speakers:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{data[CONF_API_URL].rstrip('/')}/api/tts/speakers",
                    headers={"Authorization": f"Bearer {data[CONF_API_KEY]}"},
                    timeout=10,
                )
            if response.status_code == 200:
                speakers = response.json().get("speakers", [])
        except Exception as e:
            _LOGGER.error("[LemonTTS] Failed to fetch speakers: %s", e)

    if not speakers:
        _LOGGER.error("[LemonTTS] No speakers available, cannot set up entities.")
        return

    async_add_entities([LemonTTSEntity(config_entry, speaker) for speaker in speakers])


class LemonTTSEntity(TextToSpeechEntity):
    """Lemon TTS entity for a single speaker."""

    def __init__(self, config_entry: ConfigEntry, speaker_name: str) -> None:
        self._config_entry = config_entry
        self._speaker_name = speaker_name
        self._attr_name = f"Lemon TTS {speaker_name}"
        self._attr_unique_id = f"{config_entry.entry_id}_{speaker_name}"

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
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._config_entry.entry_id)},
            name="Lemon TTS",
            manufacturer="Lemon",
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
            "speaker_name": self._speaker_name,
        }

        for key in ("sdp_ratio", "noise", "noisew", "length", "style_weight"):
            if key in options:
                params[key] = options[key]

        for key in ("style_text", "translation_prompt"):
            if options.get(key):
                params[key] = options[key]

        _LOGGER.info(
            "[LemonTTS] speaker=%s, text=%.80s", self._speaker_name, message
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
