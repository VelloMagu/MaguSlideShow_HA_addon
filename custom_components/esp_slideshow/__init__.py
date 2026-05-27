import asyncio
import logging
import json
import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ESP Slideshow from a config entry."""
    coordinator = ESPSlideshowCoordinator(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Start the background websocket listener
    coordinator.start()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.async_stop()
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class ESPSlideshowCoordinator:
    """Manages the WebSocket connection and state updates."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        self.hass = hass
        self.entry = entry
        self.host = entry.data[CONF_HOST]
        self.name = entry.data[CONF_NAME]
        self.data = {}
        self._ws_task = None
        self._stop_event = asyncio.Event()
        self._listeners = []
        self._ws = None

    def start(self):
        """Start the WebSocket listener task."""
        self._stop_event.clear()
        self._ws_task = self.hass.async_create_background_task(
            self._ws_loop(), f"ESP Slideshow WS loop for {self.host}"
        )

    async def async_stop(self):
        """Stop the WebSocket coordinator."""
        self._stop_event.set()
        if self._ws_task:
            self._ws_task.cancel()
            try:
                await self._ws_task
            except asyncio.CancelledError:
                pass

    def register_listener(self, update_callback):
        """Register a callback to be called on state changes."""
        self._listeners.append(update_callback)

    def remove_listener(self, update_callback):
        """Remove a registered callback."""
        if update_callback in self._listeners:
            self._listeners.remove(update_callback)

    def _notify_listeners(self):
        """Notify all listeners of updated state."""
        for callback in self._listeners:
            callback()

    async def _ws_loop(self):
        """WS connection loop with auto-reconnect."""
        session = aiohttp.ClientSession()
        
        while not self._stop_event.is_set():
            url = f"http://{self.host}:81/"
            _LOGGER.info("Connecting to WebSocket: %s", url)
            try:
                async with session.ws_connect(url, timeout=10) as ws:
                    self._ws = ws
                    _LOGGER.info("Connected to ESP Slideshow on %s", self.host)
                    
                    async for msg in ws:
                        if self._stop_event.is_set():
                            break
                            
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            try:
                                payload = json.loads(msg.data)
                                self.data = payload
                                self._notify_listeners()
                            except ValueError as err:
                                _LOGGER.error("Failed to parse JSON message: %s", err)
                        elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                            _LOGGER.warning("WebSocket connection closed or errored")
                            break
            except Exception as err:
                _LOGGER.warning("WebSocket error connecting to %s: %s", self.host, err)
            finally:
                self._ws = None
            
            if not self._stop_event.is_set():
                # Wait 5 seconds before reconnecting
                await asyncio.sleep(5)
                
        await session.close()

    async def async_send_command(self, payload: dict):
        """Send a JSON command to the device."""
        if self._ws is not None and not self._ws.closed:
            try:
                await self._ws.send_str(json.dumps(payload))
                _LOGGER.debug("Sent WS command (active conn) to %s: %s", self.host, payload)
                return
            except Exception as err:
                _LOGGER.warning("Active WS send failed, trying temporary connection: %s", err)

        # Fallback to temporary connection
        url = f"http://{self.host}:81/"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(url, timeout=5) as ws:
                    await ws.send_str(json.dumps(payload))
                    _LOGGER.debug("Sent WS command (temp conn) to %s: %s", self.host, payload)
        except Exception as err:
            _LOGGER.error("Failed to send command to %s: %s", self.host, err)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        mac = self.data.get("mac", self.host)
        version = self.data.get("firmware", "v0.25")
        return DeviceInfo(
            identifiers={(DOMAIN, mac)},
            name=self.name,
            manufacturer="Waveshare",
            model="ESP32-S3 AMOLED Slideshow",
            sw_version=version,
        )
