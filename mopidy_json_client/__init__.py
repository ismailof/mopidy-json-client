import logging
from .ws_client import MopidyClient, SimpleClient
from .listener import MopidyListener, SimpleListener

__version__ = '0.4.10'

__all__ = [
    'MopidyClient',
    'SimpleClient',
    'MopidyListener',
    'SimpleListener'
]

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
