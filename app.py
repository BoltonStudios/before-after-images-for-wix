"""
A Flask app for Wix.
"""
# pylint: disable=broad-exception-caught

# imports
import os
import json
import logging
import urllib.parse
import constants
from model.WidgetComponentSlider import WidgetComponentSlider
from controllers import utils
from controllers import wix_auth_controller

# flask imports
from flask import Flask, Response, redirect, render_template, request

# Define globals
app = Flask(__name__)
temp_requests_list = []
requests_list = []
component_list = []
logger = logging.getLogger()

# Define routes.
# Homepage.
@app.route('/')
def root():

    """Return a friendly greeting."""

    # Initialize variables.
    message = "The app is running."

    return render_template('index.html',
        message=message
    )

# App URL (Installation) page.
@app.route( '/app-wix', methods=[ 'POST', 'GET' ] )
def app_wix():

    """
    The program calls this route before Wix asks the user to provide consent.

    Configure the 'App URL' in the Wix Developers to point here
    This code was adapted from functions posted by SAMobileDev repository here: 
    https://github.com/wix-incubator/sample-wix-rest-app/blob/master/src/index.js
    Source: Wix Sample Rest App source code https://github.com/wix-incubator
    retrieved in June 2023.
    """

    print( "Got a call from Wix for app installation." )
    print( "==============================" )

    # Construct the app installation URL.
    permission_request_url = "https://www.wix.com/installer/install"
    app_id = constants.APP_ID
    redirect_url = 'https://' + request.host + '/redirect-wix'
    redirect_url = urllib.parse.quote( redirect_url, safe='~')
    token = request.args.get( 'token' )
    url = permission_request_url + '?token=' + token + '&state=start'
    url += '&appId=' + app_id + '&redirectUrl=' + redirect_url

    print( "redirecting to " + url )
    print( "=============================" )

    # Redirect to the app installation URL.
    return redirect( url )

# Redirect URL (App Authorized, Complete Installation).
@app.route( '/redirect-wix', methods=[ 'POST', 'GET' ] )
def redirect_wix():

    """
    The program calls this route once the user finishes installing your application 
    and Wix redirects them to your application's site (here).

    Configure the 'Redirect URL' in Wix Developers to point here.
    This code was adapted from functions posted by SAMobileDev repository here: 
    https://github.com/wix-incubator/sample-wix-rest-app/blob/master/src/index.js
    Source: Wix Sample Rest App source code https://github.com/wix-incubator
    retrieved in June 2023.
    """
    print( "Got a call from Wix for redirect-wix." )
    print( "=============================" )

    # Get the authorization code from Wix.
    authorization_code = request.args.get( 'code' )

    try:
        print( "Getting Tokens From Wix." )
        print( "=======================" )

        # Get a refresh token from Wix.
        refresh_token = json.loads(
            wix_auth_controller.get_tokens_from_wix(
                authorization_code,
                auth_provider_base_url = constants.AUTH_PROVIDER_BASE_URL,
                app_secret = constants.APP_SECRET,
                app_id = constants.APP_ID
            )
        )[ 'refresh_token' ]

        # Construct the URL to Completes the OAuth flow.
        # https://dev.wix.com/api/rest/getting-started/authentication#getting-started_authentication_step-5a-app-completes-the-oauth-flow
        redirect_url = "https://www.wix.com/installer/close-window?access_token="
        redirect_url += wix_auth_controller.get_access_token(
            refresh_token,
            auth_provider_base_url = constants.AUTH_PROVIDER_BASE_URL,
            app_secret = constants.APP_SECRET,
            app_id = constants.APP_ID
        )

        # Close the consent window by redirecting the user to the following URL
        # with the user's access token.
        return redirect( redirect_url )

        # Get the app instance.
        # instance = wix_auth_controller.get_app_instance(
        #    refresh_token,
        #    instance_api_url = constants.INSTANCE_API_URL,
        #    auth_provider_base_url = constants.AUTH_PROVIDER_BASE_URL,
        #    app_secret = constants.APP_SECRET,
        #    app_id = constants.APP_ID
        # )

        # return render_template(
        #    'redirect-wix.html',
        #    title = 'Wix Application',
        #    app_id = constants.APP_ID,
        #    site_display_name = instance[ 'site' ][ 'siteDisplayName' ],
        #    instance_id = instance[ 'instance' ][ 'instanceId' ],
        #    permissions = instance[ 'instance' ][ 'permissions' ],
        #    token = refresh_token,
        #    response = json.dumps( instance )
        # )

    except Exception as err:
        print( "Error getting token from Wix" )
        print( err )
        return Response("{'error':'wixError'}", status=500, mimetype='application/json')

