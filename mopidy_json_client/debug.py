from functools import wraps


# TODO: Change prints for debugs ?
def debug_function(_function_):
    @wraps(_function_)
    def wrapper(*args, **kwargs):
        print('[CALL] %r, args: %r, kwargs: %s' % (_function_.__name__,
                                                   args,
                                                   kwargs))
        try:
            return_value = _function_(*args, **kwargs)
        except Exception as ex:
            print('[EXCEPTION] %r \n %r' % (_function_.__name__, ex))

        if return_value is not None:
            print('[RETURN] %r returned %r %r' % (_function_.__name__,
                                                  return_value,
                                                  type(return_value)))
            return return_value

    return wrapper
