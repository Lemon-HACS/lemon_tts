"""Lemon TTS platform."""
import io
import logging
import wave

import httpx
from homeassistant.components.tts import TextToSpeechEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_API_KEY,
    CONF_API_URL,
    CONF_ENABLE_ENTITY,
    CONF_ENABLE_STATE,
    DEFAULT_LANGUAGE,
    DEFAULT_ENABLE_STATE,
    DOMAIN,
    SUPPORTED_LANGUAGES,
    TTS_OPTIONS,
)

_LOGGER = logging.getLogger(__name__)


def _generate_silence() -> bytes:
    """0.1초 무음 WAV 데이터를 생성합니다."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(22050)
        w.writeframes(b"\x00\x00" * 2205)
    return buf.getvalue()


async def _fetch_speakers(api_url: str, api_key: str) -> list[str]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{api_url.rstrip('/')}/api/tts/speakers",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10,
        )
    if response.status_code != 200:
        return []
    return response.json().get("speakers", [])


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up one TTS entity per speaker (화자 목록은 항상 서버에서 조회)."""
    data = config_entry.data

    try:
        speakers = await _fetch_speakers(data[CONF_API_URL], data[CONF_API_KEY])
    except Exception as e:
        _LOGGER.error("[LemonTTS] Failed to fetch speakers: %s", e)
        return

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

        # TTS 활성화 체크: 설정된 엔티티가 있고 상태가 활성화 상태가 아니면 스킵
        enable_entity = data.get(CONF_ENABLE_ENTITY, "")
        if enable_entity:
            enable_state = data.get(CONF_ENABLE_STATE, DEFAULT_ENABLE_STATE)
            entity_state = self.hass.states.get(enable_entity)
            if entity_state is not None and entity_state.state != enable_state:
                _LOGGER.debug(
                    "[LemonTTS] TTS disabled by %s (state=%s, expected=%s). Returning silence.",
                    enable_entity, entity_state.state, enable_state,
                )
                return "wav", _generate_silence()

        api_url = data[CONF_API_URL].rstrip("/")
        api_key = data[CONF_API_KEY]

        params: dict = {
            "text": message,
            "speaker_name": self._speaker_name,
        }

        if "speed" in options:
            params["speed"] = options["speed"]
        if options.get("translation_prompt"):
            params["translation_prompt"] = options["translation_prompt"]

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
