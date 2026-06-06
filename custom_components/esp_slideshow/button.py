from homeassistant.components.button import ButtonEntity
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
        ESPSlideshowPrevButton(coordinator),
        ESPSlideshowNextButton(coordinator),
        ESPSlideshowSyncTimeButton(coordinator),
    ])


class ESPSlideshowPrevButton(ButtonEntity):
    """Representation of the Prev button."""

    def __init__(self, coordinator: ESPSlideshowCoordinator) -> None:
        """Initialize button."""
        self.coordinator = coordinator
        self._attr_name = f"{coordinator.name} Previous"
        self._attr_unique_id = f"{coordinator.host}_prev"
        self._attr_device_info = coordinator.device_info

    async def async_press(self) -> None:
        """Press the button."""
        await self.coordinator.async_post_http("/api/prev")


class ESPSlideshowNextButton(ButtonEntity):
    """Representation of the Next button."""

    def __init__(self, coordinator: ESPSlideshowCoordinator) -> None:
        """Initialize button."""
        self.coordinator = coordinator
        self._attr_name = f"{coordinator.name} Next"
        self._attr_unique_id = f"{coordinator.host}_next"
        self._attr_device_info = coordinator.device_info

    async def async_press(self) -> None:
        """Press the button."""
        await self.coordinator.async_post_http("/api/next")


class ESPSlideshowSyncTimeButton(ButtonEntity):
    """Representation of the Sync Time button."""

    def __init__(self, coordinator: ESPSlideshowCoordinator) -> None:
        """Initialize button."""
        self.coordinator = coordinator
        self._attr_name = f"{coordinator.name} Sync Time"
        self._attr_unique_id = f"{coordinator.host}_synctime"
        self._attr_device_info = coordinator.device_info

    async def async_press(self) -> None:
        """Press the button."""
        await self.coordinator.async_post_http("/api/synctime")
