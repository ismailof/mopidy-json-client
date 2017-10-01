import logging

__author__ = 'Ismael Asensio (ismailof@github.com)'
__version__ = '0.6.0'

from .client import MopidyClient, SimpleClient

__all__ = [
    'MopidyClient',
    'SimpleClient',
]


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
