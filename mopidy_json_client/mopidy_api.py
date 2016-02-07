from mopidy.core import CoreListener
from common import *
       
class MopidyWSListener (CoreListener):
    '''
        Subclass of ::class::mopidt.core.CoreListener class in mopidy.        
                
        ::meth::CoreListener::on_event gracefully dispatch events to client functions, 
        while maintaining compatibility to mopidy core.
        
        Subclass MAY implement the functions described in CoreListener API 
        (http://mopidy.readthedocs.org/en/latest/api/core/#core-events)
        to handle he desired events
    '''        
       
class MopidyWSController (object):
    def __init__(self, request_handler):
        self._request_handler_ = request_handler       
    
    def mopidy_request(self, method, **kwargs):         
        return self._request_handler_(method, **kwargs)        
        
        
class PlaybackController (MopidyWSController):               
    def play(self):
        self.mopidy_request('core.playback.play')
           
    def pause(self):
        self.mopidy_request('core.playback.pause')   
           
    def stop(self):
        self.mopidy_request('core.playback.stop') 
                   
    def resume(self):
        self.mopidy_request('core.playback.resume') 
           
    def next(self):
        self.mopidy_request('core.playback.next') 
                   
    def previous(self):
        self.mopidy_request('core.playback.previous') 
    
    def get_current_track(self, **options):
        return self.mopidy_request('core.playback.get_current_track', **options)           

    def seek(self, time_position, **options):
        return self.mopidy_request('core.playback.seek', time_position=time_position, **options)           
    
    def get_current_tl_track(self, **options):
        return self.mopidy_request('core.playback.get_current_tl_track', **options)           
    
    def get_stream_title(self, **options):
        return self.mopidy_request('core.playback.get_stream_title', **options)           
    
    def get_time_position(self, **options):
        return self.mopidy_request('core.playback.get_time_position', **options)           
    
    def get_state(self, **options):
        return self.mopidy_request('core.playback.get_state', **options)           

    def set_state(self, new_state, **options):
        return self.mopidy_request('core.playback.set_state', new_state=new_state, **options)           
    
 
class MixerController (MopidyWSController):
    def set_volume(self, volume, **options):        
        return self.mopidy_request('core.mixer.set_volume', volume=volume, **options)      
           
    def get_volume(self, **options):
        return self.mopidy_request('core.mixer.get_volume', **options)              

    def set_mute(self, mute, **options):        
        return self.mopidy_request('core.mixer.set_mute', mute=mute, **options)      
           
    def get_mute(self, **options):
        return self.mopidy_request('core.mixer.get_mute', **options)              

        
class LibraryController (MopidyWSController):      
    def browse(self, uri, **options):
        return self.mopidy_request('core.library.browse', uri=uri, **options)                      

    def lookup(self, uris, **options):  
        return self.mopidy_request('core.library.lookup', uris=uris, **options)  
       
    def get_images(self, uris, **options):
        return self.mopidy_request('core.library.get_images', uris=uris, **options)                      

    def search(self, query=None, uris=None, exact=False, **options):
        return self.mopidy_request('core.library.search', query=query, uris=uris, exact=exact, **options)                      
        
    def refresh(self, uri=None):
        return self.mopidy_request('core.library.refresh', uri=uri)   
        
    def get_distinct(field, query=None, **options):
        return self.mopidy_request('core.library.get_distinct', field=field, query=query, **options)           
    

class TracklistController (MopidyWSController):
    #Manipulating
    def add(self, uris=None, at_position=None, **options):        
        return self.mopidy_request('core.tracklist.add', at_position=at_position, uris=uris, **options)

    def clear(self, **options):  
        return self.mopidy_request('core.tracklist.clear', **options) 

    def filter(self, criteria=None, **options):
        return self.mopidy_request('core.tracklist.filter', criteria=criteria, **options) 

    def move(self, start, end, to_position, **options):
        return self.mopidy_request('core.tracklist.move', start=start, end=end, to_position=to_position, **options) 
        
    def remove(self, criteria=None, **options):
        return self.mopidy_request('core.tracklist.remove', criteria=criteria, **options) 
        
    def shuffle(self, start=None, end=None, **options):
        return self.mopidy_request('core.tracklist.shuffle', start=start, end=end, **options) 
        
    def slice(self, start, end, **options):
        return self.mopidy_request('core.tracklist.slice', start=start, end=end, **options) 
    
    #Tracklist options
    def get_consume(self, **options):
        return self.mopidy_request('core.mixer.get_consume', **options) 
        
    def get_random(self, **options):
        return self.mopidy_request('core.mixer.get_random', **options) 
        
    def get_repeat(self, **options):
        return self.mopidy_request('core.mixer.get_repeat', **options) 
        
    def get_single(self, **options):
        return self.mopidy_request('core.mixer.get_single', **options) 
    
    def set_consume(self, value, **options):
        return self.mopidy_request('core.mixer.set_consume', value=value, **options) 
        
    def set_random(self, value, **options):
        return self.mopidy_request('core.mixer.set_random', value=value, **options) 
        
    def set_repeat(self, value, **options):
        return self.mopidy_request('core.mixer.set_repeat', value=value, **options) 
        
    def set_single(self, value, **options):
        return self.mopidy_request('core.mixer.set_single', value=value, **options) 
        
    
    #Current State
    def index(self, tl_track=None, tlid=None, **options):
        return self.mopidy_request('core.tracklist.index', tl_track=tl_track, tlid=tlid, **options) 
  
    def get_tl_tracks(self, **options):
        return self.mopidy_request('core.tracklist.get_tl_tracks', **options) 
        
    def get_tracks(self, **options):
        return self.mopidy_request('core.tracklist.get_tracks', **options) 
        
    def get_length(self, **options):
        return self.mopidy_request('core.tracklist.get_length', **options) 

    def get_version(self, **options):
        return self.mopidy_request('core.tracklist.get_version', **options) 

    #Future State
    def get_eot_tlid(self, **options):
        return self.mopidy_request('core.tracklist.get_eot_tlid', **options)
        
    def get_next_tlid(self, **options):
        return self.mopidy_request('core.tracklist.get_next_tlid', **options)
    
    def get_previous_tlid(self, **options):
        return self.mopidy_request('core.tracklist.get_previous_tlid', **options)
       
    def eot_track(self, tl_track=None, **options):
        return self.mopidy_request('core.tracklist.eot_track', tl_track=tl_track, **options) 
    
    def next_track(self, tl_track=None, **options):
        return self.mopidy_request('core.tracklist.next_track', tl_track=tl_track, **options)         
        
    def previous_track(self, tl_track=None, **options):
        return self.mopidy_request('core.tracklist.previous_track', tl_track=tl_track, **options)
        
        
class HistoryController (MopidyWSController):   
    def get_history(self, **options):
        return self.mopidy_request('core.history.get_history', **options)                      
    
    def get_length(self, **options):
        return self.mopidy_request('core.history.get_length', **options)                      
        
        
class TestController (MopidyWSController):
    def get_api (self, **options):
        return self.mopidy_request('core.describe', **options)                      
    
    def get_version (self, **options):
        return self.mopidy_request('core.get_version', **options)                      
    
    def send_method (self, method, **params):
        return self.mopidy_request(method, **params)                      