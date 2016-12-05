****************************
Mopidy-JSON-Client
****************************

Mopidy Client via JSON/RPC Websocket interface

This module generates a python interface which maps the `Mopidy Core API <https://mopidy.readthedocs.org/en/latest/api/core>`_ methods and events, as described in `mopidy.readthedocs.org/en/latest/api/core <https://mopidy.readthedocs.org/en/latest/api/core>`_ .
It makes use of `websocket_client <https://github.com/liris/websocket_client>`_

Current version supports Mopidy 1.1 and Mopidy 2.0 JSON/RPC API methods and events. API version of Mopidy server will be automatically detected and used.

From version 0.5.0, a major refactoring in code has been done. Now it handles connection and disconnection to the Websocket. By default it will keep trying to reconnect to the mopidy Websocket when the connection is lost. It can includes the functions `connect()`. `disconnect()` and `is_connected()`

**This package is yet to be largely improved, so package API changes can be expected in any version**. API to Mopidy calls will remain.

Pending features:
  - exception handling
  - some refactoring needed


Installation
============

Install by running:
``sudo pip install https://github.com/ismailof/mopidy-json-client/archive/master.zip``
or 
``git clone https://github.com/ismailof/mopidy-json-client``, 
and then   
``sudo pip install mopidy-json-client``

This module is not yet upload to PyPI repository. I'm looking forward to it in a near future.

Usage
=====

mopidy-json-client provides two main classes:
   - 'MopidyClient' : manages the connection and methods to the Mopidy Server
   - 'MopidyListener' : event handler

To ilustrate the use of the module, two examples are provided:
   - demo_cli.py implements a simple Mopidy CLI (Command Line Interface) client.
   - demo_volumen_gpio.py controls the volume and mute using a HW RotaryEncoder knob through the RPi.GPIO interface


Project resources
=================

- `Source code <https://github.com/ismailof/mopidy-json-client>`_
- `Issue tracker <https://github.com/ismailof/mopidy-json-client/issues>`_


Changelog
=========

v0.5.6 (UNRELEASED)
----------------------------------------
- Retry connection if lost (parameters `retry_max` and `retry_secs`)
- Debug option (paramter `debug`)

v0.5.2 (UNRELEASED)
----------------------------------------
- Handle connection/disconnection to server WebSocket
- Important internal refactoring

v0.4.8 (UNRELEASED)
----------------------------------------
- API name changes. MopidyClient, SimpleClient, SimpleListener
- Bind callbacks to events using bind method
- Examples provided

v0.3.4 (UNRELEASED)
----------------------------------------
- Small tweaks
- Added server errors handling via callback

v0.3.0 (UNRELEASED)
----------------------------------------
- Mopidy controllers API can be automatically generated

v0.2.0 (UNRELEASED)
----------------------------------------
- Initial release on Git
