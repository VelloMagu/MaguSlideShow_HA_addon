import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from .const import DOMAIN

class ESPSlideshowConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ESP Slideshow."""
    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow."""
        self._host = None
        self._name = None

    async def async_step_user(self, user_input=None):
        """Handle user-initiated flow."""
        errors = {}

        if user_input is not None:
            self._host = user_input[CONF_HOST]
            self._name = user_input.get(CONF_NAME, "ESP Slideshow")
            
            await self.async_set_unique_id(self._host)
            self._abort_if_unique_id_configured()
            
            return self.async_create_entry(
                title=self._name,
                data={CONF_HOST: self._host, CONF_NAME: self._name},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_NAME, default="ESP Slideshow"): str,
            }),
            errors=errors,
        )

    async def async_step_zeroconf(self, discovery_info: ZeroconfServiceInfo):
        """Handle zeroconf discovery."""
        host = discovery_info.host
        name = discovery_info.properties.get("device", "ESP Slideshow")
        
        self._host = host
        self._name = name
        
        await self.async_set_unique_id(self._host)
        self._abort_if_unique_id_configured()
        
        self.context["title_placeholders"] = {"name": self._name}
        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(self, user_input=None):
        """Confirm discovery."""
        if user_input is not None:
            return self.async_create_entry(
                title=self._name,
                data={CONF_HOST: self._host, CONF_NAME: self._name},
            )

        return self.async_show_form(
            step_id="discovery_confirm",
            description_placeholders={"name": self._name},
        )
