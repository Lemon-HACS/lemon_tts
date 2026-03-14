"""Config flow for Lemon TTS."""
import logging

import httpx
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_API_KEY,
    CONF_API_URL,
    CONF_DEFAULT_SPEAKER,
    DEFAULT_SPEAKER,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def _fetch_speakers(api_url: str, api_key: str) -> list[str]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{api_url.rstrip('/')}/api/tts/speakers",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10,
        )
    if response.status_code == 200:
        return response.json().get("speakers", [])
    return []


class LemonTTSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Lemon TTS."""

    VERSION = 1

    def __init__(self) -> None:
        self._api_url: str = ""
        self._api_key: str = ""
        self._speakers: list[str] = []

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                speakers = await _fetch_speakers(
                    user_input[CONF_API_URL], user_input[CONF_API_KEY]
                )
                if not speakers:
                    errors["base"] = "cannot_connect"
                else:
                    self._api_url = user_input[CONF_API_URL]
                    self._api_key = user_input[CONF_API_KEY]
                    self._speakers = speakers
                    return await self.async_step_speaker()
            except Exception:
                _LOGGER.exception("Error connecting to Lemon TTS API")
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_URL): str,
                    vol.Required(CONF_API_KEY): str,
                }
            ),
            errors=errors,
        )

    async def async_step_speaker(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="Lemon TTS",
                data={
                    CONF_API_URL: self._api_url,
                    CONF_API_KEY: self._api_key,
                    CONF_DEFAULT_SPEAKER: user_input[CONF_DEFAULT_SPEAKER],
                },
            )

        default = self._speakers[0] if self._speakers else DEFAULT_SPEAKER
        return self.async_show_form(
            step_id="speaker",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_DEFAULT_SPEAKER, default=default): vol.In(
                        self._speakers
                    ),
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return LemonTTSOptionsFlow()


class LemonTTSOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Lemon TTS."""

    async def async_step_init(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(data=user_input)

        try:
            speakers = await _fetch_speakers(
                self.config_entry.data[CONF_API_URL],
                self.config_entry.data[CONF_API_KEY],
            )
        except Exception:
            speakers = []

        current_speaker = self.config_entry.options.get(
            CONF_DEFAULT_SPEAKER,
            self.config_entry.data.get(CONF_DEFAULT_SPEAKER, DEFAULT_SPEAKER),
        )

        if speakers:
            speaker_selector = vol.In(speakers)
            default = current_speaker if current_speaker in speakers else speakers[0]
        else:
            speaker_selector = str
            default = current_speaker
            errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_DEFAULT_SPEAKER, default=default): speaker_selector,
                }
            ),
            errors=errors,
        )
