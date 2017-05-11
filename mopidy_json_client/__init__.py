import logging

from .client import MopidyClient, SimpleClient
from .listener import MopidyListener, SimpleListener


__author__ = 'Ismael Asensio (ismailof@github.com)'
__version__ = '0.5.14'

__all__ = [
    'MopidyClient',
    'SimpleClient',
    'MopidyListener',
    'SimpleListener'
]


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
