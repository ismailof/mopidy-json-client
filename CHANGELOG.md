# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.6] - Unreleased
### Added
- Simplified event binding. To subscribe to events use the `bind_event` method
- `get_client_version()` method
### Removed
- Merged `SimpleListener` and `MopidyListener`, and removed exposition
- No dependencies on Mopidy package

## [0.5.9] - Unreleased
### Added
- Retry connection if lost (parameters `retry_max` and `retry_secs`)
- Debug option (paramter `debug`)

### Fixed
- Fixed bug on connection retry attemps counting

## [0.5.2] - Unreleased
### Added
- Handle connection/disconnection to server WebSocket
- Important internal refactoring

## [0.4.8] - Unreleased
### Added
- API name changes. MopidyClient, SimpleClient, SimpleListener
- Bind callbacks to events using `bind` method
- Examples provided
- Server errors handling via callback

## [0.3.0] - Unreleased
### Added
- Mopidy controllers API can be automatically generated

