from .playback import PlaybackController
from .tracklist import TracklistController
from .mixer import MixerController
from .library import LibraryController
from .playlists import PlaylistsController
from .history import HistoryController

_version_ = '1.1'

_all_ = [
    PlaybackController,
    TracklistController,
    MixerController,
    LibraryController,
    PlaylistsController,
    HistoryController
]

mopidy_eventlist = [
   'track_playback_paused',
   'track_playback_resumed',
   'track_playback_started',
   'track_playback_ended',
   'playback_state_changed',
   'tracklist_changed',
   'playlists_loaded',
   'playlist_changed',
   'playlist_deleted',
   'options_changed',
   'volume_changed',
   'mute_changed',
   'seeked',
   'stream_title_changed'
]