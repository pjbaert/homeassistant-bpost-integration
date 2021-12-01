from datetime import timedelta
from logging import Logger
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from my_bpost_api import AuthenticationException, BpostApi, BpostApiException


async def async_update_sensors(bpost_api: BpostApi):
    mail = await bpost_api.async_fetch_mail()

    sensor_data = {"mail_today": {"data": len(mail["Active"]), "extra": {"mail_ids": []}}}

    binary_sensor_data = {
        "mail_processed_today": {"data": not mail["isHoliday"] and not mail["isMailProcessed"]},
        "mail_service_available": {"data": mail["isMMTSubscribed"]},
    }

    camera_data = {}
    for active_mail in mail["Active"]:
        camera_data[active_mail["tagId"]] = {
            "data": active_mail["mailURL"],
            "extra": {"expected_delivery_date": active_mail["expectedDeliveryDate"]},
        }
        sensor_data["mail_today"]["extra"]["mail_ids"].append(active_mail["tagId"])  # type: ignore

    return {
        "sensor": sensor_data,
        "binary_sensor": binary_sensor_data,
        "camera": camera_data,
    }


class BpostEntryData:
    def __init__(self, hass: HomeAssistant, data: dict[str, Any], logger: Logger) -> None:
        super().__init__()
        self.api = BpostApi(
            email=data["email"],
            token=data["token"],
            refresh_token=data["refresh_token"],
            session_callback=lambda: async_get_clientsession(hass, True),
        )

        async def async_update_data() -> dict[str, Any]:
            try:
                return await async_update_sensors(self.api)
            except AuthenticationException as ex:
                raise ConfigEntryAuthFailed(ex)
            except BpostApiException as ex:
                raise UpdateFailed(f"Error communicating with API: {ex}")

        self.coordinator = DataUpdateCoordinator(
            hass,
            logger,
            name="bpost",
            update_method=async_update_data,
            update_interval=timedelta(hours=1),
        )
