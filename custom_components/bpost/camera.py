from __future__ import annotations

import collections
from typing import Any, Mapping

from homeassistant.components.camera import DEFAULT_CONTENT_TYPE, Camera
from homeassistant.components.stream import Stream
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from my_bpost_api import BpostApi

from . import BpostEntryData
from .const import DOMAIN


async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Configure all sensors and expose as entities."""

    entry_data: BpostEntryData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        BpostCamera(entry_data.coordinator, ent, entry_data.api.token)
        for idx, ent in enumerate(entry_data.coordinator.data["camera"])
    )


class BpostCamera(CoordinatorEntity, Camera):
    def __init__(self, coordinator: DataUpdateCoordinator, sensor_id: str, token: str):
        super().__init__(coordinator)
        self.sensor_id = sensor_id
        self._token = token
        self._image = None

        self.is_streaming: bool = False
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
        bpost_api = BpostApi(
            token=self._token,
            email=None,
            session_callback=lambda: async_get_clientsession(self.hass, True),
        )
        self._image = await bpost_api.async_get_mail_image(
            self.coordinator.data[self.platform.domain][self.sensor_id]["data"]
        )

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        return self.coordinator.data[self.platform.domain][self.sensor_id].get("extra")
