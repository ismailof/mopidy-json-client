from functools import wraps
import time


def format_expand(value, indent=0, htchar='\t', lfchar='\n'):
    try:
        nlch = lfchar + htchar * (indent)
        if type(value) is dict:
            items = [
                nlch + str(key) + ': ' + format_expand(value[key], indent=indent + 1)
                for key in value
            ]
            return '%10s' % (''.join(items))
        elif type(value) is list:
            items = [
                format_expand(item, indent=indent)
                for item in value
            ]
            return '%s' % ((nlch + '+').join(items))
        elif type(value) is tuple:
            items = [
                nlch + format_expand(item, htchar, lfchar, indent=indent + 1)
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


def format_nice(data, format=None):

    try:
        if data is None:
            nice_str_data = '<None>'

        elif format == 'raw':
            print('%r %r' % (type(data), data))
            
        elif format == 'expand':
            nice_str_data = format_expand(data, indent=1)
       
        elif format == 'track':
            title = data['name']
            artist = data['artists'][0]['name'] if 'artists' in data else '<unknown>'
            uri = data['uri']
            nice_str_data = '%r - %r (%s)' % (artist, title, uri)            

        elif format == 'tracklist':
            nice_str_data = ''
            for tl_track in data:      
                str_data = {'tlid': tl_track['tlid'],
                            'title': tl_track['track']['name'],
                            'artist': tl_track['track']['artists'][0]['name'] if 'artists' in tl_track['track'] else '<unknown>',
                            'uri': tl_track['track']['uri'] }
                nice_str_data += '\n\t[%(tlid)3d] %(artist)r - %(title)r (%(uri)s)' % (str_data)

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
            nice_str_data = format_expand(data, indent=1)

        return nice_str_data
       
    except Exception as ex:
        return format_nice (data, format='raw')
    
       

def print_nice(label, data, format=None):
    # Print label and formatted data
    print('%s%s' % (label, format_nice(data, format=format)))


# TODO: Change prints for debugs ?
def debug_function(_function_):
    @wraps(_function_)
    def wrapper(*args, **kwargs):
        print('[CALL] <%r>, args %r, kwargs: %s' % (_function_.__name__, args, kwargs))
        return_value = _function_(*args, **kwargs)
        if return_value is not None:
            print('[RETURN] <%r> returned %r %r' % (_function_.__name__, return_value, type(return_value)))
            return return_value

    return wrapper
