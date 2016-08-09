import websocket
import json
import threading
import time

from debug import debug_function


class MopidyWSManager(object):

    connected = False
    wsa = None
    wsa_thread = None

    def __init__(self,
                 on_msg_event=None,
                 on_msg_result=None,
                 on_msg_error=None,
                 on_connection=None):

        self._on_event = on_msg_event
        self._on_result = on_msg_result
        self._on_error = on_msg_error
        self._on_connection = on_connection

        self.conn_lock = threading.Condition()

    @debug_function
    def connect_ws(self, url=None, locked=True):
        
        if url:
            self.ws_url = url

        if self.wsa:
            self.wsa.close()

        # Initialize websocket parameters
        self.wsa = websocket.WebSocketApp(
            url=self.ws_url,
            on_message=self._received_message,
            on_error=self._ws_error,
            on_open=self._ws_open,
            on_close=self._ws_close)

        # Run the websocket in parallel thread
        self.wsa_thread = threading.Thread(
            target=self.wsa.run_forever,
            name='WSA-Thread')
        self.wsa_thread.setDaemon(True)
        self.wsa_thread.start()

        # Return immediately if locked is not set
        if not locked:
            return None

        # Wait for the WSA Thread to attemp the connection
        with self.conn_lock:
            self.conn_lock.wait(5)

        return self.connected

    @debug_function
    def _ws_error(self, *args, **kwargs):
        pass
    
    @debug_function
    def _ws_open(self, *args, **kwargs):
        self._connection_change(connected=True)

    @debug_function
    def _ws_close(self, *args, **kwargs):
        self._connection_change(connected=False)

    @debug_function
    def _connection_change(self, connected):
        with self.conn_lock:
            self.connected = connected
            self.conn_lock.notify()

        if self._on_connection:
            threading.Thread(
                target=self._on_connection,
                args=(self.connected, ),
                ).start()
            
        # Try to reconnect
        if not self.connected:
            time.sleep (5)
            self.connect_ws(locked=False)

    def send_json_message(self, message):
        self.wsa.send(message)

    def _received_message(self, ws, message):
        # Unpack received message
        msg_data = json.loads(message)

        # JSON-RPC Message(response to a request)
        if 'jsonrpc' in msg_data:
            # Check for integrity
            assert msg_data['jsonrpc'] == '2.0', 'Wrong JSON-RPC version: %s' % msg_data['jsonrpc']
            assert 'id' in msg_data, 'JSON-RPC message has no id'

            # Process received message
            msg_id = msg_data.get('id')
            error_data = msg_data.get('error')
            result_data = msg_data.get('result')

            if error_data and self._on_error:
                threading.Thread(
                    name='Error-ID%d' % msg_id,
                    target=self._on_error,
                    kwargs={'id_msg': msg_id,
                            'error': format_error_msg(error_data)},
                    ).start()

            # Send result even if 'None' to close request            
            if self._on_result:
                threading.Thread(
                    name='Result-ID%d' % msg_id,
                    target=self._on_result,
                    kwargs={'id_msg': msg_id,
                            'result': result_data},
                    ).start()

        # Mopidy CoreListener Event
        elif 'event' in msg_data:
            if self._on_event:
                event = msg_data.pop('event')
                threading.Thread(
                    target=self._on_event,
                    kwargs={'event': event,
                            'event_data': msg_data}
                    ).start()

        # Received not-parseable message
        else:
            print('Unparseable JSON-RPC message received', message)
            #logger.warning('Unparseable JSON-RPC message received', message=message)

    # Compose JSON request message
    def format_json_msg(self, id_msg, method, **params):
        '''
        Generates the json-rpc message
            id_msg: the json-rpc message identifier
            method: the mopidy method to call
            **paramters: adittional parameters passed to the method
        '''
        json_msg = {
            "id": id_msg,
            "method": method,
            "params": params,
            "jsonrpc": "2.0"}
        message = json.dumps(json_msg)

    # Compose custom error message
    def format_error_msg(self, error_data):
        
        compact_error_data = {}
        
        compact_error_data['title'] = error_data.get('message')
        inner_data = error_data.get('data')        
        if type(inner_data) in {str, unicode}:
            compact_error_data['error'] = inner_data        
        elif 'message' in error_data:
            compact_error_data['error'] = inner_data.get('message')
            compact_error_data['type'] = inner_data.get('type')
            compact_error_data['traceback'] = inner_data.get('traceback')        
        else:
            compact_error_data['error'] = 'Error #' + error_data.get('code')

        return compact_error_data

    def close(self):
        self.wsa.close()
