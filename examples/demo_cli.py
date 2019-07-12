#!/usr/bin/python
from __future__ import unicode_literals, print_function

import time
import sys
import json

from builtins import input

from mopidy_json_client import MopidyClient
from mopidy_json_client.formatting import print_nice


class MopidyWSCLI(object):

    def __init__(self, debug=False):
        super(MopidyWSCLI, self).__init__()

        print('Starting Mopidy Websocket Client CLI DEMO ...')

        # Init variables
        self.state = 'stopped'
        self.uri = None
        self.save_results = False
        self.debug_flag = debug

        # Instantiate Mopidy Client
        self.mopidy = MopidyClient(
            ws_url='ws://localhost:6680/mopidy/ws',
            error_handler=self.on_server_error,
            connection_handler=self.on_connection,
            autoconnect=False,
            retry_max=10,
            retry_secs=10
        )

        self.mopidy.debug_client(self.debug_flag)
        self.bind_events()
        self.mopidy.connect()

    def on_connection(self, conn_state):
        if conn_state:
            # Initialize mopidy track and state
            self.state = self.mopidy.playback.get_state(timeout=5)
            tl_track = self.mopidy.playback.get_current_tl_track(timeout=15)
            self.track_playback_started(tl_track)
        else:
            self.state = 'stopped'
            self.uri = None

    def bind_events(self):
        self.mopidy.bind_event('playback_state_changed', self.playback_state_changed)
        self.mopidy.bind_event('stream_title_changed', self.stream_title_changed)
        self.mopidy.bind_event('options_changed', self.options_changed)
        self.mopidy.bind_event('volume_changed', self.volume_changed)
        self.mopidy.bind_event('mute_changed', self.mute_changed)
        self.mopidy.bind_event('seeked', self.seeked)
        #self.mopidy.bind_event('audio_message', audio_message)

    def gen_uris(self, input_uris=None):
        presets = {'bt': ['bt:stream'],
                   'spotify': ['spotifyweb:yourmusic:songs'],
                   'epic': ['tunein:station:s213847'],
                   'flaix': ['tunein:station:s24989'],
                   'tunein': ['tunein:root'],
                   'uri': [self.uri],
                   'none': [None],
                   'test': ['spotify:track:4ZiMMIaoK9sSI1iQIvHSq8',
                            'tunein:station:s24989',
                            'podcast+http://feeds.feedburner.com/aokishouse#http://traffic.libsyn.com/steveaoki/037_AOKIS_HOUSE_-_STEVE_AOKI.mp3',
                            'bt:stream',
                            ],
                   }

        if not input_uris:
            return [self.uri]

        output_uris = []
        for uri in input_uris:
            if uri in presets:
                output_uris += presets[uri]
            else:
                output_uris += [uri]

        return output_uris

    def prompt(self):
        symbol = {'playing': '|>',
                  'paused': '||',
                  'stopped': '[]',
                  None: '--',
                  }
        uri = self.uri
        prompt_line = 'Mopidy %s>> ' % (
            # '{%s}(%s)' % (symbol[self.state], uri)
            '(%s)' % (symbol[self.state])
            if self.mopidy.is_connected() else '[OFFLINE]'
        )
        user_input = input(prompt_line)
        command_line = user_input.strip(' \t\n\r').split(' ')

        command = command_line[0].lower()
        args = command_line[1:]

        return command, args

    @staticmethod
    def command_on_off(args, getter, setter):
        if args:
            if args[0].lower() in {'on', 'yes', 'true'}:
                new_value = True
            elif args[0].lower() in {'off', 'no', 'false'}:
                new_value = False
        else:
            current_value = getter(timeout=15)
            new_value = not current_value

        setter(new_value)

    @staticmethod
    def command_numeric(args, getter, setter, callback=None, step=1, res=1):

        if args:
            arg_value = args[0]
            current_value = 0

            relative = +1 if arg_value.startswith('+') \
                else -1 if arg_value.startswith('-') \
                else 0

            if relative:
                current_value = getter(timeout=15)
                arg_value = arg_value[1:]
            else:
                relative = 1

            if unicode(arg_value).isnumeric():
                step = int(arg_value)
            elif arg_value:
                return

            new_value = current_value + step * relative * res
            new_value = max(new_value, 0)

            setter(new_value)

        else:
            # No argument, get current value
            getter(on_result=callback)

    def get_debug(self, **kwargs):
        return self.debug_flag

    def set_debug(self, value, **kwargs):
        self.debug_flag = value
        self.mopidy.debug_client(self.debug_flag)
        print('> Debugging mopidy-json-client : %s' % self.debug_flag)

    def get_save_results(self, **kwargs):
        return self.save_results

    def set_save_results(self, value, **kwargs):
        self.save_results = value
        print('> Saving Results to file : %s' % value)

    def execute_command(self, command, args=[]):
        # Exit demo program
        if (command == 'exit'):
            self.mopidy.disconnect()
            time.sleep(0.2)
            exit()

        # Connection methods
        elif (command == 'connect'):
            self.mopidy.connect()

        elif (command == 'disconnect'):
            self.mopidy.disconnect()

        # Core methods
        elif (command == 'api'):
            core_api = self.mopidy.core.describe(timeout=40)

            if args:
                filtered_api = {method: desc
                                for method, desc in core_api.items()
                                if any([arg in method for arg in args])}
                print_nice('*** MOPIDY CORE API [%s] ***' % ', '.join(args), filtered_api)
            else:
                print_nice('*** MOPIDY CORE API ***', core_api)

        elif (command == 'version'):
            mopidy_version = self.mopidy.core.get_version(timeout=5)
            client_version = self.mopidy.get_client_version()
            print_nice('Mopidy Core Version: ', mopidy_version)
            print_nice('Mopidy-JSON Client Version: ', client_version)

        elif (command == 'send'):
            if args:
                kwargs = {}
                try:
                    for arg in args[1:]:
                        words = arg.split('=')
                        key = words[0]
                        value = int(words[1]) if unicode(words[1]).isnumeric() \
                            else words[1]
                        kwargs.update({key: value})
                    if 'timeout' not in kwargs:
                        kwargs['timeout'] = 40

                    result = self.mopidy.core.send(args[0], **kwargs)
                    print_nice('Result: ', result)

                except Exception as ex:
                    print_nice('Exception: ', ex, format='error')
            else:
                print('Use %s <method> <arg1=vaue1> <arg2=value2> ...\n' % command)

        elif (command == 'debug'):
            self.command_on_off(args,
                                getter=self.get_debug,
                                setter=self.set_debug)

        # Get current track and update self.uri
        elif (command == 'track'):
            tl_track = self.mopidy.playback.get_current_tl_track(timeout=10)
            self.track_playback_started(tl_track)

        elif(command == 'stream'):
            self.mopidy.playback.get_stream_title(on_result=self.stream_title_changed)

        elif(command == 'pos'):
            self.command_numeric(args,
                                 getter=self.mopidy.playback.get_time_position,
                                 setter=self.mopidy.playback.seek,
                                 callback=self.seeked,
                                 step=30,
                                 res=1000)

        elif(command == 'state'):
            self.state = self.mopidy.playback.get_state(timeout=5)
            print_nice('Playback State: ', self.state)

        # Playback commands
        elif (command == 'play'):
            if args:
                if unicode(args[0]).isnumeric():
                    self.mopidy.playback.play(tlid=int(args[0]))
            else:
                self.mopidy.playback.play()
        elif (command == 'pause'):
            self.mopidy.playback.pause()
        elif (command == 'stop'):
            self.mopidy.playback.stop()
        elif (command == 'resume'):
            self.mopidy.playback.resume()
        elif (command == 'next'):
            self.mopidy.playback.next()
        elif (command in ('prev', 'previous')):
            self.mopidy.playback.previous()

        # Mixer commands
        elif (command in ('vol', 'volume')):
            self.command_numeric(args,
                                 getter=self.mopidy.mixer.get_volume,
                                 setter=self.mopidy.mixer.set_volume,
                                 callback=self.volume_changed,
                                 step=10)

        elif (command == 'mute'):
            self.command_on_off(args,
                                getter=self.mopidy.mixer.get_mute,
                                setter=self.mopidy.mixer.set_mute)

        # Tracklist commands
        elif (command == 'tracklist'):
            self.mopidy.tracklist.get_tl_tracks(on_result=self.show_tracklist)

        elif (command == 'add'):
            self.mopidy.tracklist.add(uris=self.gen_uris(args))

        elif (command == 'del'):
            if args and all([unicode(arg).isnumeric() for arg in args]):
                self.mopidy.tracklist.remove(criteria={'tlid': [int(i) for i in args]})

        elif (command == 'clear'):
            self.mopidy.tracklist.clear()

        elif (command == 'shuffle'):
            self.mopidy.tracklist.shuffle()

        elif (command == 'random'):
            self.command_on_off(args,
                                getter=self.mopidy.tracklist.get_random,
                                setter=self.mopidy.tracklist.set_random)
        elif (command == 'single'):
            self.command_on_off(args,
                                getter=self.mopidy.tracklist.get_single,
                                setter=self.mopidy.tracklist.set_single)
        elif (command == 'repeat'):
            self.command_on_off(args,
                                getter=self.mopidy.tracklist.get_repeat,
                                setter=self.mopidy.tracklist.set_repeat)
        elif (command == 'consume'):
            self.command_on_off(args,
                                getter=self.mopidy.tracklist.get_consume,
                                setter=self.mopidy.tracklist.set_consume)
        elif (command == 'options'):
            self.options_changed()

        elif (command == 'playlists'):
            self.mopidy.playlists.as_list(on_result=self.show_playlists)

        # 'Tune' the given URIs uris and play them
        elif (command == 'tune'):
            if args:
                self.mopidy.tracklist.clear()
                self.mopidy.tracklist.add(uris=self.gen_uris(args))
                self.mopidy.playback.play()
                self.execute_command('track')

        # History methods
        elif (command == 'history'):
            self.mopidy.history.get_history(on_result=self.show_history)

        # Library methods
        elif (command == 'browse'):
            uri = self.gen_uris(args)[0]
            result = self.mopidy.library.browse(uri=uri, timeout=30)
            print_nice('> Browsing %s :' % uri, result, format='browse')

        elif (command in ['info', 'lookup', 'detail']):
            info = self.mopidy.library.lookup(uris=self.gen_uris(args), timeout=30)
            print_nice('> Lookup on URIs: ', info,
                       format='expand' if command == 'detail' else 'lookup')

        elif (command in ['image', 'images']):
            images = self.mopidy.library.get_images(uris=self.gen_uris(args), timeout=30)
            print_nice('> Images for URIs :', images, format='images')

        elif (command == 'search'):
            if args:
                uris = []
                search_terms = []
                for arg in args:
                    if arg.startswith('#'):
                        arg = self.gen_uris(arg)
                    if ':' in arg:
                        uris.append(arg)
                    else:
                        search_terms.append(arg)
                if not uris:
                    uris = []

                self.mopidy.library.search(query={'any': search_terms},
                                           uris=uris,
                                           on_result=self.show_search_results)

        # Set current uri
        elif (command == 'uri'):
            if args:
                self.uri = self.gen_uris([' '.join(args)])[0]

            print_nice ("> Current URI: ", self.uri)

        elif (command == 'save'):
            self.command_on_off(args,
                                getter=self.get_save_results,
                                setter=self.set_save_results)

        elif command != '':
                print("  Unknown command '%s'" % command)

    # Request callbacks

    def show_search_results(self, search_results):
        print_nice('> Search Results: ', search_results, format='search')
        if self.save_results:
            with open('result_search.json', 'w') as json_file:
                json.dump(search_results, json_file)

    def show_tracklist(self, tracklist):
        print_nice('> Current Tracklist: ', tracklist, format='tracklist')
        if self.save_results:
            with open('result_tracklist.json', 'w') as json_file:
                json.dump(tracklist, json_file)

    def show_playlists(self, playlists):
        print_nice('> User Playlists: ', playlists, format='browse')
        if self.save_results:
            with open('result_playlists.json', 'w') as json_file:
                json.dump(playlists, json_file)

    def show_history(self, history):
        print_nice('> History: ', history, format='history')
        if self.save_results:
            with open('result_history.json', 'w') as json_file:
                json.dump(history, json_file)

    # Server Error Handler

    def on_server_error(self, error):
        print_nice('[SERVER_ERROR] ', error, format='error')

    # Mopidy Corelistener Events

    def stream_title_changed(self, title):
        print_nice('> Stream Title: ', title)

    def volume_changed(self, volume):
        print_nice('> Current volume is ', volume, format='volume')

    def playback_state_changed(self, old_state, new_state):
        self.state = new_state
        print_nice('> Playback state changed to ', self.state)

    def mute_changed(self, mute):
        print_nice('> Mute State is ', mute, format='mute')

    def options_changed(self):
        options = {'random': self.mopidy.tracklist.get_random(timeout=10),
                   'single': self.mopidy.tracklist.get_single(timeout=10),
                   'consume': self.mopidy.tracklist.get_consume(timeout=10),
                   'repeat': self.mopidy.tracklist.get_repeat(timeout=10)}
        print_nice('Tracklist Options:', options, format='expand')

    def track_playback_started(self, tl_track):
        track = tl_track.get('track') if tl_track else None
        self.uri = track.get('uri') if track else None
        print_nice('> Current Track: ', track, format='track')

    def seeked(self, time_position):
        print_nice('> Current Position is ', time_position, format='time_position')

    # def audio_message(self, message):
        # if message and message['name'] == 'spectrum':
            # print(''.join(['%d'% (-val//10) for val in message['data']['magnitude']]))


if __name__ == '__main__':

    debug = False
    if len(sys.argv) > 1 and sys.argv[1] == '-v':
        debug = True

    demo = MopidyWSCLI(debug=debug)

    while True:
        command, args = demo.prompt()
        if command != '':
            demo.execute_command(command, args)
        time.sleep(0.3)
