import time
from functools import partial


class RequestQueue (object):

    def __init__(self, send_function, start_id=1):
        self.requests = {}
        self._send_function_ = send_function
        self.id_msg = start_id

    def make_request(self,
                     method,
                     on_result=None,
                     timeout=None,
                     **params):
        
      
        # If no option is passed (callback nor timeout) send a notification (no waiting for response)
        if not on_result and not timeout:        
            self._send_message(None, method, params)
            return None
        
        # Increase Message ID
        self.id_msg += 1            
        
        # Generate request        
        request_data = {'method': method,
                        'params': params,
                        'callback': on_result if on_result else partial(self._unlock, id_msg=self.id_msg),
                        'timeout': timeout,
                        'locked': False if on_result else True,
                        'start_time': time.time(),
                        'result': None
                        }                
        # Add request to queue
        self.requests[self.id_msg] = request_data        
    
        # Send message to websocket
        self._send_message(self.id_msg, method, params)

        # Block thread until getting a result
        if request_data['locked']:
            return self._wait_for_result(self.id_msg)

    def _send_message(self, id_msg, method, params):
        self._send_function_(id_msg, method, **params)

    def result_handler(self, id_result, result):
        for id_request, req_data in self.requests.items():
            if id_request == id_result:
                # Dispatch result to callback function
                req_data['callback'](result)
                # Garbage collector: remove request from queue
                time.sleep(0.3)
                self.requests.pop(id_result)
                break

    def _unlock(self, result, id_msg=None):
        if id_msg is not None:
            self.requests[id_msg]['result'] = result
            self.requests[id_msg]['locked'] = False

    def _wait_for_result(self, id_msg):
        while self.requests[id_msg]['locked']:
            if time.time() - self.requests[id_msg]['start_time'] > self.requests[id_msg]['timeout']:
                # TODO: raise Error right
                # raise TimeoutError('Time-out on request')
                print('[TIMEOUT] On request: %s (%d secs)' % (self.requests[id_msg]['method'], self.requests[id_msg]['timeout']))
                return None
            time.sleep(0.1)  # To save resouces
        result = self.requests[id_msg]['result']
        return result
