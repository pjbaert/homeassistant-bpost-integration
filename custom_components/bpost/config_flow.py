"""Config flow for bpost integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_CODE, CONF_EMAIL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from my_bpost_api import AuthenticationException, BpostApi, BpostApiException

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_EMAIL_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
    }
)

STEP_USER_VERIFICATION_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CODE): str,
    }
)


async def validate_email(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate that the account exists and send a verification code if so."""
    email_address = data.get(CONF_EMAIL)
    if email_address is None:
        raise ValueError("No email address provided")

    email_address = email_address.lower()

    async with BpostApi(
        email=email_address,
        session_callback=lambda: async_get_clientsession(hass, True),
    ) as bpost_api:
        try:
            await bpost_api.async_users_email_login()
        except AuthenticationException as exc:
            raise InvalidAuth(exc)
        except BpostApiException as exc:
            raise CannotConnect(exc)
        else:
            return {
                CONF_EMAIL: bpost_api.email,
            }


async def validate_code(hass: HomeAssistant, email_address: str, data: dict[str, Any]) -> dict[str, Any]:
    code = data.get(CONF_CODE)
    if code is None:
        raise ValueError("No verification code provided")

    async with BpostApi(
        email=email_address,
        session_callback=lambda: async_get_clientsession(hass, True),
    ) as bpost_api:
        try:
            await bpost_api.async_users_email_login_verify_code(code)
        except AuthenticationException as exc:
            raise InvalidAuth(exc)
        except BpostApiException as exc:
            raise CannotConnect(exc)
        else:
            return {
                "email": bpost_api.email,
                "token": bpost_api.token,
                "refresh_token": bpost_api.refresh_token,
            }


class BpostConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore
    """Handle a config flow for BPost."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""

        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=STEP_USER_EMAIL_SCHEMA)

        errors = {}

        try:
            info = await validate_email(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except ValueError:
            errors[CONF_EMAIL] = "invalid_email"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            await self.async_set_unique_id(info[CONF_EMAIL])
            self._abort_if_unique_id_configured()
            return await self.async_step_verify_code()

        return self.async_show_form(step_id="user", data_schema=STEP_USER_EMAIL_SCHEMA, errors=errors)

    async def async_step_verify_code(self, user_input: dict | None = None) -> FlowResult:
        """Handle the verification code step."""

        if user_input is None:
            return self.async_show_form(
                step_id="verify_code",
                data_schema=STEP_USER_VERIFICATION_SCHEMA,
            )

        errors = {}

        try:
            info = await validate_code(self.hass, self.unique_id, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except ValueError:
            errors[CONF_CODE] = "invalid_code"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return await self.async_create_or_update_entry(info)

        return self.async_show_form(
            step_id="verify_code",
            data_schema=STEP_USER_VERIFICATION_SCHEMA,
            errors=errors,
        )

    async def async_create_or_update_entry(self, info: dict[str, Any]) -> FlowResult:
        """Create or update entry."""
        existing_entry = await self.async_set_unique_id(info[CONF_EMAIL])
        if existing_entry:
            self.hass.config_entries.async_update_entry(existing_entry, data=info)
            await self.hass.config_entries.async_reload(existing_entry.entry_id)
            return self.async_abort(reason="reauth_successful")
        else:
            return self.async_create_entry(title=info[CONF_EMAIL], data=info)

    async def async_step_reauth(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle reauthentication."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle reauthentication confirmation."""
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=vol.Schema({}),
            )

        await validate_email(self.hass, {CONF_EMAIL: self.unique_id})
        return await self.async_step_verify_code(user_input)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
