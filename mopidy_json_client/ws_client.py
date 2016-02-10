import logging

from .mopidy_api import CoreController
import methods_1_1_2 as methods
from .ws_manager import MopidyWSManager
from .request_manager import RequestQueue

logging.basicConfig()


class MopidyWSSimpleClient(object):

    def __init__(self,
                 ws_endpoint='ws://localhost:6680/mopidy/ws',
                 event_handler=None,
                 error_handler=None,
                 ):

        self.event_handler = event_handler
        self.error_handler = error_handler

        self.ws_manager = MopidyWSManager(ws_url=ws_endpoint,
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


class MopidyWSClient(MopidyWSSimpleClient):

    def __init__(self, **kwargs):
        super(MopidyWSClient, self).__init__(**kwargs)

        # Load mopidy JSON/RPC methods
        self.playback = methods.PlaybackController(self.request_queue.make_request)
        self.mixer = methods.MixerController(self.request_queue.make_request)
        self.tracklist = methods.TracklistController(self.request_queue.make_request)
        self.playlists = methods.PlaylistsController(self.request_queue.make_request)
        self.library = methods.LibraryController(self.request_queue.make_request)
        self.history = methods.HistoryController(self.request_queue.make_request)
