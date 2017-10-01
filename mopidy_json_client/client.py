import time
import threading
import logging

import websocket

from . import __version__ as client_version
from .mopidy_api import MopidyAPI, CoreController
from .messages import RequestMessage, ResponseMessage
from .listener import MopidyListener


logger = logging.getLogger('mopidy_json_client')


class SimpleClient(object):

    def __init__(self,
                 ws_url='ws://localhost:6680/mopidy/ws',
                 event_handler=None,
                 error_handler=None,
                 connection_handler=None,
                 autoconnect=True,
                 retry_max=None,
                 retry_secs=10,
                 debug=False,
                 ):

        self.request_queue = []

        self._connected = False
        self.wsa = None
        self.wsa_thread = None

        # Set the debug level
        self.debug_client(debug)

        # Set event and error handlers
        self.event_handler = event_handler
        self.error_handler = error_handler
        self.connection_handler = connection_handler

        ResponseMessage.set_handlers(
            on_msg_event=self._dispatch_event,
            on_msg_result=self._dispatch_result,
            on_msg_error=self._dispatch_error)

        # Core controller
        self.core = CoreController(self._server_request)

        # Connection to Mopidy Websocket Server
        self.conn_lock = threading.Condition()
        self.ws_url = ws_url
        self.retry_max = retry_max
        self.retry_secs = retry_secs

        if autoconnect:
            self.connect(wait_secs=5)

    def debug_client(self, debug_value=True):
        logger.setLevel(
            logging.DEBUG if debug_value else logging.INFO)

    # Connection public functions

    def connect(self, ws_url=None, wait_secs=0):
        if self.is_connected():
            logger.warning(
                '[CONNECTION] Already connected to Mopidy Server at %s',
                self.ws_url)
            return True

        if ws_url:
            self.ws_url = ws_url

        # Set reconnection attemp
        self.retry_attemp = 0

        # Do connection attemp
        logger.info('[CONNECTION] Connecting to Mopidy Server at %s',
                     self.ws_url)
        self._ws_connect()

        # Return immediately if not waiting required
        if not wait_secs:
            return None

        # Wait for the WSA Thread to attemp the connection
        with self.conn_lock:
            self.conn_lock.wait(wait_secs)

        return self.is_connected()

    def disconnect(self):
        # Stop attemps to reconnect
        self.retry_attemp = None

        if not self.is_connected():
            logger.info('[CONNECTION] Already disconnected from Mopidy Server')
            return

        self.wsa.close()

    def is_connected(self):
        with self.conn_lock:
            return self._connected

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

    def _ws_retry(self):
        if self.retry_attemp is None:
            return

        if self.retry_max is None:
            # Infinite attemps
            time.sleep(self.retry_secs)
            logger.debug('[CONNECTION] Reconnecting to Mopidy Server')
            self._ws_connect()

        elif self.retry_attemp < self.retry_max:
            # Limited attemps
            time.sleep(self.retry_secs)
            self.retry_attemp += 1
            logger.debug(
                '[CONNECTION] Reconnecting to Mopidy Server. Attemp %d/%d',
                self.retry_attemp,
                self.retry_max)
            self._ws_connect()

        else:
            # TODO: Exception Max Retries unsuccessfull
            logger.warning(
                '[CONNECTION] Reached maximum of attemps to reconnect (%d)',
                self.retry_max)

    def _ws_error(self, *args, **kwargs):
        pass

    def _ws_open(self, *args, **kwargs):
        logger.info(
            '[CONNECTION] Mopidy Server is connected at %s',
            self.ws_url)
        self._update_status(connected=True)

    def _ws_close(self, *args, **kwargs):
        if self.is_connected():
            logger.info('[CONNECTION] Mopidy Server is disconnected')
            self._update_status(connected=False)
        else:
            logger.debug('[CONNECTION] Connection attemp to Mopidy Server failed')

        self._ws_retry()

    def _update_status(self, connected):
        with self.conn_lock:
            self._connected = connected
            if self.retry_attemp is not None:
                self.retry_attemp = 0
            self.conn_lock.notify()

        self._dispatch_connection(self.is_connected())

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

    def _dispatch_connection(self, conn_status):
        # Report connection
        if self.connection_handler:
            threading.Thread(
                target=self.connection_handler,
                args=(conn_status, ),
            ).start()

    def _dispatch_result(self, id_msg, result):
        for request in self.request_queue:
            if request.id_msg == id_msg:
                request.callback(result)
                self.request_queue.remove(request)
                return
        logger.warning('[RESPONSE] Recieved message id (%d) does not match any request', id_msg)

    def _dispatch_error(self, id_msg, error):
        if self.error_handler:
            self.error_handler(error)
        else:
            # TODO: Deal Error Messages from Server(raise errors or something)
            pass

    def _dispatch_event(self, event, event_data):
        if self.event_handler:
            self.event_handler(event, **event_data)


class MopidyClient(SimpleClient):

    def __init__(self, version='2.0', **kwargs):

        # Init client
        super(MopidyClient, self).__init__( **kwargs)

        # Select Mopidy API version methods
        if not version:
            version = self.core.get_version(timeout=5)
        if version is None:
            logger.warning('Could not get Mopidy API version from server')

        MopidyAPI.set_version(version)

        if not self.event_handler:
            self.listener = MopidyListener()
            self.event_handler = self.listener.on_event

        # Load mopidy JSON/RPC methods
        self.playback = MopidyAPI.controllers.PlaybackController(self._server_request)
        self.mixer = MopidyAPI.controllers.MixerController(self._server_request)
        self.tracklist = MopidyAPI.controllers.TracklistController(self._server_request)
        self.playlists = MopidyAPI.controllers.PlaylistsController(self._server_request)
        self.library = MopidyAPI.controllers.LibraryController(self._server_request)
        self.history = MopidyAPI.controllers.HistoryController(self._server_request)

    def bind_event(self, event, callback):
        logger.debug('[LISTENER] Binding %s to event %s', callback, event)
        self.listener.bind(event, callback)

    def get_client_version(self):
        return client_version

