****************************
Mopidy-JSON-Client
****************************

Mopidy Client via JSON/RPC Websocket interface

This module generates a python interface which maps the `Mopidy Core API <https://mopidy.readthedocs.org/en/latest/api/core>`_ methods and events, as described in `mopidy.readthedocs.org/en/latest/api/core <https://mopidy.readthedocs.org/en/latest/api/core>`_ .
It makes use of `websocket_client <https://github.com/liris/websocket_client>`_

Current version supports Mopidy 1.1 and Mopidy 2.0 JSON/RPC API methods and events. API version of Mopidy server will be automatically detected and used.

For now, connection/disconnection details are not handled. Mopidy-JSON-Client just assumes a running version of Mopidy server accesible via the HTTP Websockets interface. Otherwise, an Exception will be raised.

Pending features:
  - connection/disconnection management
  - exception handling
  - some refactoring needed


Installation
============

Install by running:

    git clone git@github.com:ismailof/mopidy-json-client
    sudo pip install mopidy-json-client


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
