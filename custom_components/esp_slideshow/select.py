from homeassistant.components.select import SelectEntity
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
    """Set up ESP Slideshow select entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        ESPSlideshowClockFormatSelect(coordinator),
        ESPSlideshowTimezoneSelect(coordinator),
        ESPSlideshowRotationSelect(coordinator),
    ])


class ESPSlideshowClockFormatSelect(SelectEntity):
    """Representation of the Clock Format select (12h/24h)."""

    _attr_options = ["12-Hour", "24-Hour"]

    def __init__(self, coordinator: ESPSlideshowCoordinator) -> None:
        """Initialize select."""
        self.coordinator = coordinator
        self._attr_name = f"{coordinator.name} Clock Format"
        self._attr_unique_id = f"{coordinator.host}_clock_format"
        self._attr_device_info = coordinator.device_info
        self._attr_entity_category = EntityCategory.CONFIG

    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return False

    @property
    def current_option(self) -> str:
        """Return the selected option."""
        return "24-Hour" if self.coordinator.data.get("clock24h", False) else "12-Hour"

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        val = (option == "24-Hour")
        await self.coordinator.async_send_command({"clock24h": val})

    async def async_added_to_hass(self) -> None:
        """Register callback."""
        self.coordinator.register_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Unregister callback."""
        self.coordinator.remove_listener(self.async_write_ha_state)


class ESPSlideshowTimezoneSelect(SelectEntity):
    """Representation of the Timezone select."""

    def __init__(self, coordinator: ESPSlideshowCoordinator) -> None:
        """Initialize select."""
        self.coordinator = coordinator
        self._attr_name = f"{coordinator.name} Timezone"
        self._attr_unique_id = f"{coordinator.host}_timezone"
        self._attr_device_info = coordinator.device_info
        self._attr_entity_category = EntityCategory.CONFIG

    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return False

    @property
    def options(self) -> list[str]:
        """Return the list of available options."""
        return self.coordinator.timezones

    @property
    def current_option(self) -> str:
        """Return the selected option."""
        val = self.coordinator.data.get("timezoneName", "UTC")
        if val in self.options:
            return val
        return "UTC"

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self.coordinator.async_send_command({"timezoneName": option, "timezoneAuto": False})

    async def async_added_to_hass(self) -> None:
        """Register callback."""
        self.coordinator.register_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Unregister callback."""
        self.coordinator.remove_listener(self.async_write_ha_state)


class ESPSlideshowRotationSelect(SelectEntity):
    """Representation of the Screen Rotation select."""

    _attr_options = ["Portrait", "Landscape", "Portrait 180°", "Landscape 270°", "Auto (IMU)"]

    def __init__(self, coordinator: ESPSlideshowCoordinator) -> None:
        """Initialize select."""
        self.coordinator = coordinator
        self._attr_name = f"{coordinator.name} Screen Rotation"
        self._attr_unique_id = f"{coordinator.host}_screen_rotation"
        self._attr_device_info = coordinator.device_info
        self._attr_entity_category = EntityCategory.CONFIG

    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return False

    @property
    def current_option(self) -> str:
        """Return the selected option."""
        val = self.coordinator.data.get("orientation", 0)
        if 0 <= val < len(self._attr_options):
            return self._attr_options[val]
        return self._attr_options[0]

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option in self._attr_options:
            val = self._attr_options.index(option)
            await self.coordinator.async_send_command({"orientation": val})

    async def async_added_to_hass(self) -> None:
        """Register callback."""
        self.coordinator.register_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Unregister callback."""
        self.coordinator.remove_listener(self.async_write_ha_state)
