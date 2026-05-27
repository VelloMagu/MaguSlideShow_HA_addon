from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
)
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
    """Set up ESP Slideshow light entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        ESPSlideshowScreenLight(coordinator),
        ESPSlideshowClockLight(coordinator),
    ])


class ESPSlideshowScreenLight(LightEntity):
    """Representation of the ESP Slideshow Screen light (power/brightness)."""

    def __init__(self, coordinator: ESPSlideshowCoordinator) -> None:
        """Initialize light."""
        self.coordinator = coordinator
        self._attr_name = f"{coordinator.name} Screen"
        self._attr_unique_id = f"{coordinator.host}_screen"
        self._attr_device_info = coordinator.device_info
        self._attr_color_mode = ColorMode.BRIGHTNESS
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    @property
    def should_poll(self) -> bool:
        """No polling needed for push updates."""
        return False

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self.coordinator.data.get("power_bool", True)

    @property
    def brightness(self) -> int:
        """Return the brightness of this light between 0..255."""
        val_percent = self.coordinator.data.get("brightness", 80)
        return int((val_percent * 255) / 100)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the light on or adjust brightness."""
        payload = {}
        if ATTR_BRIGHTNESS in kwargs:
            brightness_percent = int((kwargs[ATTR_BRIGHTNESS] * 100) / 255)
            # Ensure brightness is within bounds
            brightness_percent = max(5, min(100, brightness_percent))
            payload["brightness"] = brightness_percent
            
        payload["power_bool"] = True
        await self.coordinator.async_send_command(payload)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the light off."""
        await self.coordinator.async_send_command({"power_bool": False})

    async def async_added_to_hass(self) -> None:
        """Register update callback."""
        self.coordinator.register_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Unregister update callback."""
        self.coordinator.remove_listener(self.async_write_ha_state)


class ESPSlideshowClockLight(LightEntity):
    """Representation of the ESP Slideshow Clock face (on/off and color)."""

    def __init__(self, coordinator: ESPSlideshowCoordinator) -> None:
        """Initialize light."""
        self.coordinator = coordinator
        self._attr_name = f"{coordinator.name} Clock"
        self._attr_unique_id = f"{coordinator.host}_clock"
        self._attr_device_info = coordinator.device_info
        self._attr_color_mode = ColorMode.RGB
        self._attr_supported_color_modes = {ColorMode.RGB}

    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return False

    @property
    def is_on(self) -> bool:
        """Return true if clock is enabled."""
        return self.coordinator.data.get("clockEnabled", False)

    @property
    def rgb_color(self) -> tuple[int, int, int]:
        """Return the rgb color value."""
        hex_color = self.coordinator.data.get("clockTimeColor", "#00f2fe")
        hex_color = hex_color.lstrip("#")
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except Exception:
            return (0, 242, 254) # fallback

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the clock display on and/or set color."""
        payload = {"clockEnabled": True}
        if ATTR_RGB_COLOR in kwargs:
            rgb = kwargs[ATTR_RGB_COLOR]
            hex_color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
            payload["clockTimeColor"] = hex_color
            
        await self.coordinator.async_send_command(payload)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the clock display off."""
        await self.coordinator.async_send_command({"clockEnabled": False})

    async def async_added_to_hass(self) -> None:
        """Register update callback."""
        self.coordinator.register_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Unregister update callback."""
        self.coordinator.remove_listener(self.async_write_ha_state)
