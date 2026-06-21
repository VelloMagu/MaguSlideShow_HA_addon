# Changelog

All notable changes to the Home Assistant integration (ESP Slideshow Addon) are documented here.

## [1.5.0] - 2026-06-21

### Added
- **Ambient light sensor**: Reports lux from VEML7700 or APDS-9960 when auto-brightness is enabled on firmware 1.5.0+.

## [1.3.5] - 2026-06-08

### Fixed
- **Update Reliability**: Fixed client timeouts in update checks, added periodic updates via `SCAN_INTERVAL`, and registered a listener for websocket-driven coordinator updates.
- **GitHub Rate Limits**: Log a warning when update checks hit GitHub API rate limits (HTTP 403).

## [1.3.4] - 2026-06-07

### Fixed
- **Initial Device Version**: Fetch `/api/info` synchronously on startup to ensure correct firmware version and MAC address are registered in Home Assistant immediately, resolving the old default version ("v0.25") issue.

## [1.3.3] - 2026-06-07

### Changed
- **Version Alignment**: Bump version to align with firmware 1.3.2 release.

## [1.3.2] - 2026-06-07

### Added
- **Dynamic Device Info**: Dynamically parse `manufacturer` and `model` from the device's reported `boardName` (e.g. Waveshare, LilyGO).
- **Hardware-Aware Updates**: Filter GitHub release assets by `boardId` to find and flash the matching hardware binary, preventing incorrect flashing.

## [1.3.1] - 2026-06-07

### Changed
- **Release Tracking Repo**: Changed firmware update tracking repository to `VMSlideShowReleases`.

## [1.3.0] - 2026-06-07

### Added
- **Update Platform**: Added an `update` entity to track and install ESP slideshow firmware updates directly from Home Assistant.

## [1.2.1] - 2026-06-07

### Added
- **Auto Rotation Option**: Added the "Auto (IMU)" option to the screen rotation dropdown menu.

## [1.2.0] - 2026-06-07

### Changed
- **Unified Media Control**: Replaced individual playback controls (switches, buttons) with a standard Home Assistant `media_player` entity.
- **Entity Categories**: Refactored entities by assigning appropriate Entity Categories (e.g. configuration entities placed in the Config category).

## [1.1.0] - 2026-06-06

### Added
- **Controls & Settings**: Added control and configuration entities for brightness, clock color, slide duration, and timezone selection.

## [1.0.0] - 2026-06-06

### Added
- **Initial Setup**: Initial skeleton and configuration setup for the ESP Slideshow Home Assistant custom component.
