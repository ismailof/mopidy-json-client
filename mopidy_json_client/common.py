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
            return '%s' % ((nlch+'+').join(items))
        elif type(value) is tuple:
            items = [
                nlch + format_data(item, htchar, lfchar, indent=indent + 1)
                for item in value
            ]
            return '(%s)' % (','.join(items))
        else:
            try:
                return str(value).replace(lfchar,nlch)
            except:
                return repr(value)
    except:
        return str(value).replace(lfchar,nlch) 

def print_nice (label, data, format=None):        
    
    try:   
        if data is None:
            nice_str_data = '<None>'   
        elif format == 'track':
            nice_str_data = '%r - %r' % (data['artists'][0]['name'], data['name'])        
        elif format == 'tracklist':
            str_track = ['\n\t[%3d] %r - %r (%s)' % (tl_track['tlid'], tl_track['track']['artists'][0]['name'], tl_track['track']['name'], tl_track['track']['uri']) for tl_track in data]
            nice_str_data = ''.join(str_track)
        elif format == 'time_position':
            secs = data/1000
            nice_str_data = '%02dm%02ds'%(secs//60, secs%60) if secs<3600 else '%dh%02dm%02ds'%(secs%3600, (secs//60)%60, secs%60)                                                                              
        elif format == 'image':         
            str_uris = []
            for uri, uri_images in data.iteritems():
                list_images = []
                for image in uri_images:
                    list_images = '\n\t\t[%3dx%3d] %s'%(image.get('width',0),image.get('height',0),image.get('uri',''))
                str_uris.append ('\n\t(URI %s)'%uri + ''.join(list_images))        
            nice_str_data = ''.join(str_uris)
        elif format == 'browse':               
            str_browse = ['\n\t[%s] %r (%s)'%(item.get('type'),item.get('name'),item.get('uri')) for item in data]            
            nice_str_data = ''.join(str_browse)        
        elif format == 'history':                                 
            str_history = ['\n\t[%s] %r (%s)'%(time.strftime('%d-%b %H:%M:%S',time.localtime(item[0]/1000)),item[1]['name'],item[1]['uri']) for item in data]            
            nice_str_data = ''.join(str_history)        
        else:
            nice_str_data = format_data(data, indent=1)
    
        print ('%s%s' % (label, nice_str_data))
    except Exception as ex:        
        print ('%s\n%r %r' % (label, type(data), data))
        print (ex)
        
def check_parameters (params, mandatory):        
    if mandatory:
        if type(mandatory)=='str':
            mandatory = set(mandatory)
        for mandatory_parameter in mandatory:
            assert mandatory_parameter in params, 'Parameter %s is mandatory in method %s' % (mandatory_paramenter, method)                
        
def debug_function (_function_):  
    @wraps(_function_)
    def wrapper (*args, **kwargs):
        print ('DEBUG: Called %r with args %r, kwargs: %s' % (_function_.__name__, args, kwargs))
        return_value = _function_ (*args, **kwargs)
        if return_value is not None:
            print ('DEBUG: Function %r returned %r %r' % (_function_.__name__, return_value, type(return_value)) )
            return return_value

    return wrapper
