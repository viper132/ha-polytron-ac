"""Config flow for Polytron Smart AC integration."""
from __future__ import annotations

import logging
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_USERNAME, CONF_TOKEN, CONF_USER_B
from .polytron_api import PolytronAPI

_LOGGER = logging.getLogger(__name__)

class PolytronConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Polytron Smart AC."""

    VERSION = 1

    def __init__(self):
        self._phone: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle initial step: phone number entry."""
        errors: dict[str, str] = {}

        if user_input is not None:
            phone = user_input.get(CONF_USERNAME, "").strip()
            # Standardize leading zeros or country codes if necessary
            if phone.startswith("+"):
                phone = phone[1:]
            
            if phone:
                try:
                    res = await self.hass.async_add_executor_job(
                        PolytronAPI.request_wa_otp, phone
                    )
                    if res.get("error") == "0":
                        self._phone = phone
                        return await self.async_step_otp()
                    else:
                        errors["base"] = "otp_send_failed"
                except Exception as err:
                    _LOGGER.exception("Failed to request OTP from Polytron: %s", err)
                    errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_USERNAME): str,
            }),
            errors=errors,
        )

    async def async_step_otp(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle OTP verification step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            otp_code = user_input.get("otp_code", "").strip()
            try:
                res = await self.hass.async_add_executor_job(
                    PolytronAPI.verify_otp, self._phone, otp_code
                )
                token = res.get("token") or res.get("data", {}).get("token")
                if token:
                    await self.async_set_unique_id(self._phone)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"Polytron ({self._phone})",
                        data={
                            CONF_USERNAME: self._phone,
                            CONF_TOKEN: token,
                            CONF_USER_B: res.get("userB", "")
                        }
                    )
                else:
                    errors["base"] = "invalid_otp"
            except Exception as err:
                _LOGGER.exception("Failed to verify OTP with Polytron: %s", err)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="otp",
            data_schema=vol.Schema({
                vol.Required("otp_code"): str,
            }),
            errors=errors,
            description_placeholders={"phone": self._phone or ""},
        )
