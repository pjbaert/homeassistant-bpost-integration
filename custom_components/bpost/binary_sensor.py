from __future__ import annotations

from collections import Mapping
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from . import DOMAIN, BpostEntryData


async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Configure all sensors and expose as entities."""

    entry_data: BpostEntryData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        BpostBinarySensor(entry_data.coordinator, ent)
        for idx, ent in enumerate(entry_data.coordinator.data["binary_sensor"])
    )


class BpostBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator: DataUpdateCoordinator, sensor_id: str):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.sensor_id = sensor_id

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data[self.platform.domain][self.sensor_id]["data"]

    @property
    def unique_id(self) -> str | None:
        return f"{DOMAIN}_{self.platform.domain}_{self.sensor_id}"

    @property
    def name(self) -> str | None:
        return self.sensor_id.replace("_", " ").capitalize()

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        return self.coordinator.data[self.platform.domain][self.sensor_id].get("extra")
