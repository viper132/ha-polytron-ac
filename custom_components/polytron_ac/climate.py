"""Support for Polytron Smart AC climate devices."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
    HVACAction,
)
from homeassistant.components.climate.const import (
    SWING_OFF,
    SWING_VERTICAL,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    HVAC_MODE_TO_POLYTRON,
    POLYTRON_TO_HVAC_MODE,
    FAN_MODE_TO_POLYTRON,
    POLYTRON_TO_FAN_MODE,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Polytron climate platform."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator = entry_data["coordinator"]
    api = entry_data["api"]
    devices = entry_data["devices"]

    entities = []
    for dev in devices:
        sn = dev.get("serialNumber")
        if sn:
            entities.append(PolytronClimateEntity(coordinator, api, dev))

    async_add_entities(entities)

class PolytronClimateEntity(CoordinatorEntity, ClimateEntity):
    """Representation of a Polytron Smart AC unit."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = 1.0
    _attr_min_temp = 16.0
    _attr_max_temp = 32.0
    _attr_has_entity_name = True
    _attr_name = None

    _attr_hvac_modes = [
        HVACMode.OFF,
        HVACMode.COOL,
        HVACMode.DRY,
        HVACMode.FAN_ONLY,
        HVACMode.AUTO,
    ]
    _attr_fan_modes = ["auto", "low", "medium", "high"]
    _attr_swing_modes = [SWING_OFF, SWING_VERTICAL]

    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.SWING_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )

    def __init__(self, coordinator, api, dev_meta: dict):
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._api = api
        self._meta = dev_meta
        self._serial = dev_meta["serialNumber"]
        self._attr_unique_id = f"polytron_ac_{self._serial}"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._serial)},
            "name": dev_meta.get("label", "Polytron AC"),
            "manufacturer": "Polytron",
            "model": f"Neuva Pro ({dev_meta.get('jenisPerangkat', 'AE04')})",
            "sw_version": "IRAA-02-04",
        }

    @property
    def _dev_data(self) -> dict:
        """Get live data for this device from coordinator."""
        if not self.coordinator.data:
            return {}
        return self.coordinator.data.get(self._serial, {}).get("state", {})

    @property
    def _controls(self) -> dict:
        return self._dev_data.get("controls", {})

    @property
    def _sensors(self) -> dict:
        return self._dev_data.get("sensors", {})

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current operation mode."""
        power = self._controls.get("power", 0)
        if power == 0:
            return HVACMode.OFF
        mode_val = self._controls.get("mode", 2)
        mode_str = POLYTRON_TO_HVAC_MODE.get(mode_val, "cool")
        return HVACMode(mode_str)

    @property
    def hvac_action(self) -> HVACAction:
        """Return the current running action."""
        if self.hvac_mode == HVACMode.OFF:
            return HVACAction.OFF
        if self.hvac_mode == HVACMode.COOL:
            # Check if compressor is active via power consumption
            watt = self._sensors.get("power_watt", 0)
            return HVACAction.COOLING if watt > 100 else HVACAction.IDLE
        if self.hvac_mode == HVACMode.DRY:
            return HVACAction.DRYING
        if self.hvac_mode == HVACMode.FAN_ONLY:
            return HVACAction.FAN
        return HVACAction.IDLE

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return float(self._controls.get("target_temp", 24))

    @property
    def current_temperature(self) -> float | None:
        """Return the current room temperature from sensor."""
        return self._sensors.get("room_temp")

    @property
    def fan_mode(self) -> str | None:
        """Return the fan setting."""
        fan_val = self._controls.get("fan_speed", 1)
        return POLYTRON_TO_FAN_MODE.get(fan_val, "auto")

    @property
    def swing_mode(self) -> str | None:
        """Return the swing setting."""
        swing_val = self._controls.get("swing", 0)
        return SWING_VERTICAL if swing_val == 1 else SWING_OFF

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        temp_int = int(round(temperature))
        # Ensure bounds 16 - 32
        temp_int = max(16, min(32, temp_int))
        success = await self.hass.async_add_executor_job(
            self._api.send_control, self._serial, 3, 3, temp_int
        )
        if success:
            self._controls["target_temp"] = temp_int
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.OFF:
            success = await self.hass.async_add_executor_job(
                self._api.send_control, self._serial, 0, 2, 0
            )
            if success:
                self._controls["power"] = 0
                self.async_write_ha_state()
                await self.coordinator.async_request_refresh()
            return

        # Turn ON if currently OFF
        if self._controls.get("power", 0) == 0:
            await self.hass.async_add_executor_job(
                self._api.send_control, self._serial, 0, 2, 1
            )
            self._controls["power"] = 1

        mode_code = HVAC_MODE_TO_POLYTRON.get(str(hvac_mode), 2)
        success = await self.hass.async_add_executor_job(
            self._api.send_control, self._serial, 1, 3, mode_code
        )
        if success:
            self._controls["mode"] = mode_code
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        fan_code = FAN_MODE_TO_POLYTRON.get(fan_mode.lower(), 1)
        success = await self.hass.async_add_executor_job(
            self._api.send_control, self._serial, 4, 3, fan_code
        )
        if success:
            self._controls["fan_speed"] = fan_code
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        """Set new target swing operation."""
        swing_val = 1 if swing_mode == SWING_VERTICAL else 0
        success = await self.hass.async_add_executor_job(
            self._api.send_control, self._serial, 5, 2, swing_val
        )
        if success:
            self._controls["swing"] = swing_val
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        """Turn the entity on."""
        success = await self.hass.async_add_executor_job(
            self._api.send_control, self._serial, 0, 2, 1
        )
        if success:
            self._controls["power"] = 1
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        await self.async_set_hvac_mode(HVACMode.OFF)
