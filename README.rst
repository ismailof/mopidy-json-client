****************************
Mopidy-JSON-Client
****************************

Mopidy Client via JSON/RPC Websocket interface

This module is u

Current features include:
  - Remote Playback Control (play/pause/stop)
  - Remote Playback Monitor: Display Artist/Track/Album Info  

Pending features:
  - implement PlaylistController methods
  - execption and error handling
  - some refactor
  - check of mopidy JSON/RPC version and methods

Current version maps Mopidy 1.1.2. Next versions may break the functionality

Installation
============

Install by running:

    git clone git@github.com:ismailof/mopidy-json-client
    sudo python setup.py install
    

Usage
=====

mopidy-json-client provides two classes: 
    
    ::class::MopidyWSClient : manages the connection and methods to the Mopidy Server        
    ::class:MopidyWSListener : event handler

A demo application (::file::demo.py) is provided. It makes use of ::package::mopidy-json-client to implement a simple Mopidy CLI (Command Line Interface) client.
    

Project resources
=================

- `Source code <https://github.com/ismailof/mopidy-json-client`_
- `Issue tracker <https://github.com/ismailof/mopidy-json-client/issues>`_


Changelog
=========

v0.2.0 (UNRELEASED)
----------------------------------------
- Initial release on Git
