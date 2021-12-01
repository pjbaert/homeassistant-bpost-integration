from __future__ import annotations

from collections import Mapping
from typing import Any

from homeassistant.components.bpost import DOMAIN, BpostEntryData
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator


async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Configure all sensors and expose as entities."""

    entry_data: BpostEntryData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        BpostSensor(entry_data.coordinator, ent) for idx, ent in enumerate(entry_data.coordinator.data["sensor"])
    )


class BpostSensor(CoordinatorEntity, SensorEntity):
    """Sensor providing information about bpost My Mail and parcels."""

    def __init__(self, coordinator: DataUpdateCoordinator, sensor_id: str):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.sensor_id = sensor_id

    @property
    def native_value(self) -> StateType:
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
