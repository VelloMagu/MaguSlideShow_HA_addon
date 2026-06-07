import logging
import aiohttp
from homeassistant.components.update import (
    UpdateEntity,
    UpdateEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .__init__ import ESPSlideshowCoordinator

_LOGGER = logging.getLogger(__name__)

GITHUB_RELEASE_URL = "https://api.github.com/repos/VelloMagu/VMSlideShowReleases/releases/latest"

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ESP Slideshow update entity."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        ESPSlideshowUpdateEntity(coordinator),
    ])


class ESPSlideshowUpdateEntity(UpdateEntity):
    """Representation of an ESP Slideshow Update Entity."""

    _attr_has_entity_name = True
    _attr_title = "ESP Slideshow Firmware"

    def __init__(self, coordinator: ESPSlideshowCoordinator) -> None:
        """Initialize the update entity."""
        self.coordinator = coordinator
        self._attr_name = f"{coordinator.name} Firmware Update"
        self._attr_unique_id = f"{coordinator.host}_update"
        self._attr_device_info = coordinator.device_info
        self._attr_supported_features = UpdateEntityFeature.INSTALL
        
        self._latest_version = None
        self._release_notes = None
        self._download_url = None

    @property
    def installed_version(self) -> str | None:
        """Version installed and in use."""
        version = self.coordinator.data.get("firmware")
        if not version:
            return None
        # Clean potential 'v' prefix
        return version.lstrip('v')

    @property
    def latest_version(self) -> str | None:
        """Latest version available for install."""
        return self._latest_version

    @property
    def release_notes(self) -> str | None:
        """Release notes for the latest version."""
        return self._release_notes

    async def async_update(self) -> None:
        """Update entity state from GitHub releases."""
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(GITHUB_RELEASE_URL, timeout=10) as response:
                if response.status == 200:
                    release_data = await response.json()
                    tag = release_data.get("tag_name", "")
                    self._latest_version = tag.lstrip('v')
                    self._release_notes = release_data.get("body", "")
                    
                    # Look for a binary asset matching the device's hardware type (boardId)
                    board_id = self.coordinator.data.get("boardId", "waveshare_2_41")
                    self._download_url = None
                    assets = release_data.get("assets", [])
                    
                    # 1. Attempt: search for a .bin asset containing the board_id (case-insensitive)
                    for asset in assets:
                        name = asset.get("name", "")
                        if name.lower().endswith(".bin") and board_id.lower() in name.lower():
                            self._download_url = asset.get("browser_download_url")
                            _LOGGER.info("Found hardware-specific firmware binary for %s: %s", board_id, name)
                            break
                            
                    # 2. Fallback: if not found, grab the first generic/available .bin asset
                    if not self._download_url:
                        for asset in assets:
                            name = asset.get("name", "")
                            if name.lower().endswith(".bin"):
                                self._download_url = asset.get("browser_download_url")
                                _LOGGER.info("Falling back to first available firmware binary: %s", name)
                                break
                                
                    if not self._download_url:
                        _LOGGER.warning("No firmware binary (.bin) matching board ID '%s' found in the latest GitHub release", board_id)
                else:
                    _LOGGER.error("Failed to fetch latest release from GitHub: HTTP %s", response.status)
        except Exception as err:
            _LOGGER.error("Error checking for updates on GitHub: %s", err)

    async def async_install(self, version: str, backup: bool, **kwargs) -> None:
        """Install an update."""
        if not self._download_url:
            _LOGGER.error("No download URL available to install the update")
            return

        session = async_get_clientsession(self.hass)
        
        # 1. Download the firmware binary
        _LOGGER.info("Downloading ESP Slideshow firmware from %s", self._download_url)
        try:
            async with session.get(self._download_url) as response:
                if response.status != 200:
                    _LOGGER.error("Failed to download firmware binary: HTTP %s", response.status)
                    return
                firmware_data = await response.read()
        except Exception as err:
            _LOGGER.error("Error downloading firmware binary: %s", err)
            return

        # 2. Upload the binary to the device via POST /api/ota
        url = f"http://{self.coordinator.host}/api/ota"
        _LOGGER.info("Uploading firmware binary to ESP Slideshow via HTTP POST: %s", url)
        
        # Create form data containing the file
        data = aiohttp.FormData()
        data.add_field('firmware', firmware_data, filename='firmware.bin', content_type='application/octet-stream')

        try:
            # We set a large timeout of 120 seconds since flashing can take time
            async with session.post(url, data=data, timeout=120) as response:
                if response.status == 200:
                    _LOGGER.info("Successfully updated ESP Slideshow firmware. Device should be rebooting.")
                else:
                    body = await response.text()
                    _LOGGER.error("Failed to upload firmware to ESP Slideshow: HTTP %s - %s", response.status, body)
        except Exception as err:
            _LOGGER.error("Error uploading firmware to ESP Slideshow: %s", err)
