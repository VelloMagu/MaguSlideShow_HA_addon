from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import LIGHT_LUX
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
    """Set up ESP Slideshow sensor entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ESPSlideshowAmbientLightSensor(coordinator)])


class ESPSlideshowAmbientLightSensor(SensorEntity):
    """Ambient light (lux) from the device's auto-brightness sensor."""

    def __init__(self, coordinator: ESPSlideshowCoordinator) -> None:
        """Initialize sensor entity."""
        self.coordinator = coordinator
        self._attr_name = f"{coordinator.name} Ambient Light"
        self._attr_unique_id = f"{coordinator.host}_ambient_lux"
        self._attr_device_info = coordinator.device_info
        self._attr_device_class = SensorDeviceClass.ILLUMINANCE
        self._attr_native_unit_of_measurement = LIGHT_LUX
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return False

    @property
    def available(self) -> bool:
        """Sensor is available when auto-brightness is on and lux is reported."""
        data = self.coordinator.data
        if not data.get("sensorsSupported"):
            return False
        if not data.get("autoBrightness"):
            return False
        lux = data.get("ambientLux")
        return lux is not None and float(lux) >= 0

    @property
    def native_value(self) -> float | None:
        """Return illuminance in lux."""
        lux = self.coordinator.data.get("ambientLux")
        if lux is None:
            return None
        value = float(lux)
        return value if value >= 0 else None

    async def async_added_to_hass(self) -> None:
        """Register update callback."""
        self.coordinator.register_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Unregister update callback."""
        self.coordinator.remove_listener(self.async_write_ha_state)
