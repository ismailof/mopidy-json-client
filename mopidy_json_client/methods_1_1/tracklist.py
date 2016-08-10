from ..mopidy_api import MopidyWSController


class TracklistController (MopidyWSController):

    def index(self, tl_track=None, tlid=None, **options):
        '''The position of the given track in the tracklist.
        If neither *tl_track* or *tlid* is given we return the index of
        the currently playing track.
        :param tl_track: the track to find the index of
        :type tl_track: :class:`mopidy.models.TlTrack` or :class:`None`
        :param tlid: TLID of the track to find the index of
        :type tlid: :class:`int` or :class:`None`
        :rtype: :class:`int` or :class:`None`
        .. versionadded:: 1.1
            The *tlid* parameter
        '''
        return self.mopidy_request('core.tracklist.index', tl_track=tl_track, tlid=tlid, **options)

    def get_consume(self, **options):
        '''Get consume mode.
        :class:`True`
            Tracks are removed from the tracklist when they have been played.
        :class:`False`
            Tracks are not removed from the tracklist.
        '''
        return self.mopidy_request('core.tracklist.get_consume', **options)

    def shuffle(self, start=None, end=None, **options):
        '''Shuffles the entire tracklist. If ``start`` and ``end`` is given only
        shuffles the slice ``[start:end]``.
        Triggers the :meth:`mopidy.core.CoreListener.tracklist_changed` event.
        :param start: position of first track to shuffle
        :type start: int or :class:`None`
        :param end: position after last track to shuffle
        :type end: int or :class:`None`
        '''
        return self.mopidy_request('core.tracklist.shuffle', start=start, end=end, **options)

    def next_track(self, tl_track, **options):
        '''The track that will be played if calling
        :meth:`mopidy.core.PlaybackController.next()`.
        For normal playback this is the next track in the tracklist. If repeat
        is enabled the next track can loop around the tracklist. When random is
        enabled this should be a random track, all tracks should be played once
        before the tracklist repeats.
        :param tl_track: the reference track
        :type tl_track: :class:`mopidy.models.TlTrack` or :class:`None`
        :rtype: :class:`mopidy.models.TlTrack` or :class:`None`
        '''
        return self.mopidy_request('core.tracklist.next_track', tl_track=tl_track, **options)

    def get_random(self, **options):
        '''Get random mode.
        :class:`True`
            Tracks are selected at random from the tracklist.
        :class:`False`
            Tracks are played in the order of the tracklist.
        '''
        return self.mopidy_request('core.tracklist.get_random', **options)

    def get_next_tlid(self, **options):
        '''The tlid of the track that will be played if calling
        :meth:`mopidy.core.PlaybackController.next()`.
        For normal playback this is the next track in the tracklist. If repeat
        is enabled the next track can loop around the tracklist. When random is
        enabled this should be a random track, all tracks should be played once
        before the tracklist repeats.
        :rtype: :class:`int` or :class:`None`
        .. versionadded:: 1.1
        '''
        return self.mopidy_request('core.tracklist.get_next_tlid', **options)

    def previous_track(self, tl_track, **options):
        '''Returns the track that will be played if calling
        :meth:`mopidy.core.PlaybackController.previous()`.
        For normal playback this is the previous track in the tracklist. If
        random and/or consume is enabled it should return the current track
        instead.
        :param tl_track: the reference track
        :type tl_track: :class:`mopidy.models.TlTrack` or :class:`None`
        :rtype: :class:`mopidy.models.TlTrack` or :class:`None`
        '''
        return self.mopidy_request('core.tracklist.previous_track', tl_track=tl_track, **options)

    # DEPRECATED
    def add(self, tracks=None, at_position=None, uri=None, uris=None, **options):
        '''Add tracks to the tracklist.
        If ``uri`` is given instead of ``tracks``, the URI is looked up in the
        library and the resulting tracks are added to the tracklist.
        If ``uris`` is given instead of ``uri`` or ``tracks``, the URIs are
        looked up in the library and the resulting tracks are added to the
        tracklist.
        If ``at_position`` is given, the tracks are inserted at the given
        position in the tracklist. If ``at_position`` is not given, the tracks
        are appended to the end of the tracklist.
        Triggers the :meth:`mopidy.core.CoreListener.tracklist_changed` event.
        :param tracks: tracks to add
        :type tracks: list of :class:`mopidy.models.Track` or :class:`None`
        :param at_position: position in tracklist to add tracks
        :type at_position: int or :class:`None`
        :param uri: URI for tracks to add
        :type uri: string or :class:`None`
        :param uris: list of URIs for tracks to add
        :type uris: list of string or :class:`None`
        :rtype: list of :class:`mopidy.models.TlTrack`
        .. versionadded:: 1.0
            The ``uris`` argument.
        .. deprecated:: 1.0
            The ``tracks`` and ``uri`` arguments. Use ``uris``.
        '''
        return self.mopidy_request('core.tracklist.add', tracks=tracks, at_position=at_position, uri=uri, uris=uris, **options)

    def get_eot_tlid(self, **options):
        '''The TLID of the track that will be played after the current track.
        Not necessarily the same TLID as returned by :meth:`get_next_tlid`.
        :rtype: :class:`int` or :class:`None`
        .. versionadded:: 1.1
        '''
        return self.mopidy_request('core.tracklist.get_eot_tlid', **options)

    def set_random(self, value, **options):
        '''Set random mode.
        :class:`True`
            Tracks are selected at random from the tracklist.
        :class:`False`
            Tracks are played in the order of the tracklist.
        '''
        return self.mopidy_request('core.tracklist.set_random', value=value, **options)

    def get_tracks(self, **options):
        '''Get tracklist as list of :class:`mopidy.models.Track`.
        '''
        return self.mopidy_request('core.tracklist.get_tracks', **options)

    def set_single(self, value, **options):
        '''Set single mode.
        :class:`True`
            Playback is stopped after current song, unless in ``repeat`` mode.
        :class:`False`
            Playback continues after current song.
        '''
        return self.mopidy_request('core.tracklist.set_single', value=value, **options)

    def slice(self, start, end, **options):
        '''Returns a slice of the tracklist, limited by the given start and end
        positions.
        :param start: position of first track to include in slice
        :type start: int
        :param end: position after last track to include in slice
        :type end: int
        :rtype: :class:`mopidy.models.TlTrack`
        '''
        return self.mopidy_request('core.tracklist.slice', start=start, end=end, **options)

    # DEPRECATED
    def filter(self, criteria=None, **options):
        '''Filter the tracklist by the given criterias.
        A criteria consists of a model field to check and a list of values to
        compare it against. If the model field matches one of the values, it
        may be returned.
        Only tracks that matches all the given criterias are returned.
        Examples::
            # Returns tracks with TLIDs 1, 2, 3, or 4 (tracklist ID)
            filter({'tlid': [1, 2, 3, 4]})
            # Returns track with URIs 'xyz' or 'abc'
            filter({'uri': ['xyz', 'abc']})
            # Returns track with a matching TLIDs (1, 3 or 6) and a
            # matching URI ('xyz' or 'abc')
            filter({'tlid': [1, 3, 6], 'uri': ['xyz', 'abc']})
        :param criteria: on or more criteria to match by
        :type criteria: dict, of (string, list) pairs
        :rtype: list of :class:`mopidy.models.TlTrack`
        .. deprecated:: 1.1
            Providing the criteria via ``kwargs``.
        '''
        return self.mopidy_request('core.tracklist.filter', criteria=criteria, **options)

    def get_single(self, **options):
        '''Get single mode.
        :class:`True`
            Playback is stopped after current song, unless in ``repeat`` mode.
        :class:`False`
            Playback continues after current song.
        '''
        return self.mopidy_request('core.tracklist.get_single', **options)

    def set_consume(self, value, **options):
        '''Set consume mode.
        :class:`True`
            Tracks are removed from the tracklist when they have been played.
        :class:`False`
            Tracks are not removed from the tracklist.
        '''
        return self.mopidy_request('core.tracklist.set_consume', value=value, **options)

    def get_previous_tlid(self, **options):
        '''Returns the TLID of the track that will be played if calling
        :meth:`mopidy.core.PlaybackController.previous()`.
        For normal playback this is the previous track in the tracklist. If
        random and/or consume is enabled it should return the current track
        instead.
        :rtype: :class:`int` or :class:`None`
        .. versionadded:: 1.1
        '''
        return self.mopidy_request('core.tracklist.get_previous_tlid', **options)

    def get_length(self, **options):
        '''Get length of the tracklist.
        '''
        return self.mopidy_request('core.tracklist.get_length', **options)

    def get_repeat(self, **options):
        '''Get repeat mode.
        :class:`True`
            The tracklist is played repeatedly.
        :class:`False`
            The tracklist is played once.
        '''
        return self.mopidy_request('core.tracklist.get_repeat', **options)

    def get_version(self, **options):
        '''Get the tracklist version.
        Integer which is increased every time the tracklist is changed. Is not
        reset before Mopidy is restarted.
        '''
        return self.mopidy_request('core.tracklist.get_version', **options)

    def move(self, start, end, to_position, **options):
        '''Move the tracks in the slice ``[start:end]`` to ``to_position``.
        Triggers the :meth:`mopidy.core.CoreListener.tracklist_changed` event.
        :param start: position of first track to move
        :type start: int
        :param end: position after last track to move
        :type end: int
        :param to_position: new position for the tracks
        :type to_position: int
        '''
        return self.mopidy_request('core.tracklist.move', start=start, end=end, to_position=to_position, **options)

    def remove(self, criteria=None, **options):
        '''Remove the matching tracks from the tracklist.
        Uses :meth:`filter()` to lookup the tracks to remove.
        Triggers the :meth:`mopidy.core.CoreListener.tracklist_changed` event.
        :param criteria: on or more criteria to match by
        :type criteria: dict
        :rtype: list of :class:`mopidy.models.TlTrack` that was removed
        .. deprecated:: 1.1
            Providing the criteria  via ``kwargs``.
        '''
        return self.mopidy_request('core.tracklist.remove', criteria=criteria, **options)

    def get_tl_tracks(self, **options):
        '''Get tracklist as list of :class:`mopidy.models.TlTrack`.
        '''
        return self.mopidy_request('core.tracklist.get_tl_tracks', **options)

    def clear(self, **options):
        '''Clear the tracklist.
        Triggers the :meth:`mopidy.core.CoreListener.tracklist_changed` event.
        '''
        return self.mopidy_request('core.tracklist.clear', **options)

    def eot_track(self, tl_track, **options):
        '''The track that will be played after the given track.
        Not necessarily the same track as :meth:`next_track`.
        :param tl_track: the reference track
        :type tl_track: :class:`mopidy.models.TlTrack` or :class:`None`
        :rtype: :class:`mopidy.models.TlTrack` or :class:`None`
        '''
        return self.mopidy_request('core.tracklist.eot_track', tl_track=tl_track, **options)

    def set_repeat(self, value, **options):
        '''Set repeat mode.
        To repeat a single track, set both ``repeat`` and ``single``.
        :class:`True`
            The tracklist is played repeatedly.
        :class:`False`
            The tracklist is played once.
        '''
        return self.mopidy_request('core.tracklist.set_repeat', value=value, **options)
