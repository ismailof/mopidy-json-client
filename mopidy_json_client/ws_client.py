import logging
from distutils.version import LooseVersion

from .mopidy_api import CoreController
from .ws_manager import MopidyWSManager
from .listener import MopidyListener
from .request_manager import RequestQueue


logger = logging.getLogger(__name__)


class SimpleClient(object):

    def __init__(self,
                 server_addr='localhost:6680',
                 event_handler=None,
                 error_handler=None,
                 ):

        # Event and error handlers
        self.event_handler = event_handler
        self.error_handler = error_handler

        # Connection to Mopidy Websocket Server
        ws_url = 'ws://' + server_addr + '/mopidy/ws'
        self.ws_manager = MopidyWSManager(on_msg_event=self._handle_event,
                                          on_msg_result=self._handle_result,
                                          on_msg_error=self._handle_error)

        self.ws_manager.connect_ws(url=ws_url)

        # Request Queue
        self.request_queue = RequestQueue(send_function=self.ws_manager.send_message)

        # Core controller
        self.core = CoreController(self.request_queue.make_request)

    def _handle_result(self, id_msg, result):
        self.request_queue.result_handler(id_msg, result)

    def _handle_error(self, id_msg, error):
        self.request_queue.result_handler(id_msg, None)
        if self.error_handler:
            self.error_handler(error)
        else:
            # TODO: Deal Error Messages from Server(raise errors or something)
            pass

    def _handle_event(self, event, event_data):
        if self.event_handler:
            self.event_handler(event, **event_data)

    def close(self):
        self.ws_manager.close()


class MopidyClient(SimpleClient):

    listener = None

    def __init__(self, event_handler=None, **kwargs):

        # If no event_handler is selected start an internal one
        if event_handler is None:
            self.listener = MopidyListener()
            event_handler = self.listener.on_event

        # Init client
        super(MopidyClient, self).__init__(event_handler=event_handler, **kwargs)

        # Select Mopidy API version methods
        version = self.core.get_version(timeout=20)

        assert version is not None, 'Could not get Mopidy API version from server'
        assert LooseVersion(version) >= LooseVersion('1.1'), 'Mopidy API version %s is not supported' % version

        if LooseVersion(version) >= LooseVersion('2.0'):
            import methods_2_0 as methods
        elif LooseVersion(version) >= LooseVersion('1.1'):
            import methods_1_1 as methods

        logger.info('Connected to Mopidy Server, API version: %s', version)

        # Load mopidy JSON/RPC methods
        self.playback = methods.PlaybackController(self.request_queue.make_request)
        self.mixer = methods.MixerController(self.request_queue.make_request)
        self.tracklist = methods.TracklistController(self.request_queue.make_request)
        self.playlists = methods.PlaylistsController(self.request_queue.make_request)
        self.library = methods.LibraryController(self.request_queue.make_request)
        self.history = methods.HistoryController(self.request_queue.make_request)
