__author__ = 'Ismael Asensio (ismailof@github.com)'
__version__ = '0.5.0'

__all__ = [
    'MopidyClient',
    'SimpleClient',
    'MopidyListener',
    'SimpleListener'
]

import logging
from .client import MopidyClient, SimpleClient
from .listener import MopidyListener, SimpleListener

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
