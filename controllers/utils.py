'''
Miscellaneous helper functions.
'''

import sys
import json
from threading import Lock

lock = Lock()

def dump( item, name ):
    '''
    Print the item contents to the terminal.
    '''
    print( name + "=" )
    print( item )
    print( "===========================" )

def write_json( file_name, data ):
    '''
    Helper function to write to JSON file.
    '''
    # acquire the lock
    with lock:

        # critical section
        with open( file_name, 'w', encoding='utf-8' ) as file:

            json.dump( data, file, ensure_ascii=False, indent=4 )

# Read JSON file
def read_json( file_name ):
    '''
    Helper function to write to JSON file.
    '''
    with open( file_name, encoding='utf-8' ) as data_file:

        data_loaded = json.load(data_file)

    return data_loaded

def str_to_class( classname ):
    '''
    Convert string to a class.

    Source: https://stackoverflow.com/a/1176180
    '''
    return getattr( sys.modules[__name__], classname )
