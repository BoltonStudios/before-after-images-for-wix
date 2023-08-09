'''
Miscellaneous helper functions.
'''

# imports
import sys
import json
from threading import Lock

# Define globals
lock = Lock()

# Dump variable values to the terminal.
def dump( item, name ):
    '''
    Print the item contents to the terminal.
    '''
    print( name + "=" )
    print( item )
    print( "===========================" )

# Write to a JSON file.
def write_json( file_name, data ):
    '''
    Helper function to write to JSON file.
    '''
    # acquire the lock
    with lock:

        # critical section
        with open( file_name, 'w', encoding='utf-8' ) as file:

            json.dump( data, file, ensure_ascii=False, indent=4 )

# Read a JSON file.
def read_json( file_name ):
    '''
    Helper function to read from a JSON file.
    '''
    with open( file_name, encoding='utf-8' ) as data_file:

        data_loaded = json.load(data_file)

    return data_loaded

#Convert string to a class.
def str_to_class( classname ):
    '''
    Given a string as user input, get the class object if there is 
    a class with that name in the currently defined namespace.

    Source: https://stackoverflow.com/a/1176180
    '''
    return getattr( sys.modules[__name__], classname )
