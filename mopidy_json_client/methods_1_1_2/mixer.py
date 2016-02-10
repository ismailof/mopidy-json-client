from ..mopidy_api import MopidyWSController


class MixerController (MopidyWSController):

    def set_mute(self, mute, **options):
        '''Set mute state.
        :class:`True` to mute, :class:`False` to unmute.
        Returns :class:`True` if call is successful, otherwise :class:`False`.
        '''
        return self.mopidy_request('core.mixer.set_mute', mute=mute, **options)

    def get_volume(self, **options):
        '''Get the volume.
        Integer in range [0..100] or :class:`None` if unknown.
        The volume scale is linear.
        '''
        return self.mopidy_request('core.mixer.get_volume', **options)

    def set_volume(self, volume, **options):
        '''Set the volume.
        The volume is defined as an integer in range [0..100].
        The volume scale is linear.
        Returns :class:`True` if call is successful, otherwise :class:`False`.
        '''
        return self.mopidy_request('core.mixer.set_volume', volume=volume, **options)

    def get_mute(self, **options):
        '''Get mute state.
        :class:`True` if muted, :class:`False` unmuted, :class:`None` if
        unknown.
        '''
        return self.mopidy_request('core.mixer.get_mute', **options)
