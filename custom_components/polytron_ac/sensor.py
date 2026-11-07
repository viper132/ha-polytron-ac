"""Sensor platform for Polytron Smart AC."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfPower,
    UnitOfEnergy,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Polytron sensors."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator = entry_data["coordinator"]
    devices = entry_data["devices"]

    entities = []
    for dev in devices:
        sn = dev.get("serialNumber")
        if sn:
            entities.extend([
                PolytronPowerSensor(coordinator, dev),
                PolytronEnergySensor(coordinator, dev),
                PolytronRssiSensor(coordinator, dev),
            ])

    async_add_entities(entities)

class PolytronBaseSensor(CoordinatorEntity, SensorEntity):
    """Base sensor for Polytron AC telemetry."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, dev_meta: dict):
        super().__init__(coordinator)
        self._serial = dev_meta["serialNumber"]
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._serial)},
            "name": dev_meta.get("label", "Polytron AC"),
            "manufacturer": "Polytron",
            "model": f"Neuva Pro ({dev_meta.get('jenisPerangkat', 'AE04')})",
        }

    @property
    def _sensors(self) -> dict:
        if not self.coordinator.data:
            return {}
        return self.coordinator.data.get(self._serial, {}).get("state", {}).get("sensors", {})


class PolytronPowerSensor(PolytronBaseSensor):
    """Real-time active wattage sensor."""

    _attr_name = "Power"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT

    def __init__(self, coordinator, dev_meta: dict):
        super().__init__(coordinator, dev_meta)
        self._attr_unique_id = f"polytron_ac_{self._serial}_power"

    @property
    def native_value(self) -> float | None:
        return self._sensors.get("power_watt")


class PolytronEnergySensor(PolytronBaseSensor):
    """Accumulated energy usage sensor in kWh."""

    _attr_name = "Energy Consumption"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

    def __init__(self, coordinator, dev_meta: dict):
        super().__init__(coordinator, dev_meta)
        self._attr_unique_id = f"polytron_ac_{self._serial}_energy"

    @property
    def native_value(self) -> float | None:
        return self._sensors.get("energy_kwh")


class PolytronRssiSensor(PolytronBaseSensor):
    """Wi-Fi Signal Strength in dBm."""

    _attr_name = "Wi-Fi RSSI"
    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT

    def __init__(self, coordinator, dev_meta: dict):
        super().__init__(coordinator, dev_meta)
        self._attr_unique_id = f"polytron_ac_{self._serial}_rssi"

    @property
    def native_value(self) -> int | None:
        return self._sensors.get("rssi")
