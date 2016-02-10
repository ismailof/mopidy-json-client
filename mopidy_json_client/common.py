from functools import wraps
import time


def format_data(value, indent=0, htchar='\t', lfchar='\n'):
    try:
        nlch = lfchar + htchar * (indent)
        if type(value) is dict:
            items = [
                nlch + str(key) + ': ' + format_data(value[key], indent=indent + 1)
                for key in value
            ]
            return '%10s' % (''.join(items))
        elif type(value) is list:
            items = [
                format_data(item, indent=indent)
                for item in value
            ]
            return '%s' % ((nlch + '+').join(items))
        elif type(value) is tuple:
            items = [
                nlch + format_data(item, htchar, lfchar, indent=indent + 1)
                for item in value
            ]
            return '(%s)' % (','.join(items))
        else:
            try:
                return str(value).replace(lfchar, nlch)
            except:
                return repr(value)
    except:
        return str(value).replace(lfchar, nlch)


def print_nice(label, data, format=None):

    try:
        if data is None:
            nice_str_data = '<None>'

        elif format == 'raw':
            print('%r %r' % (type(data), data))

        elif format == 'track':
            nice_str_data = '%r - %r' % (data['artists'][0]['name'], data['name'])

        elif format == 'tracklist':
            nice_str_data = ''
            for tl_track in data:
                tlid = tl_track['tlid']
                name = tl_track['track']['name']
                artist = tl_track['track']['artists'][0]['name']
                uri = tl_track['track']['uri']
                nice_str_data = ['\n\t[%3d] %r - %r (%s)' % (tlid, artist, name, uri)]

        elif format == 'time_position':
            secs = data / 1000
            minutes = secs // 60
            hours = secs // 3600
            nice_str_data = ('%02dm%02ds' % (minutes, secs % 60)) if (hours < 1) else '%dh%02dm%02ds' % ((hours, minutes % 60, secs % 60))

        elif format == 'image':
            str_uris = []
            for uri, uri_images in data.iteritems():
                list_images = []
                for image in uri_images:
                    list_images = '\n\t\t[%3dx%3d] %s' % (image.get('width', 0), image.get('height', 0), image.get('uri', ''))
                str_uris.append('\n\t(URI %s)' % uri + ''.join(list_images))
            nice_str_data = ''.join(str_uris)

        elif format == 'browse':
            str_browse = ['\n\t[%s] %r (%s)' % (item.get('type'), item.get('name'), item.get('uri')) for item in data]
            nice_str_data = ''.join(str_browse)

        elif format == 'history':
            str_history = ['\n\t[%s] %r (%s)' % (time.strftime('%d-%b %H:%M:%S', time.localtime(item[0] / 1000)), item[1]['name'], item[1]['uri']) for item in data]
            nice_str_data = ''.join(str_history)

        else:
            nice_str_data = format_data(data, indent=1)

        # Print label and formatted data
        print('%s%s' % (label, nice_str_data))

    except Exception as ex:
        print('%s\n%r %r' % (label, type(data), data))
        print(ex)


def debug_function(_function_):
    @wraps(_function_)
    def wrapper(*args, **kwargs):
        print('DEBUG: Called %r with args %r, kwargs: %s' % (_function_.__name__, args, kwargs))
        return_value = _function_(*args, **kwargs)
        if return_value is not None:
            print('DEBUG: Function %r returned %r %r' % (_function_.__name__, return_value, type(return_value)))
            return return_value

    return wrapper
