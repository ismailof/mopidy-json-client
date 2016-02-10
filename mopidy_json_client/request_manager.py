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
                     timeout=30,
                     **params):

        # Increase Message ID
        self.id_msg += 1

        # Generate request
        id_msg = self.id_msg
        request_data = {'method': method,
                        'params': params,
                        'callback': on_result,
                        'timeout': timeout,
                        'locked': False,
                        'start_time': time.time(),
                        'result': None
                        }
        # If no callback passed, prepare blocking method
        if on_result is None:
            request_data['locked'] = True
            request_data['callback'] = partial(self._unlock, id_msg=id_msg)

        # Add data to queue
        self.requests[id_msg] = request_data
        # Send message to websocket
        self._send_message(id_msg, request_data)

        # If no callback passed, block thread until getting a result
        if on_result is None:
            return self._wait_for_result(self.id_msg)

    def _send_message(self, id_msg, request_data):
        method = request_data['method']
        params = request_data['params']
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
