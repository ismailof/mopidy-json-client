#!/usr/bin/python

import time
import logging
from mopidy_json_client import MopidyWSClient, MopidyWSListener
from mopidy_json_client.formatting import print_nice


class MopidyWSCLI(MopidyWSListener):

    def __init__(self):
        print 'Starting Mopidy Websocket Client CLI DEMO ...'

        # Set logger debug
        client_log = logging.getLogger('mopidy_json_client')
        client_log.setLevel(logging.DEBUG)

        # Instantiate Mopidy Client
        self.mopidy = MopidyWSClient(event_handler=self.on_event,
                                     error_handler=self.on_server_error)

        # Initialize mopidy track and state
        self.state = self.mopidy.playback.get_state(timeout=5)
        tl_track = self.mopidy.playback.get_current_tl_track(timeout=15)
        self.uri = tl_track['track'].get('uri') if tl_track else None

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
        user_input = raw_input('%s {%s}(%s)>> ' % ('MoPiDy', symbol[self.state], uri))
        command_line = user_input.strip(' \t\n\r').split(' ')

        command = command_line[0].lower()
        args = command_line[1:]

        return command, args

    def command_on_off(self, args, getter, setter):
        if args:
            if args[0].lower() in {'on', 'yes', 'true'}:
                new_value = True
            elif args[0].lower() in {'off', 'no', 'false'}:
                new_value = False
        else:
            current_value = getter(timeout=15)
            new_value = not current_value

        setter(new_value)

    def execute_command(self, command, args=[]):
        # Exit demo program
        if (command == 'exit'):
            self.mopidy.close()
            exit()

        # Core methods
        elif (command == 'api'):
            core_api = self.mopidy.core.describe(timeout=40)
            
            if args:
                filtered_api = {method: desc for method, desc in core_api.iteritems() 
                                                if any([arg in method for arg in args])}
                print_nice('*** MOPIDY CORE API [%s] ***' % ', '.join(args), filtered_api)
            else:
                print_nice('*** MOPIDY CORE API ***', core_api)

        elif (command == 'version'):
            version = self.mopidy.core.get_version(timeout=5)
            print_nice('Mopidy Core Version: ', version)

        elif (command == 'send'):
            if args:
                kwargs = {}
                for arg in args[1:]:
                    words = arg.split('=')
                    kwargs.update(words[0], words[1])
                result = self.mopidy.core.send(args[0], timeout=40, **kwargs)
                print_nice('Result: ', result)
            else:
                print('\nUse %s <method> <arg1=vaue1> <arg2=value2> ...' % command)

        # Get current track and update self.uri
        elif (command == 'track'):
            track = self.mopidy.playback.get_current_tl_track(timeout=10)
            print_nice('Current Track: ', track.get('track') if track else None)
            self.uri = track['track']['uri'] if track else None

        elif(command == 'stream'):
            self.mopidy.playback.get_stream_title(on_result=self.stream_title_changed)

        elif(command == 'pos'):
            self.mopidy.playback.get_time_position(on_result=self.seeked)

        elif(command == 'state'):
            self.state = self.mopidy.playback.get_state(timeout=5)
            print_nice('Playback Status: ', self.state)

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
        elif (command == 'previous'):
            self.mopidy.playback.previous()

        elif (command == 'seek'):
            if unicode(args[0]).isnumeric():
                self.mopidy.playback.seek(time_position=int(args[0]))

        # Mixer commands
        elif (command in {'vol', 'volume'}):
            if args:
                if unicode(args[0]).isnumeric():
                    self.mopidy.playback.set_volume(volume=int(args[0]))
            else:
                vol = self.mopidy.mixer.get_volume(timeout=15)
                print_nice('[REQUEST] Current volume is ', vol)
        elif (command == '+'):
            vol = self.mopidy.mixer.get_volume(timeout=15)
            if vol is not None:
                self.mopidy.mixer.set_volume(vol + 10)
        elif (command == '-'):
            vol = self.mopidy.mixer.get_volume(timeout=15)
            if vol is not None:
                self.mopidy.mixer.set_volume(max(vol - 10, 0))
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
            print_nice('[REQUEST] Browsing %s :' % uri, result, format='browse')

        elif (command in ['info', 'lookup', 'detail']):
            info = self.mopidy.library.lookup(uris=self.gen_uris(args), timeout=30)
            print_nice('[REQUEST] Lookup on URIs: ', info,
                       format='expand' if command == 'detail' else 'lookup')

        elif (command in ['image', 'images']):
            images = self.mopidy.library.get_images(uris=self.gen_uris(args), timeout=30)
            print_nice('[REQUEST] Images for URIs :', images, format='images')

        elif (command == 'search'):
            if args:
                uris = [args[0]] if ':' in args[0] else [self.uri]
                search_terms = args[1:] if ':' in args[0] else args[0:]
                self.mopidy.library.search(query={'any': search_terms},
                                           uris=uris,
                                           on_result=self.show_search_results)

        # Set current uri
        elif (command == 'uri'):
            if args:
                self.uri = self.gen_uris(args)[0]

        elif command != '':
                print ("  Unknown command '%s'" % command)

    # Request callbacks
    def show_search_results(self, search_results):
        print_nice('[REQUEST] Search Results: ', search_results, format='search')

    def show_tracklist(self, tracklist):
        print_nice('[REQUEST] Current Tracklist: ', tracklist, format='tracklist')

    def show_history(self, history):
        print_nice('[REQUEST] History: ', history, format='history')

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
        # Currently not working. 
        # TODO: Post issue in mopidy
        pass
        #options = self.mopidy.tracklist.get_random(timeout=10)
        #options = {'random': self.mopidy.tracklist.get_random(timeout=10),
                   #'single': self.mopidy.tracklist.get_single(timeout=10),
                   #'consume': self.mopidy.tracklist.get_consume(timeout=10),
                   #'repeat': self.mopidy.tracklist.get_repeat(timeout=10)}
        #print_nice('TRACKLIST OPTIONS:', options, format='expand')

    def track_playback_started(self, tl_track):
        track = tl_track.get('track')
        self.uri = track.get('uri')
        print_nice('> Current Track is ', track, format='track')

    def seeked(self, time_position):
        print_nice('> Current Position is ', time_position, format='time_position')


if __name__ == '__main__':
    demo = MopidyWSCLI()
    while True:
        command, args = demo.prompt()
        if command != '':
            demo.execute_command(command, args)
        time.sleep(0.3)
