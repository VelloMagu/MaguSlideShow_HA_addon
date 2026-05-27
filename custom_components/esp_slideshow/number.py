from homeassistant.components.number import NumberEntity, NumberMode
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
    """Set up ESP Slideshow number entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        ESPSlideshowDurationNumber(coordinator),
        ESPSlideshowClockIntervalNumber(coordinator),
    ])


class ESPSlideshowDurationNumber(NumberEntity):
    """Representation of the Slideshow Duration number setting."""

    def __init__(self, coordinator: ESPSlideshowCoordinator) -> None:
        """Initialize number entity."""
        self.coordinator = coordinator
        self._attr_name = f"{coordinator.name} Slideshow Duration"
        self._attr_unique_id = f"{coordinator.host}_slideshow_duration"
        self._attr_device_info = coordinator.device_info
        self._attr_native_min_value = 1
        self._attr_native_max_value = 300
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = "s"
        self._attr_mode = NumberMode.BOX

    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return False

    @property
    def native_value(self) -> float:
        """Return the value of the entity."""
        return float(self.coordinator.data.get("slideshowDuration", 5))

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        await self.coordinator.async_send_command({"slideshowDuration": int(value)})

    async def async_added_to_hass(self) -> None:
        """Register update callback."""
        self.coordinator.register_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Unregister update callback."""
        self.coordinator.remove_listener(self.async_write_ha_state)


class ESPSlideshowClockIntervalNumber(NumberEntity):
    """Representation of the Clock Interval number setting."""

    def __init__(self, coordinator: ESPSlideshowCoordinator) -> None:
        """Initialize number entity."""
        self.coordinator = coordinator
        self._attr_name = f"{coordinator.name} Clock Interval"
        self._attr_unique_id = f"{coordinator.host}_clock_interval"
        self._attr_device_info = coordinator.device_info
        self._attr_native_min_value = 1
        self._attr_native_max_value = 10
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = "slides"
        self._attr_mode = NumberMode.BOX

    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return False

    @property
    def native_value(self) -> float:
        """Return the value of the entity."""
        return float(self.coordinator.data.get("clockInterval", 5))

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        await self.coordinator.async_send_command({"clockInterval": int(value)})

    async def async_added_to_hass(self) -> None:
        """Register update callback."""
        self.coordinator.register_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Unregister update callback."""
        self.coordinator.remove_listener(self.async_write_ha_state)
