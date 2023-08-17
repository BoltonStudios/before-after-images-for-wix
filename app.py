"""
A Flask app for Wix.
"""
# pylint: disable=broad-exception-caught
# pylint: disable=not-callable

# Python imports
import os
import json
import logging
import urllib.parse
from dataclasses import dataclass
import jwt

# Flask imports
from flask import Flask, Response, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_migrate import Migrate

# Local imports
from . import constants
from .controllers import utils
from .controllers import wix_auth_controller
from .controllers import slider_controller

# Define a base directory as the current directory.
basedir = os.path.abspath( os.path.dirname( __file__ ) )

# Create a Flask application instance.
app = Flask( __name__ )

# Define the database URI to specify the database with which to connect.
# Format for SQL Lite: sqlite:///path/to/database.db
# Format for MySQL mysql://username:password@host:port/database_name
# Format for PostgreSQL: postgresql://username:password@host:port/database_name
db_uri = 'sqlite:///' + os.path.join( basedir, 'database.db' )

# Configure Flask-SQLAlchemy configuration keys.
# Set the database URI to specify the database with which to connect.
app.config[ 'SQLALCHEMY_DATABASE_URI'] = db_uri

# Disable tracking modifications of objects to use less memory.
app.config[ 'SQLALCHEMY_TRACK_MODIFICATIONS' ] = False

# Create a database object.
db = SQLAlchemy( app )

# Create a Migrate object.
migrate = Migrate( app, db )

# Define other globals.
temp_requests_list = []
requests_list = []
component_list = []
logger = logging.getLogger()

# Define the user table class.
@dataclass
class User( db.Model ):

    # pylint: disable=too-many-instance-attributes
    # Eight is reasonable in this case.

    """
    Class to define the User table.
    """
    instance_id: db.Column      = db.Column( db.String( 200 ), primary_key = True, unique = True )
    site_id: db.Column          = db.Column( db.String( 200 ), unique = True )
    user_id: db.Column          = db.Column( db.String( 200 ), unique = True )
    refresh_token: db.Column    = db.Column( db.String( 200 ) )
    created_at: db.Column       = db.Column( db.DateTime( timezone = True ),
                                        server_default = func.now() )

    def __repr__( self ):
        return f'<user { self.instance_id }>'

# Define the slider component table class.
@dataclass
class ComponentSlider( db.Model ):

    # pylint: disable=too-many-instance-attributes
    # Eight is reasonable in this case.

    """
    Class to define the Slider Component table.
    """
    component_id: db.Column     = db.Column( db.String( 80 ), primary_key = True, unique = True )
    instance_id: db.Column      = db.Column( db.String( 80 ), db.ForeignKey( User.instance_id ) )
    before_image: db.Column     = db.Column( db.String( 1000 ) )
    before_alt_text: db.Column  = db.Column( db.String( 1000 ) )
    after_image: db.Column      = db.Column( db.String( 1000 ) )
    after_alt_text: db.Column   = db.Column( db.String( 1000 ) )
    offset: db.Column           = db.Column( db.Integer )
    offset_float: db.Column     = db.Column( db.Float )
    created_at: db.Column       = db.Column( db.DateTime( timezone = True ),
                                        server_default = func.now() )

    def __repr__( self ):
        return f'<slider { self.component_id } in { self.instance_id }>'

# Define the function to create a database.
def init_db():

    """Initialze the application's database."""

    # Issue CREATE statements for our tables and their related constructs.
    # Note: the db.create_all() function does not recreate or update a table if it already exists.
    db.create_all()

    # Return feedback to the console.
    print( "Initialized the database." )

# Ensure we are working within the application context...
with app.app_context():

    # Then create the tables if they do not already exist.
    init_db()

