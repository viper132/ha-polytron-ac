"""The Polytron Smart AC integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_USERNAME, CONF_TOKEN, CONF_USER_B, SCAN_INTERVAL_SECONDS
from .polytron_api import PolytronAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.CLIMATE, Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Polytron Smart AC from a config entry."""
    username = entry.data[CONF_USERNAME]
    token = entry.data[CONF_TOKEN]
    user_b = entry.data.get(CONF_USER_B, "")

    api = PolytronAPI(username=username, token=token, user_b=user_b)

    # Initial device discovery
    try:
        devices = await hass.async_add_executor_job(api.get_devices)
    except Exception as err:
        _LOGGER.error("Failed to connect to Polytron IoT service: %s", err)
        raise UpdateFailed(f"Connection error: {err}") from err

    async def async_update_data():
        """Fetch data from Polytron API for all registered devices."""
        data = {}
        for dev in devices:
            sn = dev.get("serialNumber")
            if not sn:
                continue
            try:
                state = await hass.async_add_executor_job(api.get_live_state, sn)
                data[sn] = {
                    "meta": dev,
                    "state": state
                }
            except Exception as err:
                _LOGGER.warning("Error updating Polytron device %s: %s", sn, err)
        return data

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
        "devices": devices,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
