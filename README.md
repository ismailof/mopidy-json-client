# Mopidy-JSON-Client [![version](https://img.shields.io/badge/version-0.6.0-blue.svg)](./CHANGELOG.md)

Mopidy Client via JSON/RPC Websocket interface

This module generates a python interface which maps the [Mopidy Core API] methods and events.
For the websocket connection internals, it makes use of [websocket_client] package.

Current version supports `Mopidy 1.1` and `Mopidy 2.0` JSON/RPC API methods and events.

From version `0.5.0`, a major refactoring in code has been done to allow handling connection and disconnection to the Websocket, by means of the methods `connect()`. `disconnect()` and `is_connected()`. By default it will keep trying to reconnect to the mopidy Websocket when the connection is lost.

**This package is yet to be largely improved, so package API changes can be expected in any version**. API to Mopidy calls will remain.

## Usage

mopidy-json-client provides a main class `MopidyClient`, which manages the connection and methods to the Mopidy Server.
Use the `bind_event` function to subscribe to mopidy events.

```python
from mopidy_json_client import MopidyClient

mopidy = MopidyClient()
mopidy.bind_event('track_playback_started', print_track_info)
mopidy.playback.play()
```

To ilustrate the use of the module, check in the examples folder:
   - [now_playing.py](./examples/now_playing.py): simple script that prints the song on every track start event
   - [demo_cli.py](./examples/demo_cli.py) implements a simple Mopidy CLI (Command Line Interface) client.
   - [demo_volumen_gpio.py](./examples/demo_volumen_gpio.py) controls the volume and mute using a HW RotaryEncoder knob through the RPi.GPIO interface

## Installation

This module is not yet upload to PyPI repository. I'm looking forward to it in a near future.

Install by running:
- `sudo pip install https://github.com/ismailof/mopidy-json-client/archive/master.zip`

or
- `git clone https://github.com/ismailof/mopidy-json-client`
- `sudo pip install mopidy-json-client`

## Pending features:
  - better exception handling

## Project resources

- Source code: <https://github.com/ismailof/mopidy-json-client>
- Issue tracker: <https://github.com/ismailof/mopidy-json-client/issues>

## References
- [Mopidy Core API](https://mopidy.readthedocs.org/en/latest/api/core)
- [websocket_client](https://github.com/liris/websocket_client)