# Define Flask routes.
# Homepage.
@app.route('/')
def root():

    """Return a friendly greeting."""

    # Initialize variables.
    message = "The app is running."

    return render_template('index.html',
        page_id = 'home',
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

        # Get an access token from Wix.
        access_token = wix_auth_controller.get_access_token(
            refresh_token,
            auth_provider_base_url = constants.AUTH_PROVIDER_BASE_URL,
            app_secret = constants.APP_SECRET,
            app_id = constants.APP_ID
        )

        # Get data about the installation of this app on the user's website.
        app_instance = wix_auth_controller.get_app_instance(
            refresh_token,
            'https://www.wixapis.com/apps/v1/instance',
            auth_provider_base_url = constants.AUTH_PROVIDER_BASE_URL,
            app_secret = constants.APP_SECRET,
            app_id = constants.APP_ID
        )

        # Construct the URL to Completes the OAuth flow.
        # https://dev.wix.com/api/rest/getting-started/authentication#getting-started_authentication_step-5a-app-completes-the-oauth-flow
        redirect_url = "https://www.wix.com/installer/close-window?access_token="
        redirect_url += access_token

        # Extract data from the app instance.
        instance_id = app_instance[ 'instance' ][ 'instanceId' ]
        site_id = app_instance[ 'site' ][ 'siteId' ]

        # Search the User table for the instance ID (primary key)
        user_in_db = User.query.get( instance_id )

        # If the user does not exist in the table...
        if user_in_db is None:

            # Construct a new User record.
            user = User(
                instance_id = app_instance[ 'instance' ][ 'instanceId' ],
                site_id = app_instance[ 'site' ][ 'siteId' ],
                refresh_token = refresh_token
            )

        else:

            # Update the user record.
            user = user_in_db
            user.site_id = site_id
            user.refresh_token = refresh_token

        # Add the new or updated user record to the User table.
        db.session.add( user )
        db.session.commit()

        # Close the consent window by redirecting the user to the following URL
        # with the user's access token.
        return redirect( redirect_url )

    except Exception as err:
        print( "Error getting token from Wix" )
        print( err )
        return Response("{'error':'wixError'}", status=500, mimetype='application/json')


# Remove application files and data for the user (App Uninstalled)
@app.route( '/uninstall', methods=[ 'POST' ] )
def uninstall():

    """
    Take action when the application recieves a POST request from the App Removed webhook.
    
    See documentation:
    https://dev.wix.com/docs/rest/api-reference/app-management/apps/app-instance/instance-app-installed
    """

    # Initialize variables.
    instance_id = ''
    secret = constants.WEBHOOK_PUBLIC_KEY

    # If the user submitted a POST request...
    if request.method == 'POST':

        # Get the encoded data received.
        encoded_jwt = request.data

        # Decode the data using our secret.
        data = jwt.decode( encoded_jwt, secret, algorithms=["RS256"] )

        # Load the JSON payload.
        request_data = json.loads( data['data'] )

        # Print the data received to the console for debugging.
        utils.dump( request_data, "request_data" )

        # Extract the instance ID
        instance_id = request_data[ 'instanceId' ]

        # Search the tables for records, filtering by instance ID.
        # user_in_db = User.query.get( instance_id )
        # component_in_db = ComponentSlider.query.filter_by( instance_id = instance_id ).first()

        users = User.query.filter_by( instance_id = instance_id )
        components = ComponentSlider.query.filter_by( instance_id = instance_id )

        for user in users:

            # Delete the user.
            db.session.delete( user )

            # Return feedback to the console.
            print( "Deleted user #" + instance_id )

        for component in components:

            # Delete the user.
            db.session.delete( component )

            # Return feedback to the console.
            print( "Deleted component #" + component.component_id )

        # Save changes.
        db.session.commit()

        # Return feedback to the console.
        print( "Instance #" + instance_id + " uninstalled." )

    # The app must return a 200 response upon successful receipt of a webhook.
    # Source: https://dev.wix.com/docs/rest/articles/getting-started/webhooks
    return "", 200

# App Settings Panel
@app.route('/settings', methods=['POST','GET'])
def settings():

    """
    Build the App Settings panel allowing users to customize the app iframe component.
    
    Find recommended App Settings panel features here:
    https://devforum.wix.com/kb/en/article/build-an-app-settings-panel-for-website-iframe-components
    """

    # Initialize variables.
    message = "It's running! Another Test"
    instance_id = None
    requested_component_id = None
    component_in_db = None
    before_image = ''
    before_alt_text = ''
    after_image = ''
    after_alt_text = ''
    slider_offset = 50
    slider_offset_float = 0.5

    # If the user submitted a GET request...
    if request.method == 'GET':

        # Assign the value of 'origCompId' from the GET request to the component_id variable.
        requested_component_id = request.args.get( 'origCompId' )

        # Search the ComponentSlider table for the component by its component ID (primary key).
        component_in_db = ComponentSlider.query.get( requested_component_id )

        # If the requested_component variable is not empty...
        if component_in_db != None:

            # Update the local variables with the requested_component values.
            instance_id     = component_in_db.instance_id
            before_image    = component_in_db.before_image
            before_alt_text = component_in_db.before_alt_text
            after_image     = component_in_db.after_image
            after_alt_text  = component_in_db.after_alt_text
            slider_offset   = component_in_db.offset
            slider_offset_float = component_in_db.offset_float

    # Pass local variables to Flask and render the template.
    return render_template('settings.html',
        page_id = 'settings',
        message = message,
        instance_id = instance_id,
        component_id = requested_component_id,
        before_image = before_image,
        before_alt_text = before_alt_text,
        after_image = after_image,
        after_alt_text = after_alt_text,
        slider_offset = slider_offset,
        slider_offset_float = slider_offset_float
    )

# Widget Component: Slider
@app.route('/widget-component-slider', methods=['POST','GET'])
def widget_component_slider():

    """
    Build the widget iframe component containing a before-and-after slider.
    """

    # Initialize variables.
    requested_component_id = None
    component_in_db = None
    before_image = ''
    after_image = ''
    slider_offset = 50
    slider_offset_float = 0.5

    # If the user submitted a POST request...
    if request.method == 'POST':

        # Get the data received.
        utils.dump( request.data, "request.data" )
        request_data = json.loads( request.data )
        requested_component_id = request_data[ "componentID" ]

        # Search the ComponentSlider table for the component by its component ID (primary key).
        component_in_db = ComponentSlider.query.get( requested_component_id )

        #
        if component_in_db is not None:

            #
            if request_data[ "action" ] == "delete" :

                # Delete the component by its ID.
                db.session.delete( component_in_db )
                db.session.commit()

            else:

                # Edit the ComponentSlider record.
                component_in_db.before_image = request_data[ 'beforeImage' ]
                component_in_db.before_alt_text = request_data[ 'beforeAltText' ]
                component_in_db.after_image = request_data[ 'afterImage' ]
                component_in_db.after_alt_text = request_data[ 'afterAltText' ]
                component_in_db.offset = request_data[ 'sliderOffset' ]
                component_in_db.offset_float = request_data[ 'sliderOffsetFloat' ]

                # Add a new component to the ComponentSlider table.
                db.session.add( component_in_db )
                db.session.commit()

        else:

            # Construct a new ComponentSlider record.
            component = ComponentSlider(
                component_id = requested_component_id,
                instance_id = request_data[ 'instanceID' ],
                before_image = request_data[ 'beforeImage' ],
                before_alt_text = request_data[ 'beforeAltText' ],
                after_image = request_data[ 'afterImage' ],
                after_alt_text = request_data[ 'afterAltText' ],
                offset = request_data[ 'sliderOffset' ],
                offset_float = request_data[ 'sliderOffsetFloat' ]
            )

            # Add a new component to the ComponentSlider table.
            db.session.add( component )
            db.session.commit()

        # Return a success message.
        return "", 201

    # If the user submitted a GET request...
    if request.method == 'GET':

        # If the GET request provided the 'origCompId'...
        if request.args.get( 'origCompId' ):

            # Assign its value to component_id...
            requested_component_id = request.args.get( 'origCompId' )

        elif request.args.get( 'viewerCompId' ):

            # Otherwise, use the 'viewerCompId' (front-end) component ID.
            requested_component_id = request.args.get( 'viewerCompId' )

        # Search the database and get the component by the requested component ID (primary key).
        component_in_db = ComponentSlider.query.get( requested_component_id )

        if component_in_db is not None:

            # Edit the ComponentSlider record.
            before_image = component_in_db.before_image
            before_alt_text = component_in_db.before_alt_text
            after_image = component_in_db.after_image
            after_alt_text = component_in_db.after_alt_text
            slider_offset = component_in_db.offset
            slider_offset_float = component_in_db.offset_float

    # Pass local variables to Flask and render the template.
    return render_template( 'widget-component-slider.html',
        page_id = 'baie-slider',
        component_id = requested_component_id,
        before_image = before_image,
        before_alt_text = before_alt_text,
        after_image = after_image,
        after_alt_text = after_alt_text,
        slider_offset = slider_offset,
        slider_offset_float = slider_offset_float
    )

# Database
@app.route( '/db-test' )
def db_test():

    """Return database contents."""

    # Initialize variables.
    users = User.query.all()
    components = ComponentSlider.query.all()

    return render_template( 'db-test.html',
        users = users,
        components = components
    )

#
@app.route( '/<int:component_id>/' )
def user_component( component_id ):

    """Return database contents."""
    component_record = ComponentSlider.query.get_or_404( component_id )
    return render_template( 'component.html',
        component = component_record
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
