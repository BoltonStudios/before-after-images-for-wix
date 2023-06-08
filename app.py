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
from controllers import csv_controller
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

    # Initialize variables.=
    components = csv_controller.read_csv( 'components.csv' )
    did_find_component = False
    matched_component = []
    requested_component_id = None
    slider_offset = 0.5

    # If the user submitted a POST request...
    if request.method == 'POST':

        # Get the data received.
        print( request.data )
        data = json.loads( request.data )

        # If the received data contains a componentID key...
        if data[ 'componentID' ] :

            # Search through existing components and
            # edit a matched component.
            # Iterate over the saved sliders.
            for component in components :

                # If the ID for the saved slider in this iteration
                # matches the value of the received data's componentID...
                if component[0] == data[ 'componentID' ] :

                    # Update the did_find_component flag.
                    did_find_component = True

                    # Extract more values from the received data.
                    requested_component_id = data[ 'componentID' ]
                    component_text = data[ 'title' ]
                    component_slider_offset = data[ 'sliderOffset' ]

                    # Update the the saved slider in this iteration.
                    component[0] = requested_component_id
                    component[1] = component_text
                    component[2] = component_slider_offset

            # Saved changes to the data store.
            csv_controller.write_csv( 'components.csv' , components )

            # If the search through saved components did not find a match...
            if not did_find_component :

                # Construct a new component.
                requested_component_id = data[ 'componentID' ]
                component_text = data[ 'title' ]
                component_slider_offset = data[ 'sliderOffset' ]

                # Add the new component to the saved components list.
                components.append([
                    requested_component_id,
                    component_text,
                    component_slider_offset
                ])

            # Saved changes to the data store.
            csv_controller.write_csv( 'components.csv' , components )

    # If the user submitted a GET request...
    if request.method == 'GET':

        # If the GET request provided the 'origCompId'...
        if request.args.get( 'origCompId' ) :

            # Assign its value to component_id...
            requested_component_id = request.args.get( 'origCompId' )

        elif request.args.get( 'viewerCompId' ):

            # Or use the 'viewerCompId' (front-end) component ID, if available.
            request.args.get( 'viewerCompId' )

    # Iterate over the saved sliders.
    for component in components :

        # If the ID for this saved slider matches the current slider...
        if component[0] == requested_component_id :

            # This component is selected.
            matched_component = component

    # If the matched component has a slider offset (index 2)...
    if len( matched_component ) >= 2 :

        # Assign its value to the local slider_offset variable.
        slider_offset = int( matched_component[2] )/100

    #
    return render_template( 'widget-slider.html',
        component_id = requested_component_id,
        components = components,
        component = matched_component,
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
    