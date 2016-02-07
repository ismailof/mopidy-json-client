import logging

import mopidy_api
from ws_manager import MopidyWSManager
from request_manager import RequestQueue
from common import * 
               
logging.basicConfig()                    
               
class MopidyWSClient (object):
    
    def __init__ (self, event_handler = None):
            
        self.event_handler = event_handler                 
        
        self.ws_manager = MopidyWSManager ( 'ws://localhost:6680/mopidy/ws',
                                            on_msg_event = self._handle_event,
                                            on_msg_result = self._handle_result,
                                            on_msg_error = self._handle_error
                                            )                 
                                            
        self.request_queue = RequestQueue (send_function = self.ws_manager.send_message)

        self.playback = mopidy_api.PlaybackController(self.request_queue.make_request)        
        self.mixer = mopidy_api.MixerController(self.request_queue.make_request)
        self.tracklist = mopidy_api.TracklistController(self.request_queue.make_request)
        #self.playlist = mopidy_api.PlaylistController(self.request_queue.make_request)
        self.library = mopidy_api.LibraryController(self.request_queue.make_request)
        self.history = mopidy_api.HistoryController(self.request_queue.make_request)
        
        self.test = mopidy_api.TestController(self.request_queue.make_request)
        
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
        