import logging
from mopidy.core import CoreListener

logger = logging.getLogger(__name__)


# TODO: List also the parameters returned within the events
def list_mopidy_events():
    ''' Helper class to list all the events that CoreListener can receive '''
    exclude_methods = ['__class__',   # python object methods
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
                       'send',   # send method, not an event
                       'on_event',  # event dispatcher
                       ]
    events = dir(CoreListener)
    for item in exclude_methods:
        if item in events:
            events.remove(item)
    return events


class SimpleListener(CoreListener):
    ''' Subclass of ::class::mopidt.core.CoreListener class in mopidy.

        ::meth::CoreListener::on_event gracefully dispatch events to client functions,
        while maintaining compatibility to mopidy core.

        Subclass MAY implement the functions described in CoreListener API
        (http://mopidy.readthedocs.org/en/latest/api/core/core-events)
        to handle he desired events
    '''

    # Called when an event is produced
    def on_event(self, event, **event_data):
        # Log event
        args_text = ['%s=%r' % (arg, value)
                     for arg, value in event_data.iteritems()]
        logger.debug('[EVENT] %s (%s)' % (event, ', '.join(args_text)))
        # Call overriden function attached to the event
        super(SimpleListener, self).on_event(event, **event_data)


class MopidyListener(SimpleListener):
    '''
        Adds suport for binding callback functions to events using:
        ::meth::bind('<event_name>', <callback_function>)
    '''
    bindings = {}
    allowed_events = list_mopidy_events()

    def on_event(self, event, **event_data):
        super(MopidyListener, self).on_event(event, **event_data)
        # Call registered events
        if event in self.bindings:
            for _callback_ in self.bindings[event]:
                # logger.debug("Event '%s' triggered callback <%s>" % (event, _callback_.__name__))
                _callback_(**event_data)

    def bind(self, event, callback):
        assert event in self.allowed_events, 'Event {} does not exist'.format(event)
        if event not in self.bindings:
            self.bindings[event] = []
        # logger.debug("Bind callback <%s> to event '%s'" % (callback.__name__, event))
        self.bindings[event].append(callback)

    def unbind(self, event, callback):
        if event not in self.bindings:
            # logger.debug("No current bindings for event '%s'" % event)
            return
        for index, cb in enumerate(self.bindings[event]):
            if cb == callback:
                # logger.debug("Unbind callback <%s> from event '%s'" % (callback.__name__, event))
                self.bindings[event].pop(index)
