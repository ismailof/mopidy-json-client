#!/usr/bin/python
import sys
from mopidy_json_client import SimpleClient


def controller_name(mopidy_module):
    '''Returns CamelCase name for the controller class of a given mopidy_module'''
    return mopidy_module[0].upper() + mopidy_module[1:] + 'Controller'


def generate_controller_code(mopidy_module, methods, version, exclude_parms={'kwargs'}):

    def nl(indent):
        tab_spaces = 4
        return '\n' + ' ' * indent * tab_spaces

    print('from . import MopidyWSController\n')
    print('class %s(MopidyWSController):' % controller_name(mopidy_module))
    print("%s''' Auto-generated %s Class for Mopidy JSON/RPC API version %s'''\n" % (nl(1),
                                                                                     controller_name(mopidy_module),
                                                                                     version))

    for method, info in methods.items():
        # Method name
        method_name = method.split('.')[2]
        # Parameters
        params_def = ''
        params_use = ''
        for param in info.get('params'):
            if param['name'] not in exclude_parms:
                params_def += ('{name}={default}'.format(param) if 'default' in param else param['name']) + ', '
                params_use += '{name}={name}'.format(param) + ', '

        # Generate function parts
        _definition = "def %s(self, %s**options):" % (method_name, params_def)
        _body = "return self.mopidy_request('%s', %s**options)" % (method, params_use)
        _description = "'''" + info.get('description').replace('\n\n', '\n').replace('\n', nl(2)) + nl(2) + "'''"
        _comments = (nl(1) + '# DEPRECATED') if '.. deprecated::' in _description else ''

        _function = _comments + nl(1) + _definition + nl(2) + _description + nl(2) + _body

        # Print Wrapper Function for the method
        print(_function)


if __name__ == '__main__':

    mopidy_modules = {'playback',
                      'mixer',
                      'tracklist',
                      'library',
                      'playlists',
                      'history'}

    if len(sys.argv) == 2:
        mopidy_modules = {sys.argv[1]}
    elif len(sys.argv) > 2:
        print 'Usage: generate_api.py [mopidy_module]'
        exit(1)

    client = SimpleClient()
    version = client.core.get_version()
    api = client.core.describe()

    for module in mopidy_modules:
        methods = {method: info for method, info in api.items() if method.startswith('core.' + module)}
        generate_controller_code(module, methods, version=version)
