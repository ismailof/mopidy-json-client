#!/usr/bin/python

import sys
from mopidy_json_client import MopidyWSClient


if len(sys.argv) != 2:
    print 'Usage: generate_api.py <mopidy_module>'
    exit(1)   

tab_spaces = 4
nl = lambda id : '\n'+' '*id*tab_spaces
mopidy_module = sys.argv[1]
exclude_parms = {'kwargs'}

client = MopidyWSClient()       
api = client.test.get_api()

print 'from .api import MopidyWSController\n'
print '%sclass %sController (MopidyWSController):' % (nl(0), mopidy_module[0].upper() + mopidy_module[1:])

for method, info in api.iteritems():
    if method.startswith('core.' + mopidy_module):              
        #Method name
        method_name = method.split('.')[2]
        #Parameters
        params_def=''
        params_use=''
        for param in info.get('params'):
            if param['name'] not in exclude_parms:
                params_def += (('%s=%s'%(param['name'],param['default'])) if 'default' in param else param['name']) + ', '        
                params_use += '%s=%s'%(param['name'],param['name']) + ', '        
        
        #Generate function parts
        _definition = "def %s(self, %s**options):" % (method_name, params_def)
        _body = "return self.mopidy_request('%s', %s**options)"% (method, params_use)        
        _description = "'''" + info.get('description').replace('\n\n','\n').replace('\n',nl(2)) + nl(2) + "'''"
        _comments = (nl(1) + '#DEPRECATED') if '.. deprecated::' in _description else ''
                    
        _function = _comments + nl(1) + _definition + nl(2) + _description + nl(2) + _body
        
        #Print Wrapper Function for the method
        print _function

