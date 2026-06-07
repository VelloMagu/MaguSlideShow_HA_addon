from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .__init__ import ESPSlideshowCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ESP Slideshow button entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        ESPSlideshowSyncTimeButton(coordinator),
    ])


class ESPSlideshowSyncTimeButton(ButtonEntity):
    """Representation of the Sync Time button."""

    def __init__(self, coordinator: ESPSlideshowCoordinator) -> None:
        """Initialize button."""
        self.coordinator = coordinator
        self._attr_name = f"{coordinator.name} Sync Time"
        self._attr_unique_id = f"{coordinator.host}_synctime"
        self._attr_device_info = coordinator.device_info
        self._attr_entity_category = EntityCategory.CONFIG

    async def async_press(self) -> None:
        """Press the button."""
        await self.coordinator.async_post_http("/api/synctime")
