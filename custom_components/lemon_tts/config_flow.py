"""Config flow for Lemon TTS."""
import logging

import httpx
import voluptuous as vol
from homeassistant import config_entries

from .const import (
    CONF_API_KEY,
    CONF_API_URL,
    CONF_MUTE_ENTITY,
    CONF_MUTE_STATE,
    CONF_SPEAKERS,
    DEFAULT_MUTE_STATE,
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
                    return self.async_create_entry(
                        title="Lemon TTS",
                        data={
                            CONF_API_URL: user_input[CONF_API_URL],
                            CONF_API_KEY: user_input[CONF_API_KEY],
                            CONF_SPEAKERS: speakers,
                            CONF_MUTE_ENTITY: user_input.get(CONF_MUTE_ENTITY, ""),
                            CONF_MUTE_STATE: user_input.get(CONF_MUTE_STATE, DEFAULT_MUTE_STATE),
                        },
                    )
            except Exception:
                _LOGGER.exception("Error connecting to Lemon TTS API")
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_URL): str,
                    vol.Required(CONF_API_KEY): str,
                    vol.Optional(CONF_MUTE_ENTITY, default=""): str,
                    vol.Optional(CONF_MUTE_STATE, default=DEFAULT_MUTE_STATE): str,
                }
            ),
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input=None):
        errors = {}
        entry = self._get_reconfigure_entry()

        if user_input is not None:
            try:
                speakers = await _fetch_speakers(
                    user_input[CONF_API_URL], user_input[CONF_API_KEY]
                )
                if not speakers:
                    errors["base"] = "cannot_connect"
                else:
                    return self.async_update_reload_and_abort(
                        entry,
                        data={
                            CONF_API_URL: user_input[CONF_API_URL],
                            CONF_API_KEY: user_input[CONF_API_KEY],
                            CONF_SPEAKERS: speakers,
                            CONF_MUTE_ENTITY: user_input.get(CONF_MUTE_ENTITY, ""),
                            CONF_MUTE_STATE: user_input.get(CONF_MUTE_STATE, DEFAULT_MUTE_STATE),
                        },
                    )
            except Exception:
                _LOGGER.exception("Error connecting to Lemon TTS API")
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_URL, default=entry.data.get(CONF_API_URL, "")): str,
                    vol.Required(CONF_API_KEY, default=entry.data.get(CONF_API_KEY, "")): str,
                    vol.Optional(CONF_MUTE_ENTITY, default=entry.data.get(CONF_MUTE_ENTITY, "")): str,
                    vol.Optional(CONF_MUTE_STATE, default=entry.data.get(CONF_MUTE_STATE, DEFAULT_MUTE_STATE)): str,
                }
            ),
            errors=errors,
        )
