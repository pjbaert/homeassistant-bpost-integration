from __future__ import annotations

import collections
from typing import Any, Mapping

from homeassistant.components.camera import DEFAULT_CONTENT_TYPE, Camera
from homeassistant.components.stream import Stream
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import entity_registry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from my_bpost_api import BpostApi

from . import BpostEntryData
from .const import DOMAIN


async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Configure all sensors and expose as entities."""

    entry_data: BpostEntryData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        BpostCamera(entry_data.coordinator, sensor_id, entry_data.api)
        for sensor_id in entry_data.coordinator.data["camera"].keys()
    )

    def add_new_entities() -> None:
        entities = entity_registry.async_entries_for_config_entry(entity_registry.async_get(hass), entry.entry_id)
        current_ids = [
            entity.entity_id.split(".")[1]
            for entity in entities
            if entity.platform == DOMAIN and entity.domain == "camera"
        ]
        data_ids = entry_data.coordinator.data["camera"].keys()
        to_add = [entity_id for entity_id in data_ids if entity_id not in current_ids]

        async_add_entities(BpostCamera(entry_data.coordinator, sensor_id, entry_data.api) for sensor_id in to_add)

    entry_data.coordinator.async_add_listener(add_new_entities)


class BpostCamera(CoordinatorEntity, Camera):
    def __init__(self, coordinator: DataUpdateCoordinator, sensor_id: str, api: BpostApi):
        super().__init__(coordinator)
        self.sensor_id = sensor_id
        self._api = api
        self._image = None

        self.stream: Stream | None = None
        self.stream_options: dict[str, str] = {}
        self.content_type: str = DEFAULT_CONTENT_TYPE
        self.access_tokens: collections.deque = collections.deque([], 2)
        self._warned_old_signature = False
        self.async_update_token()

    @property
    def unique_id(self) -> str | None:
        return f"{DOMAIN}_{self.platform.domain}_{self.sensor_id}"

    @property
    def name(self) -> str | None:
        return self.sensor_id

    async def async_camera_image(self, width: int | None = None, height: int | None = None) -> bytes | None:
        if not self._image:
            await self._download_image()
        return self._image

    async def async_update(self) -> None:
        await super().async_update()
        await self._download_image()

    async def _download_image(self):
        self._image = await self._api.async_get_mail_image(
            self.coordinator.data[self.platform.domain][self.sensor_id]["data"]
        )

    @property
    def is_recording(self) -> bool:
        return False

    @property
    def is_streaming(self) -> bool:
        return False

    @property
    def motion_detection_enabled(self) -> bool:
        return False

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        return self.coordinator.data[self.platform.domain][self.sensor_id].get("extra")
