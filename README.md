# Mopidy-JSON-Client [![version](https://img.shields.io/badge/version-0.5.9-blue.svg)][CHANGELOG]

Mopidy Client via JSON/RPC Websocket interface

This module generates a python interface which maps the [Mopidy Core API](https://mopidy.readthedocs.org/en/latest/api/core) methods and events, as described in <https://mopidy.readthedocs.org/en/latest/api/core>.
It makes use of [websocket_client](https://github.com/liris/websocket_client)

Current version supports Mopidy 1.1 and Mopidy 2.0 JSON/RPC API methods and events. API version of Mopidy server will be automatically detected and used.

From version 0.5.0, a major refactoring in code has been done. Now it handles connection and disconnection to the Websocket. By default it will keep trying to reconnect to the mopidy Websocket when the connection is lost. It can includes the functions `connect()`. `disconnect()` and `is_connected()`

**This package is yet to be largely improved, so package API changes can be expected in any version**. API to Mopidy calls will remain.

## Pending features:
  - better exception handling

## Installation

This module is not yet upload to PyPI repository. I'm looking forward to it in a near future.

Install by running:
- `sudo pip install https://github.com/ismailof/mopidy-json-client/archive/master.zip`

or 
- `git clone https://github.com/ismailof/mopidy-json-client` 
- `sudo pip install mopidy-json-client`

## Usage

mopidy-json-client provides two main classes:
   - 'MopidyClient' : manages the connection and methods to the Mopidy Server
   - 'MopidyListener' : event handler

To ilustrate the use of the module, two examples are provided:
   - demo_cli.py implements a simple Mopidy CLI (Command Line Interface) client.
   - demo_volumen_gpio.py controls the volume and mute using a HW RotaryEncoder knob through the RPi.GPIO interface

## Project resources

- Source code: <https://github.com/ismailof/mopidy-json-client>
- Issue tracker: <https://github.com/ismailof/mopidy-json-client/issues>


