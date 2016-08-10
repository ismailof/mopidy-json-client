from ..mopidy_api import MopidyWSController


class HistoryController (MopidyWSController):

    def get_length(self, **options):
        '''Get the number of tracks in the history.
        :returns: the history length
        :rtype: int
        '''
        return self.mopidy_request('core.history.get_length', **options)

    def get_history(self, **options):
        '''Get the track history.
        The timestamps are milliseconds since epoch.
        :returns: the track history
        :rtype: list of (timestamp, :class:`mopidy.models.Ref`) tuples
        '''
        return self.mopidy_request('core.history.get_history', **options)
