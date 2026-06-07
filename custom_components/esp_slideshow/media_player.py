from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
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
    """Set up ESP Slideshow media player entity."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ESPSlideshowMediaPlayer(coordinator)])


class ESPSlideshowMediaPlayer(MediaPlayerEntity):
    """Media player representation for the ESP Slideshow device."""

    _attr_media_content_type = MediaType.IMAGE

    def __init__(self, coordinator: ESPSlideshowCoordinator) -> None:
        """Initialize media player."""
        self.coordinator = coordinator
        self._attr_name = coordinator.name
        self._attr_unique_id = f"{coordinator.host}_media_player"
        self._attr_device_info = coordinator.device_info
        self._attr_supported_features = (
            MediaPlayerEntityFeature.PLAY
            | MediaPlayerEntityFeature.PAUSE
            | MediaPlayerEntityFeature.NEXT_TRACK
            | MediaPlayerEntityFeature.PREVIOUS_TRACK
        )

    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return False

    @property
    def state(self) -> MediaPlayerState:
        """Return the current state of the media player."""
        if not self.coordinator.data.get("power_bool", True):
            return MediaPlayerState.OFF
        if self.coordinator.data.get("paused", False):
            return MediaPlayerState.PAUSED
        return MediaPlayerState.PLAYING

    @property
    def media_title(self) -> str | None:
        """Return the title of the currently playing media."""
        return self.coordinator.data.get("current", None)

    async def async_media_play(self) -> None:
        """Send play command."""
        await self.coordinator.async_send_command({"paused": False})

    async def async_media_pause(self) -> None:
        """Send pause command."""
        await self.coordinator.async_send_command({"paused": True})

    async def async_media_next_track(self) -> None:
        """Send next track command."""
        await self.coordinator.async_post_http("/api/next")

    async def async_media_previous_track(self) -> None:
        """Send previous track command."""
        await self.coordinator.async_post_http("/api/prev")

    async def async_added_to_hass(self) -> None:
        """Register update callback."""
        self.coordinator.register_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Unregister update callback."""
        self.coordinator.remove_listener(self.async_write_ha_state)
