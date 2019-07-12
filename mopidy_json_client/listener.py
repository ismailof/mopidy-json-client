import logging
from .mopidy_api import MopidyAPI

logger = logging.getLogger(__name__)


class MopidyListener(object):
    '''
        Adds suport for binding callback functions to events using:
        ::meth::bind('<event_name>', <callback_function>)
        Allowed events are listed in
        https://docs.mopidy.com/en/latest/api/core/#mopidy.core.CoreListener
    '''

    def __init__(self, *args, **kwargs):
        self.bindings = {}

    def on_event(self, event, **event_data):
        # Log event
        args_text = ['%s=%r' % (arg, value)
                 for arg, value in event_data.items()]
        logger.debug('[EVENT] %s (%s)' % (event, ', '.join(args_text)))

        # Call registered events
        if event in self.bindings:
            for _callback_ in self.bindings[event]:
                # logger.debug("Event '%s' triggered callback <%s>" % (event, _callback_.__name__))
                _callback_(**event_data)

    def bind(self, event, callback):
        assert event in MopidyAPI.eventlist, 'Event {} does not exist'.format(event)
        if event not in self.bindings:
            self.bindings[event] = []
        # logger.debug("Bind callback <%s> to event '%s'" % (callback.__name__, event))
        if callback not in self.bindings[event]:
            self.bindings[event].append(callback)

    def unbind(self, event, callback):
        if event not in self.bindings:
            # logger.debug("No current bindings for event '%s'" % event)
            return
        for index, cb in enumerate(self.bindings[event]):
            if cb == callback:
                # logger.debug("Unbind callback <%s> from event '%s'" % (callback.__name__, event))
                self.bindings[event].pop(index)
                return

    def clear(self):
        # logger.debug("%: Clearing all event bindings" % self)
        self.bindings = {}
