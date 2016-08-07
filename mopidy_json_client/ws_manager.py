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
                 on_msg_error=None):

        self._on_event = on_msg_event
        self._on_result = on_msg_result
        self._on_error = on_msg_error

        self.conn_lock = threading.Condition()

    def connect_ws(self, url):

        if self.wsa:
            self.wsa.close()

        self.wsa = websocket.WebSocketApp(
            url=url,
            on_message=self._received_message,
            on_error=self._ws_error,                                          
            on_open=self._ws_open,
            on_close=self._ws_close)

        self.wsa_thread = threading.Thread(
            target=self.wsa.run_forever,
            name='WSA-Thread')
        self.wsa_thread.setDaemon(True)
        self.wsa_thread.start()

        # Wait for the WSA Thread to attemp the connection
        with self.conn_lock:
            self.conn_lock.wait(5)        

        return self.connected


    @debug_function
    def _ws_error(self, *args, **kwargs):
        with self.conn_lock:
            self.connected = False
            self.conn_lock.notify()

    @debug_function
    def _ws_open(self, *args, **kwargs):
        with self.conn_lock:
            self.connected = True
            self.conn_lock.notify()

    @debug_function
    def _ws_close(self, *args, **kwargs):        
        with self.conn_lock:
            self.connected = False          
            self.conn_lock.notify()

    def send_message(self, id_msg, method, **params):
        '''
        Generates the json-rpc message and sends it to the webserver
            method: the mopidy method to call
            **paramters: adittional parameters passed to the method
            id_msg: the json-rpc message identifier
        '''
        json_msg = {
            "id": id_msg,
            "method": method,
            "params": params,
            "jsonrpc": "2.0"}
        message = json.dumps(json_msg)

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
            error_data = msg_data.get('error')
            result_data = msg_data.get('result')

            if error_data:
                # Compose custom error message
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

                if self._on_error:
                    threading.Thread(
                        target=self._on_error,
                        kwargs={'id_msg': msg_data['id'],
                                'error': compact_error_data}
                        ).start()

            else:
                if self._on_result:
                    threading.Thread(
                        target=self._on_result,
                        kwargs={'id_msg': msg_data['id'],
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
            raise Exception('Unparseable JSON-RPC message received', message=message)

    def close(self):
        self.wsa.close()
