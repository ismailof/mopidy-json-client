import logging
from distutils.version import StrictVersion

from .mopidy_api import CoreController
from .ws_manager import MopidyWSManager
from .request_manager import RequestQueue

logging.basicConfig()


class SimpleClient(object):

    def __init__(self,
                 websocket_url='ws://localhost:6680/mopidy/ws',
                 event_handler=None,
                 error_handler=None,
                 ):

        self.event_handler = event_handler
        self.error_handler = error_handler

        self.ws_manager = MopidyWSManager(ws_url=websocket_url,
                                          on_msg_event=self._handle_event,
                                          on_msg_result=self._handle_result,
                                          on_msg_error=self._handle_error)

        self.request_queue = RequestQueue(send_function=self.ws_manager.send_message)

        # Core controller
        self.core = CoreController(self.request_queue.make_request)

    def _handle_result(self, id_msg, result):
        self.request_queue.result_handler(id_msg, result)

    def _handle_error(self, id_msg, error):
        # TODO: Deal Error Messages from Server(raise errors or something)
        self.request_queue.result_handler(id_msg, None)
        if self.error_handler:
            self.error_handler(error)

    def _handle_event(self, event, event_data):
        if self.event_handler:
            self.event_handler(event, **event_data)

    def close(self):
        self.ws_manager.close()


class MopidyClient(SimpleClient):

    def __init__(self, version='1.1.2', **kwargs):
        super(MopidyClient, self).__init__(**kwargs)

        assert StrictVersion(version) >= '1.1', 'Version %s is not supported' % version

        if StrictVersion(version) >= '1.1':
            import methods_1_1 as methods
        elif StrictVersion(version) >= '2.0':
            import methods_2_0 as methods

        # Load mopidy JSON/RPC methods
        self.playback = methods.PlaybackController(self.request_queue.make_request)
        self.mixer = methods.MixerController(self.request_queue.make_request)
        self.tracklist = methods.TracklistController(self.request_queue.make_request)
        self.playlists = methods.PlaylistsController(self.request_queue.make_request)
        self.library = methods.LibraryController(self.request_queue.make_request)
        self.history = methods.HistoryController(self.request_queue.make_request)
