import logging

from .mopidy_api import CoreController
import controllers_1_1_2 as controllers
from .ws_manager import MopidyWSManager
from .request_manager import RequestQueue
from .common import * 
               
logging.basicConfig()                    
               
               
class MopidyWSSimpleClient (object):
    
    def __init__ (self, 
                        ws_endpoint = 'ws://localhost:6680/mopidy/ws',
                        event_handler = None
                        ):
            
        self.event_handler = event_handler                 
        
        self.ws_manager = MopidyWSManager ( ws_url=ws_endpoint,
                                            on_msg_event = self._handle_event,
                                            on_msg_result = self._handle_result,
                                            on_msg_error = self._handle_error
                                            )                 
                                            
        self.request_queue = RequestQueue (send_function = self.ws_manager.send_message)

        #Core controller
        self.core = CoreController(self.request_queue.make_request)
        
    def _handle_result (self, id_msg, result):                
        self.request_queue.result_handler(id_msg, result)                
                       
    def _handle_error (self, id_msg, error): 
        #TODO: Deal Error Messages from Server (raise errors or something)
        print_nice ('[MSG_ERROR] ', error, format='error')
        self.request_queue.result_handler(id_msg, None)                               
            
    def _handle_event (self, event, event_data):        
        if self.event_handler:
            self.event_handler (event, **event_data)   
        
    def close (self):
        self.ws_manager.close()   
        
               
class MopidyWSClient (MopidyWSSimpleClient):  
    
    def __init__ (self, **kwargs):                
        super (MopidyWSClient, self).__init__(**kwargs)
        
        #Load mopidy controllers, dependant on mopidy_api_<version>
        self.playback = controllers.PlaybackController(self.request_queue.make_request)        
        self.mixer = controllers.MixerController(self.request_queue.make_request)
        self.tracklist = controllers.TracklistController(self.request_queue.make_request)
        self.playlists = controllers.PlaylistsController(self.request_queue.make_request)
        self.library = controllers.LibraryController(self.request_queue.make_request)
        self.history = controllers.HistoryController(self.request_queue.make_request)
                              