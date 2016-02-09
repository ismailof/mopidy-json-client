import time
from mopidy_json_client import MopidyWSClient, MopidyWSListener
from mopidy_json_client.common import print_nice


class MopydyWSCLI(MopidyWSListener):

    def __init__(self):
        print 'Starting Mopidy Websocket Client CLI DEMO ...'
        
        #Instantiate Mopidy Client
        self.mopidy = MopidyWSClient(event_handler=self.on_event, 
                                     error_handler=self.on_server_error)
        
        # Initialize mopidy track and state
        self.state = self.mopidy.playback.get_state()
        tl_track = self.mopidy.playback.get_current_tl_track(timeout=15)
        self.uri = tl_track['track'].get('uri') if tl_track else None

    def gen_uris(self, input_uris=None):
        presets = {'bt': 'bt:stream',
                   'spotify': 'spotifyweb:yourmusic:songs',
                   'epic': 'tunein:station:s213847',
                   'flaix': 'tunein:station:s24989',
                   'tunein': 'tunein:root',
                   'uri': self.uri,
                   'none': None,
                   }
        if not input_uris:
            return [self.uri]

        return [presets.get(key) if key in presets else key for key in input_uris]

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
        
    def execute_command(self, command, args=[]):
        # Exit demo program
        if (command == 'exit'):
            self.mopidy.close()
            exit()

        # Core methods
        elif (command == 'api'):
            core_api = self.mopidy.core.get_api(timeout=40)
            print_nice ('*** MOPIDY CORE API ***', core_api)

        elif (command == 'version'):
            version = self.mopidy.core.get_version(timeout=5)
            print_nice ('Mopidy Core Version: ', version)

        elif (command == 'send'):
            if args:
                kwargs={}
                for arg in args[1:]:
                    words=arg.split('=')
                    kwargs.update(words[0],words[1])	      
                result = self.mopidy.core.send_method('core.' + args[0], **kwargs)
                print_nice ('Result: ', result) 
            else:
                print ('\nUse %s <method> <arg1=vaue1> <arg2=value2> ...' % command)
       
        #Get current track and update self.uri
        elif (command == 'track'):
            track = self.mopidy.playback.get_current_tl_track(timeout=10)           
            self.uri = track['track']['uri'] if track else None
            # track_p = self.mopidy.tracklist.previous_track(timeout=15) 
            # track_n = self.mopidy.tracklist.next_track(tl_track=track, timeout=15)            
        
            # print_nice(' (<) Previous: ', track_p.get('track') if track_p else None, format='track')
            print_nice('Current Track: ', track.get('track') if track else None, format='track')                                 
            # print_nice(' (>)     Next: ', track_n.get('track') if track_n else None, format='track')                     
         
        elif(command == 'stream'):
            self.mopidy.playback.get_stream_title(on_result=self.stream_title_changed)

        elif(command == 'pos'):
            self.mopidy.playback.get_time_position(on_result=self.seeked)

        elif(command == 'state'):
            self.state = self.mopidy.playback.get_state()
            print_nice('Playback Status: ', self.state)
        
        #Playback commands
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
        
        #Mixer commands        
        elif (command in {'vol','volume'}):
            if args:
                if unicode(args[0]).isnumeric():
                    self.mopidy.playback.set_volume(volume=int(args[0]))
            else:
                vol = self.mopidy.mixer.get_volume(timeout=15)     
                print_nice('[REQUEST] Current volume is ', vol)
        elif (command == '+'):
            vol = self.mopidy.mixer.get_volume(timeout=15)     
            if vol is not None:
                self.mopidy.mixer.set_volume(vol+10)     
        elif (command == '-'):
            vol = self.mopidy.mixer.get_volume(timeout=15)
            if vol is not None:
                self.mopidy.mixer.set_volume(vol-10)
        elif (command == 'mute'):
            current_mute = self.mopidy.mixer.get_mute(timeout=15)     
            mute = not current_mute
            if args:
                if args[0] in {'on','yes','true'}:
                    mute = True
                elif args[0] in {'off','no','false'}:
                    mute = False
            self.mopidy.mixer.set_mute(mute)            
       
        #Tracklist commands
        elif (command == 'tracklist'):
            tracks = self.mopidy.tracklist.get_tl_tracks(on_result=self.show_tracklist)  
        elif (command == 'add'):            
            self.mopidy.tracklist.add(uris = self.gen_uris(args))            
        elif (command == 'clear'):
            self.mopidy.tracklist.clear()  
            
        #'Tune' the given (prefixed) emitter uris and play them
        elif (command == 'tune'):                                
            self.mopidy.tracklist.clear()
            self.mopidy.tracklist.add(uris=self.gen_uris(args))                
            self.mopidy.playback.play() 
            self.execute_command('track')
        
        #History methods
        elif (command == 'history'):
            self.mopidy.history.get_history(on_result=self.show_history)            
            
        #Library methods                  
        elif (command == 'browse'):  
            uri = self.gen_uris(args)[0]
            print_nice('[REQUEST] Browsing %s :'%uri, self.mopidy.library.browse(uri = uri), format='browse')
            
        elif (command in ['info','lookup']):            
            print_nice('[REQUEST] Lookup on URIs: ', self.mopidy.library.lookup(uris = self.gen_uris(args)))
            
        elif (command in ['image','images']):  
            print_nice('[REQUEST] Images for URIs :', self.mopidy.library.get_images(uris = self.gen_uris(args)), format='image')    
            
        elif (command == 'search'):            
            if args:
                uris = [args[0]] if ':' in args[0] else [self.uri]
                search_terms = args[1:] if ':' in args[0] else args[0:]
                self.mopidy.library.search(query={'any':search_terms} ,uris=uris, on_result=self.show_search_results)                   
        
        #Set current uri                    
        elif (command == 'uri'):
            if args:
                self.uri = self.gen_uris(args)[0]
                
        elif command != '':
                print ("  Unknown command '%s'" % command)
        
    # Request callbacks
    def show_search_results(self, search_results):
        print_nice ('[REQUEST] Search Results: ', search_results)           
                
    def show_tracklist(self, tracklist):
        print_nice('[REQUEST] Current Tracklist: ', tracklist, format='tracklist')                                 

    def show_history(self, history):
        print_nice('[REQUEST] History: ', history, format='history')  
        
    # Server Error Handler
    def on_server_error(self, error):
        print_nice ('[SERVER_ERROR] ', error, format='error')
                                   
    # Mopidy Corelistener Events        
    def stream_title_changed(self, title):
        print_nice('[EVENT] Stream Title: ', title)
    
    def volume_changed (self, volume):
        print_nice ('[EVENT] Current volume is ', volume, format='volume')           
    
    def playback_state_changed (self, old_state, new_state):
        self.state = new_state           
        print_nice ('[EVENT] Playback state changed to ', self.state)           
    
    def mute_changed (self, mute):
        print_nice ('[EVENT] Mute State is ', mute, format='mute')
    
    def track_playback_started (self, tl_track):        
        track = tl_track.get('track')        
        self.uri = track.get('uri')
        print_nice ('[EVENT] Current Track is ', track, format='track')          

    def seeked(self, time_position):
        print_nice ('[EVENT] Current Position is ', time_position, format='time_position')  

        
if __name__ == '__main__':    
    demo = MopydyWSCLI ()            
    while True:
        command, args = demo.prompt()
        if command != '':
            demo.execute_command(command, args)                
        time.sleep (0.3)
  
