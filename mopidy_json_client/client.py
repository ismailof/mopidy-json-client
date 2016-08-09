import logging
from distutils.version import LooseVersion

from .mopidy_api import CoreController
from .connection import MopidyWSManager
from .listener import MopidyListener
from .queue import RequestQueue

from debug import debug_function


logger = logging.getLogger(__name__)


class SimpleClient(object):

    def __init__(self,
                 server_addr='localhost:6680',
                 event_handler=None,
                 error_handler=None,
                 connection_handler=None,
                 autoconnect=True,
                 reconnect_tries=3,
                 reconnect_secs=5
                 ):

        # Event and error handlers
        self.event_handler = event_handler
        self.error_handler = error_handler
        self.connection_handler = connection_handler
        
        # Reconnect
        #self.reconnect = reconnect        
        
        # Init WebSocket manager
        self.ws_manager = MopidyWSManager(on_msg_event=self._handle_event,
                                          on_msg_result=self._handle_result,
                                          on_msg_error=self._handle_error,
                                          on_connection=self._handle_connection)
        
        # Connection to Mopidy Websocket Server
        ws_url = 'ws://' + server_addr + '/mopidy/ws'
        self.ws_url = ws_url
        
        if autoconnect:                 
            self.ws_manager.connect_ws(url=self.ws_url)

        # Request Queue
        self.request_queue = RequestQueue(send_function=self._send_message)

        # Core controller
        self.core = CoreController(self._server_request)

    def connect(self):        
        self.ws_manager.connect_ws()

    def disconnect(self):
        self.reconnect = False
        self.ws_manager.close()
    
    def is_connected(self):
        return self.ws_manager.connected

    def _server_request(self, *args, **kwargs):
        return self.request_queue.make_request(*args, **kwargs)

    def _send_message(self, id_msg, method, **params):
        self.ws_manager.send_json_message(id_msg, method, **params)

    def _handle_connection(self, ws_connected):
        logger.info('[CONNECTION] Status: %s', ws_connected)       
        
        # Report to client user
        if self.connection_handler:
            self.connection_handler(ws_connected)

    def _handle_result(self, id_msg, result):
        self.request_queue.result_handler(id_msg, result)

    def _handle_error(self, id_msg, error):
        if self.error_handler:
            self.error_handler(error)
        else:
            # TODO: Deal Error Messages from Server(raise errors or something)
            pass

    def _handle_event(self, event, event_data):
        if self.event_handler:
            self.event_handler(event, **event_data)
    

class MopidyClient(SimpleClient):

    listener = None

    def __init__(self, 
                 event_handler=None, 
                 version='2.0',
                 **kwargs):

        # If no event_handler is selected start an internal one
        if event_handler is None:
            self.listener = MopidyListener()
            event_handler = self.listener.on_event

        # Init client
        super(MopidyClient, self).__init__(event_handler=event_handler, **kwargs)

        # Select Mopidy API version methods
        if not version:
            version = self.core.get_version(timeout=5)

        assert version is not None, 'Could not get Mopidy API version from server'
        assert LooseVersion(version) >= LooseVersion('1.1'), 'Mopidy API version %s is not supported' % version

        if LooseVersion(version) >= LooseVersion('2.0'):
            import methods_2_0 as methods
        elif LooseVersion(version) >= LooseVersion('1.1'):
            import methods_1_1 as methods

        logger.info('Connected to Mopidy Server, API version: %s', version)

        # Load mopidy JSON/RPC methods
        self.playback = methods.PlaybackController(self._server_request)
        self.mixer = methods.MixerController(self._server_request)
        self.tracklist = methods.TracklistController(self._server_request)
        self.playlists = methods.PlaylistsController(self._server_request)
        self.library = methods.LibraryController(self._server_request)
        self.history = methods.HistoryController(self._server_request)

