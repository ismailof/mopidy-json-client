from ..mopidy_api import MopidyWSController


class PlaybackController (MopidyWSController):

    def seek(self, time_position, **options):
        '''Seeks to time position given in milliseconds.
        :param time_position: time position in milliseconds
        :type time_position: int
        :rtype: :class:`True` if successful, else :class:`False`
        '''
        return self.mopidy_request('core.playback.seek', time_position=time_position, **options)

    def pause(self, **options):
        '''Pause playback.
        '''
        return self.mopidy_request('core.playback.pause', **options)

    def play(self, tl_track=None, tlid=None, **options):
        '''Play the given track, or if the given tl_track and tlid is
        :class:`None`, play the currently active track.
        Note that the track **must** already be in the tracklist.
        :param tl_track: track to play
        :type tl_track: :class:`mopidy.models.TlTrack` or :class:`None`
        :param tlid: TLID of the track to play
        :type tlid: :class:`int` or :class:`None`
        '''
        return self.mopidy_request('core.playback.play', tl_track=tl_track, tlid=tlid, **options)

    def get_time_position(self, **options):
        '''Get time position in milliseconds.
        '''
        return self.mopidy_request('core.playback.get_time_position', **options)

    def next(self, **options):
        '''Change to the next track.
        The current playback state will be kept. If it was playing, playing
        will continue. If it was paused, it will still be paused, etc.
        '''
        return self.mopidy_request('core.playback.next', **options)

    def set_state(self, new_state, **options):
        '''Set the playback state.
        Must be :attr:`PLAYING`, :attr:`PAUSED`, or :attr:`STOPPED`.
        Possible states and transitions:
        .. digraph:: state_transitions
            "STOPPED" -> "PLAYING" [ label="play" ]
            "STOPPED" -> "PAUSED" [ label="pause" ]
            "PLAYING" -> "STOPPED" [ label="stop" ]
            "PLAYING" -> "PAUSED" [ label="pause" ]
            "PLAYING" -> "PLAYING" [ label="play" ]
            "PAUSED" -> "PLAYING" [ label="resume" ]
            "PAUSED" -> "STOPPED" [ label="stop" ]
        '''
        return self.mopidy_request('core.playback.set_state', new_state=new_state, **options)

    def get_current_track(self, **options):
        '''Get the currently playing or selected track.
        Extracted from :meth:`get_current_tl_track` for convenience.
        Returns a :class:`mopidy.models.Track` or :class:`None`.
        '''
        return self.mopidy_request('core.playback.get_current_track', **options)

    def stop(self, **options):
        '''Stop playing.
        '''
        return self.mopidy_request('core.playback.stop', **options)

    def get_current_tlid(self, **options):
        '''Get the currently playing or selected TLID.
        Extracted from :meth:`get_current_tl_track` for convenience.
        Returns a :class:`int` or :class:`None`.
        .. versionadded:: 1.1
        '''
        return self.mopidy_request('core.playback.get_current_tlid', **options)

    # DEPRECATED
    def get_mute(self, **options):
        '''.. deprecated:: 1.0
            Use :meth:`core.mixer.get_mute()
            <mopidy.core.MixerController.get_mute>` instead.
        '''
        return self.mopidy_request('core.playback.get_mute', **options)

    # DEPRECATED
    def get_volume(self, **options):
        '''.. deprecated:: 1.0
            Use :meth:`core.mixer.get_volume()
            <mopidy.core.MixerController.get_volume>` instead.
        '''
        return self.mopidy_request('core.playback.get_volume', **options)

    def resume(self, **options):
        '''If paused, resume playing the current track.
        '''
        return self.mopidy_request('core.playback.resume', **options)

    def get_state(self, **options):
        '''Get The playback state.
        '''
        return self.mopidy_request('core.playback.get_state', **options)

    def get_stream_title(self, **options):
        '''Get the current stream title or :class:`None`.
        '''
        return self.mopidy_request('core.playback.get_stream_title', **options)

    def get_current_tl_track(self, **options):
        '''Get the currently playing or selected track.
        Returns a :class:`mopidy.models.TlTrack` or :class:`None`.
        '''
        return self.mopidy_request('core.playback.get_current_tl_track', **options)

    def previous(self, **options):
        '''Change to the previous track.
        The current playback state will be kept. If it was playing, playing
        will continue. If it was paused, it will still be paused, etc.
        '''
        return self.mopidy_request('core.playback.previous', **options)

    # DEPRECATED
    def set_volume(self, volume, **options):
        '''.. deprecated:: 1.0
            Use :meth:`core.mixer.set_volume()
            <mopidy.core.MixerController.set_volume>` instead.
        '''
        return self.mopidy_request('core.playback.set_volume', volume=volume, **options)

    # DEPRECATED
    def set_mute(self, mute, **options):
        '''.. deprecated:: 1.0
            Use :meth:`core.mixer.set_mute()
            <mopidy.core.MixerController.set_mute>` instead.
        '''
        return self.mopidy_request('core.playback.set_mute', mute=mute, **options)