# App Settings Pabel
@app.route('/settings', methods=['POST','GET'])
def settings():

    """
    Build the App Settings panel allowing users to customize the app iframe component.
    
    Find recommended App Settings panel features here:
    https://devforum.wix.com/kb/en/article/build-an-app-settings-panel-for-website-iframe-components
    """

    # Initialize variables.
    message = "It's running! Another Test"
    component_id = 0

    # If the user submitted a GET request...
    if request.method == 'GET':

        #
        component_id = request.args.get( 'origCompId' )

    return render_template('settings.html',
        message = message,
        component_id = component_id
    )

# Widget Component: Slider
@app.route('/widget-component-slider', methods=['POST','GET'])
def widget_component_slider():

    """
    Build the widget iframe component containing a before-and-after slider.
    """

    # Initialize variables.
    components = utils.read_json( 'components.json' )
    did_find_component = False
    matched_component = []
    requested_component_id = None
    slider_offset = 0.5

    # If the user submitted a POST request...
    if request.method == 'POST':

        # Get the data received.
        print( "request data =" )
        print( request.data )
        request_data = json.loads( request.data )

        # If the received data contains a componentID key...
        if request_data[ 'componentID' ]:

            # Search through existing components and
            # edit a matched component.
            # Iterate over the saved sliders.
            for component in components["components"]:

                # Convert string to JSON.
                component_json = json.loads( component )

                # If the ID for the saved slider in this iteration
                # matches the value of the received data's componentID...
                requested_id = request_data[ 'componentID' ]
                
                if component_json['component_id'] == requested_id:

                    # Update the did_find_component flag.
                    did_find_component = True

                    print( 'did_find_component' )
                    print( "==============================" )

                    # Update the the saved slider in this iteration.
                    component_json['component_id'] = request_data[ 'componentID' ]
                    component_json['offset'] = request_data[ 'sliderOffset' ]
                    component_json['offset_float'] = float(component_json['offset'])/100

                # Pass the updated component data back to the array item.
                component = component_json

            # Saved changes to the data store.
            utils.write_json( 'components.json' , components )

            # If the search through saved components did not find a match...
            if not did_find_component:

                # Extract data from request.
                requested_component_id = request_data[ 'componentID' ]

                # Construct a new component.
                component = WidgetComponentSlider(
                    component_id = requested_component_id,
                    offset = request_data[ 'sliderOffset' ]
                )

                # Add the new component to the saved components list as JSON.
                components["components"].append( json.dumps( component, default=vars ) )

            # Saved changes to the data store.
            utils.write_json( 'components.json' , components )

        # Return a success message.
        return "", 201

    # If the user submitted a GET request...
    if request.method == 'GET':

        # If the GET request provided the 'origCompId'...
        if request.args.get( 'origCompId' ):

            # Assign its value to component_id...
            requested_component_id = request.args.get( 'origCompId' )

        elif request.args.get( 'viewerCompId' ):

            # Or use the 'viewerCompId' (front-end) component ID, if available.
            requested_component_id = request.args.get( 'viewerCompId' )

    # Iterate over the saved components.
    for component in components["components"]:

        # Convert string to JSON.
        component = json.loads( component )

        # If the ID for this saved component matches the requested component...
        if component["component_id" ] == requested_component_id:

            # This component is the requested component.
            matched_component = component

            # Update the local variables.
            slider_offset = matched_component[ "offset_float" ]

    #
    return render_template( 'widget-component-slider.html',
        component_id = requested_component_id,
        slider_offset = slider_offset
    )

# Run the app.
if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    server_port = os.environ.get( 'PORT', '3000' )
    app.run( host='127.0.0.1', port=server_port, debug=True )
    