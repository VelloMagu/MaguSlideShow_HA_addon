from homeassistant.components.switch import SwitchEntity
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
    """Set up ESP Slideshow switch entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        ESPSlideshowPlayPauseSwitch(coordinator),
        ESPSlideshowClockSwitch(coordinator),
        ESPSlideshowRtcSwitch(coordinator),
    ])


class ESPSlideshowPlayPauseSwitch(SwitchEntity):
    """Representation of the Slideshow Play/Pause switch."""

    def __init__(self, coordinator: ESPSlideshowCoordinator) -> None:
        """Initialize switch."""
        self.coordinator = coordinator
        self._attr_name = f"{coordinator.name} Play/Pause"
        self._attr_unique_id = f"{coordinator.host}_play_pause"
        self._attr_device_info = coordinator.device_info

    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return False

    @property
    def is_on(self) -> bool:
        """Return true if slideshow is playing."""
        return not self.coordinator.data.get("paused", False)

    async def async_turn_on(self, **kwargs) -> None:
        """Resume the slideshow."""
        await self.coordinator.async_send_command({"paused": False})

    async def async_turn_off(self, **kwargs) -> None:
        """Pause the slideshow."""
        await self.coordinator.async_send_command({"paused": True})

    async def async_added_to_hass(self) -> None:
        """Register callback."""
        self.coordinator.register_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Unregister callback."""
        self.coordinator.remove_listener(self.async_write_ha_state)


class ESPSlideshowClockSwitch(SwitchEntity):
    """Representation of the Clock Enable switch."""

    def __init__(self, coordinator: ESPSlideshowCoordinator) -> None:
        """Initialize switch."""
        self.coordinator = coordinator
        self._attr_name = f"{coordinator.name} Clock"
        self._attr_unique_id = f"{coordinator.host}_clock_enable"
        self._attr_device_info = coordinator.device_info

    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return False

    @property
    def is_on(self) -> bool:
        """Return true if clock is enabled."""
        return self.coordinator.data.get("clockEnabled", False)

    async def async_turn_on(self, **kwargs) -> None:
        """Enable clock overlay."""
        await self.coordinator.async_send_command({"clockEnabled": True})

    async def async_turn_off(self, **kwargs) -> None:
        """Disable clock overlay."""
        await self.coordinator.async_send_command({"clockEnabled": False})

    async def async_added_to_hass(self) -> None:
        """Register callback."""
        self.coordinator.register_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Unregister callback."""
        self.coordinator.remove_listener(self.async_write_ha_state)


class ESPSlideshowRtcSwitch(SwitchEntity):
    """Representation of the Use RTC switch."""

    def __init__(self, coordinator: ESPSlideshowCoordinator) -> None:
        """Initialize switch."""
        self.coordinator = coordinator
        self._attr_name = f"{coordinator.name} Use RTC"
        self._attr_unique_id = f"{coordinator.host}_rtc_enable"
        self._attr_device_info = coordinator.device_info

    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return False

    @property
    def is_on(self) -> bool:
        """Return true if RTC is enabled."""
        return self.coordinator.data.get("rtcEnabled", False)

    async def async_turn_on(self, **kwargs) -> None:
        """Enable RTC."""
        await self.coordinator.async_send_command({"rtcEnabled": True})

    async def async_turn_off(self, **kwargs) -> None:
        """Disable RTC."""
        await self.coordinator.async_send_command({"rtcEnabled": False})

    async def async_added_to_hass(self) -> None:
        """Register callback."""
        self.coordinator.register_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Unregister callback."""
        self.coordinator.remove_listener(self.async_write_ha_state)
