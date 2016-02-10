****************************
Mopidy-JSON-Client
****************************

Mopidy Client via JSON/RPC Websocket interface

This module generates a python interface which maps the `Mopidy Core API <https://mopidy.readthedocs.org/en/latest/api/core>`_ methods and events, as described in `mopidy.readthedocs.org/en/latest/api/core <https://mopidy.readthedocs.org/en/latest/api/core>`_ .
It makes use of `websocket_client <https://github.com/liris/websocket_client>`_

Current version maps Mopidy 1.1.2 JSON/RPC API.
If API methods change the API controllers should be generated using 'generate_api.py'


Pending features:
  - exception handling
  - some refactoring needed
  - check for mopidy JSON/RPC version and methods


Installation
============

Install by running:

    git clone git@github.com:ismailof/mopidy-json-client
    sudo python setup.py install


Usage
=====

mopidy-json-client provides two classes:
   - '::class::MopidyWSClient'  : manages the connection and methods to the Mopidy Server
   - '::class:MopidyWSListener' : event handler

A demo application (demo.py) is provided. It makes use of ::package::mopidy-json-client to implement a simple Mopidy CLI (Command Line Interface) client.


Project resources
=================

- `Source code <https://github.com/ismailof/mopidy-json-client>`_
- `Issue tracker <https://github.com/ismailof/mopidy-json-client/issues>`_


Changelog
=========

v0.3.2 (UNRELEASED)
----------------------------------------
- Added server errors handling via callback

v0.3.0 (UNRELEASED)
----------------------------------------
- Mopidy controllers API can be automatically generated

v0.2.0 (UNRELEASED)
----------------------------------------
- Initial release on Git
