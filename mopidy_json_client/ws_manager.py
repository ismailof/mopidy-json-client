import websocket
import json
import thread

from .common import * 

class MopidyWSManager (object):
            
    def __init__ (self, 
                        ws_url,
                        on_msg_event = None,
                        on_msg_result = None,
                        on_msg_error = None                        
                        ):        
               
        self._on_event = on_msg_event
        self._on_result = on_msg_result
        self._on_error = on_msg_error
        
        self.wsa = websocket.WebSocketApp(  url=ws_url,
                                            on_message=self._received_message
                                            )          
        if self.wsa:
            thread.start_new_thread(self.wsa.run_forever, ())

        #Waits for connection to start
        #TODO: Intelligent wait for connection
        #TODO: Retry connection
        time.sleep(5)

    
    def send_message (self, id_msg, method, **params):  
        '''
        Generates the json-rpc message and sends it to the webserver
            method: the mopidy method to call            
            **paramters: adittional parameters passed to the method
            id_msg: the json-rpc message identifier
        '''            
        json_msg={
            "id": id_msg,
            "method": method,
            "params": params,
            "jsonrpc": "2.0"            
        }        
        #print_nice ('JSON_MSG: ', json_msg)
        message = json.dumps(json_msg)                
        self.wsa.send(message)           
                
                   
    def _received_message (self, ws, message):            
        #Unpack received message 
        msg_data = json.loads(message)                
        
        #JSON-RPC Message (response to a request)
        if 'jsonrpc' in msg_data:        
            #Check for integrity
            assert msg_data['jsonrpc'] == '2.0', 'Wrong JSON-RPC version: %s' % msg_data['jsonrpc']
            assert 'id' in msg_data, 'JSON-RPC message has no id'
                     
            #Process received message         
            error_data = msg_data.get('error')
            result_data = msg_data.get('result')
                     
            if error_data:
                #Compose custom error message
                compact_error_data = {}
                compact_error_data['title'] = error_data.get('message')
                inner_data = error_data.get('data')
                if type(inner_data) in {str,unicode}:
                    compact_error_data['error'] = inner_data
                elif 'message' in error_data:
                    compact_error_data['error'] = inner_data.get('message')
                    compact_error_data['type'] = inner_data.get('type')
                    compact_error_data['traceback'] = inner_data.get('traceback')
                else:
                    compact_error_data['error'] = 'Error #' + error_data.get('code')                               
                
                if self._on_error:
                    self._on_error (id_msg=msg_data['id'], error=compact_error_data)
            
            else:                
                if self._on_result:
                    self._on_result (id_msg=msg_data['id'], result=result_data)
                    
        #Mopidy CoreListener Event
        elif 'event' in msg_data:            
            if self._on_event:
                event = msg_data.pop('event')   
                self._on_event (event=event, event_data=msg_data)
                
        #Received not-parseable message            
        else:                        
            raise ParseError('Unparseable JSON-RPC message received', message=message)
            
    def close (self):
        self.wsa.close()       