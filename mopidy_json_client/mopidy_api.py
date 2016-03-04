import logging 
from mopidy.core import CoreListener

log = logging.getLogger(__name__)

class MopidyWSListener(CoreListener):
    ''' Subclass of ::class::mopidt.core.CoreListener class in mopidy.

        ::meth::CoreListener::on_event gracefully dispatch events to client functions,
        while maintaining compatibility to mopidy core.

        Subclass MAY implement the functions described in CoreListener API
        (http://mopidy.readthedocs.org/en/latest/api/core/core-events)
        to handle he desired events
    '''
   
    # Used to log the events received by the client
    def on_event(self, event, **data):        
        args_text = ['%s=%r' % (arg, type(value)) for arg, value in data.iteritems()]
        log.debug('[EVENT] %s (%s)' % (event, ', '.join(args_text)))      
        super(MopidyWSListener, self).on_event(event, **data)
    
    # TODO: List also the parameters returned within the events
    def list_events(self):
        ''' Helper class to list all the events the Listener can receive '''
        exclude_methods = ['__class__', # python object methods
                           '__delattr__', 
                           '__dict__', 
                           '__doc__', 
                           '__format__', 
                           '__getattribute__', 
                           '__hash__', 
                           '__init__', 
                           '__module__', 
                           '__new__', 
                           '__reduce__', 
                           '__reduce_ex__', 
                           '__repr__', 
                           '__setattr__', 
                           '__sizeof__', 
                           '__str__', 
                           '__subclasshook__', 
                           '__weakref__',
                           'send',  # send method, not an event
                           'on_event', # event dispatcher
                           ]
        events = dir(MopidyWSListener)
        for item in exclude_methods:
            if item in events:
                events.remove(item)    
        return events


class MopidyWSController(object):
    ''' Base class of the controller wrapper classes
        It implements the function mopidy_request, which will be called by subclasses methods
    '''
    def __init__(self, request_handler):
        self._request_handler_ = request_handler

    def mopidy_request(self, method, **kwargs):
        return self._request_handler_(method, **kwargs)


class CoreController(MopidyWSController):
    ''' Implements ::method::describe and ::method::get_version of Mopidy Core
        It also provides ::method::send which can be used for testing
    '''
    def describe(self, **options):
        return self.mopidy_request('core.describe', **options)

    def get_version(self, **options):
        return self.mopidy_request('core.get_version', **options)

    def send(self, method, **params):
        return self.mopidy_request('core.' + method, **params)
