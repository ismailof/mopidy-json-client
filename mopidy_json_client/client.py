import time
import threading
import logging
from distutils.version import LooseVersion

import websocket

from .messages import RequestMessage, ResponseMessage
from .mopidy_api import CoreController
from .listener import MopidyListener


logger = logging.getLogger(__name__)


class SimpleClient(object):

    request_queue = []

    connected = False
    wsa = None
    wsa_thread = None

    def __init__(self,
                 server_addr='localhost:6680',
                 event_handler=None,
                 error_handler=None,
                 connection_handler=None,
                 autoconnect=True,
                 reconnect_max=-1,
                 reconnect_secs=10
                 ):

        # Event and error handlers
        self.event_handler = event_handler
        self.error_handler = error_handler
        self.connection_handler = connection_handler

        # Init WebSocketApp items
        self.conn_lock = threading.Condition()
        self.reconnect_max = reconnect_max
        self.reconnect_secs = reconnect_secs
        self.reconnect_try = 0 if reconnect_max else None

        ResponseMessage.set_handlers(on_msg_event=self._handle_event,
                                     on_msg_result=self._handle_result,
                                     on_msg_error=self._handle_error)

        # Connection to Mopidy Websocket Server
        ws_url = 'ws://' + server_addr + '/mopidy/ws'
        self.ws_url = ws_url

        if autoconnect:
            self.connect(wait_secs=5)

        # Core controller
        self.core = CoreController(self._server_request)

    # Connection public functions

    def connect(self, url=None, wait_secs=0):
        if self.is_connected():
            logger.warning('WebSocket is already connected to %s',
                           self.ws_url)
            return True

        if url:
            self.ws_url = url

        # Set reconnection attemp
        self.reconnect_try = 0 if self.reconnect_max else None

        # Do connection attemp
        self._ws_connect()

        # Return immediately if not waiting required
        if not wait_secs:
            return None

        # Wait for the WSA Thread to attemp the connection
        with self.conn_lock:
            self.conn_lock.wait(wait_secs)

        return self.is_connected()

    def disconnect(self):
        self.reconnect_try = None
        if not self.is_connected():
            logger.warning('WebSocket is already disconnected')

        self.wsa.close()

    def is_connected(self):
        with self.conn_lock:
            return self.connected

    # Connection internal functions

    def _ws_connect(self):
        # Initialize websocket parameters
        self.wsa = websocket.WebSocketApp(
            url=self.ws_url,
            on_message=self._server_response,
            on_error=self._ws_error,
            on_open=self._ws_open,
            on_close=self._ws_close)

        # Run the websocket in parallel thread
        self.wsa_thread = threading.Thread(
            target=self.wsa.run_forever,
            name='WSA-Thread')
        self.wsa_thread.setDaemon(True)
        self.wsa_thread.start()

    def _ws_reconnect(self):

        if self.reconnect_max < 0:
            # Infinite attemps
            time.sleep(self.reconnect_secs)
            logger.debug('[CONNECTION] Reconnecting to sever',
                         self.reconnect_secs)
            self._ws_connect()
            return

        if self.reconnect_try < self.reconnect_max:
            # Limited attemps
            time.sleep(self.reconnect_secs)
            self.reconnect_try += 1
            logger.debug('[CONNECTION] Reconnecting to sever. Attemp %d/%d',
                         self.reconnect_try,
                         self.reconnect_max)
            self._ws_connect()
        else:
            # TODO: Exception Max Retries unsuccessfull
            logger.warning('[CONNECTION] Reached maximum of attemps to reconnect (%d)',
                           self.reconnect_max)
            pass

    def _ws_error(self, *args, **kwargs):
        pass

    def _ws_open(self, *args, **kwargs):
        logger.debug('[CONNECTION] WebSocket is connected to %s',
                     self.ws_url)
        self._connection_changed(connected=True)

    def _ws_close(self, *args, **kwargs):
        if self.is_connected():
            logger.info('[CONNECTION] Server has disconnected')
            self._connection_changed(connected=False)

        if self.reconnect_try is not None:
            self._ws_reconnect()

    def _connection_changed(self, connected):
        with self.conn_lock:
            self.connected = connected
            self.conn_lock.notify()

        if self.connection_handler:
            threading.Thread(
                target=self.connection_handler,
                args=(self.connected, ),
            ).start()

    # Websocket request and response

    def _server_request(self, method, **kwargs):

        request = RequestMessage(method, **kwargs)
        self.request_queue.append(request)

        try:
            self.wsa.send(request.json_message)
            server_result = request.wait_for_result()
        except Exception as ex:
            logger.exception(ex)
            return None

        return server_result

    def _server_response(self, ws, message):
        try:
            ResponseMessage.parse_json_message(message)
        except Exception as ex:
            logger.exception(ex)

    # Higher level handlers

    def _handle_connection(self, ws_connected):
        logger.info('[CONNECTION] Status: %s', ws_connected)

        # Report to client user
        if self.connection_handler:
            self.connection_handler(ws_connected)

    def _handle_result(self, id_msg, result):
        for request in self.request_queue:
            if request.id_msg == id_msg:
                request.callback(result)
                self.request_queue.remove(request)
                return
        logger.warning('Recieved message (id %d) does not match any request', id_msg)

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
