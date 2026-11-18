"""Config and options flow for the Huawei SUN2000 integration."""

import asyncio
from typing import TYPE_CHECKING, Any

from modbus_connection import ModbusError, ModbusTcpParams
import probatio

from homeassistant.components.modbus import async_get_temporary_unit
from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    CONF_SCAN_INTERVAL,
    CONF_UNIT_ID,
    CONNECT_TIMEOUT,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_UNIT_ID,
    DOMAIN,
    LOGGER,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from .vendor.huawei_modbus import MODEL, InverterProbe

if TYPE_CHECKING:
    from collections.abc import Mapping

    from .data import HuaweiSunConfigEntry

UNIT_ID_SELECTOR = NumberSelector(
    NumberSelectorConfig(min=1, max=247, step=1, mode=NumberSelectorMode.BOX)
)

STEP_USER_SCHEMA = probatio.Schema(
    {
        probatio.Required(CONF_HOST): probatio.All(
            TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT)),
            probatio.Length(min=1),
        ),
        probatio.Required(CONF_PORT, default=DEFAULT_PORT): NumberSelector(
            NumberSelectorConfig(min=1, max=65535, step=1, mode=NumberSelectorMode.BOX)
        ),
        probatio.Required(CONF_UNIT_ID, default=DEFAULT_UNIT_ID): UNIT_ID_SELECTOR,
    }
)


def connection_params(data: Mapping[str, Any]) -> ModbusTcpParams:
    """Build the link settings from stored entry data."""
    return ModbusTcpParams(
        host=str(data[CONF_HOST]),
        port=int(data[CONF_PORT]),
    )


class HuaweiSunConfigFlow(ConfigFlow, domain=DOMAIN):
    """Collect the connection details, then prove the inverter answers."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Collect the Modbus TCP endpoint and probe the inverter."""
        errors: dict[str, str] = {}
        if user_input is not None:
            host = str(user_input[CONF_HOST]).strip()
            port = int(user_input[CONF_PORT])
            unit_id = int(user_input[CONF_UNIT_ID])
            params = ModbusTcpParams(host=host, port=port)
            try:
                async with asyncio.timeout(CONNECT_TIMEOUT):
                    async with async_get_temporary_unit(
                        self.hass, params, unit_id
                    ) as unit:
                        probe = InverterProbe(unit)
                        await probe.async_update()
            except TimeoutError:
                LOGGER.error("Timed out waiting for the inverter at %s:%s", host, port)
                errors = {"base": "cannot_connect"}
            except (ModbusError, HomeAssistantError) as err:
                LOGGER.error(
                    "Could not read the inverter at %s:%s: %s", host, port, err
                )
                errors = {"base": "cannot_connect"}
            else:
                model = probe.model_name or MODEL
                serial = probe.serial_number or ""
                await self.async_set_unique_id(serial or f"{host}-{port}-{unit_id}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"{model} ({host})",
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_UNIT_ID: unit_id,
                    },
                )
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        _config_entry: HuaweiSunConfigEntry,
    ) -> HuaweiSunOptionsFlow:
        """Return the options flow."""
        return HuaweiSunOptionsFlow()


class HuaweiSunOptionsFlow(OptionsFlowWithReload):
    """Change how often the inverter is polled."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show and store the polling interval."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=probatio.Schema(
                {
                    probatio.Required(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=MIN_SCAN_INTERVAL,
                            max=MAX_SCAN_INTERVAL,
                            step=1,
                            mode=NumberSelectorMode.BOX,
                            unit_of_measurement="s",
                        )
                    )
                }
            ),
        )
