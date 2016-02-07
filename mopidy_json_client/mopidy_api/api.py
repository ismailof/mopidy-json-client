from mopidy.core import CoreListener
       
class MopidyWSListener (CoreListener):
    ''' Subclass of ::class::mopidt.core.CoreListener class in mopidy.        
                
        ::meth::CoreListener::on_event gracefully dispatch events to client functions, 
        while maintaining compatibility to mopidy core.
        
        Subclass MAY implement the functions described in CoreListener API 
        (http://mopidy.readthedocs.org/en/latest/api/core/#core-events)
        to handle he desired events
    '''        
    pass
       
       
class MopidyWSController (object):
    ''' Base class of the controller wrapper classes
        It implements the function mopidy_request, which will be called by subclasses methods
    '''
    def __init__(self, request_handler):
        self._request_handler_ = request_handler       
    
    def mopidy_request(self, method, **kwargs):         
        return self._request_handler_(method, **kwargs)                
        
        
class TestController (MopidyWSController):
    def get_api (self, **options):
        return self.mopidy_request('core.describe', **options)                      
    
    def get_version (self, **options):
        return self.mopidy_request('core.get_version', **options)                      
    
    def send_method (self, method, **params):
        return self.mopidy_request(method, **params)                      