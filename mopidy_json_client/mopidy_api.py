import logging

logger = logging.getLogger(__name__)


class MopidyWSController(object):
    ''' Base class of the controller wrapper classes
        It implements the function mopidy_request, which will be called by subclasses methods
    '''
    def __init__(self, request_handler):
        self._request_handler_ = request_handler

    def mopidy_request(self, method, **kwargs):
        args_text = ['%s=%r' % (arg, value)
                     for arg, value in kwargs.iteritems()]
        logger.debug('[REQUEST] %s (%s)' % (method, ', '.join(args_text)))
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
