'''
Helper functions to handle the slider widget components.
'''
# pylint: disable=relative-beyond-top-level

#import json
from ..controllers import utils

# Search for a component.
def has_component( target, _in ):
    '''
    Search the component database for a matching component ID and return True or False.
    '''

    # Initialize variables.
    components_db = _in
    did_find_component = False

    # If the received data contains a componentID key...
    if target[ 'componentID' ]:

        # Search through existing components and
        # edit a matched component.
        # Iterate over the saved sliders.
        for component in components_db["components"]:
            
            # If the ID for the saved slider in this iteration
            # matches the value of the received data's componentID...
            if component['component_id'] == target[ 'componentID' ]:

                # Update the did_find_component flag.
                did_find_component = True

                print( 'did_find_component' )
                print( "==============================" )

    # Return result.
    return did_find_component

# Get a component.
def get_component( _id, _in ):
    '''
    Search the component database for a matching component ID and return the JSON component.
    '''
    components_db = _in
    matched_component = ''

    # Iterate over the saved components.
    for component in components_db["components"]:

        # If the ID for this saved component matches the requested component...
        if component["component_id" ] == _id:

            # This component is the requested component.
            matched_component = component

    # Return the matched component.
    return matched_component

# Edit a component.
def edit_component( target, _in ):
    '''
    Search the component database for a matching component ID and overwrite the component.
    '''

    # Initialize variables.
    components_db = _in
    temp_components_db = []

    # If the received data contains a componentID key...
    if target[ 'componentID' ]:

        # Search through existing components and
        # edit a matched component.
        # Iterate over the saved sliders.
        for component_json in components_db["components"]:

            # If the ID for the saved slider in this iteration
            # matches the value of the received data's componentID...
            if component_json['component_id'] == target[ 'componentID' ]:

                # Update the the saved slider in this iteration.
                component_json['component_id'] = target[ 'componentID' ]
                component_json['offset'] = target[ 'sliderOffset' ]
                component_json['offset_float'] = float(target[ 'sliderOffset' ])/100

            # Add the updated component data to temp array.
            temp_components_db.append( component_json )

    # Replace the components array with the temparay.
    components_db["components"] = temp_components_db

    # Saved changes to the database.
    utils.write_json( 'components.json' , components_db )


# Add a new component.
def add_component( new_component, _in ):
    '''
    Add a new component to the component database.
    '''

    # Initialize variables.
    components_db = _in

    #
    new_component_json = {
        'component_id': new_component.component_id,
        'offset': new_component.offset,
        'offset_float': new_component.offset_float
    }

    # Add the new component to the saved components list as JSON.
    components_db["components"].append( new_component_json )

    utils.dump( components_db, "components_db" )

    # Saved changes to the database.
    utils.write_json( 'components.json' , components_db )
