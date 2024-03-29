"""
A before-and-after slider app for Wix.
"""
# pylint: disable=broad-exception-caught
# pylint: disable=too-many-lines

# Python imports
import os
import json
import urllib.parse
import base64
from datetime import datetime, timedelta
import jwt
import requests
from dotenv import load_dotenv

# Flask imports
from flask import Flask, Response, abort, redirect, render_template, request, url_for

# Local imports
from database import db, db_uri, migrate
import logic

# Import models.
from models import Instance, Extension

# Load environment variables from .env file
load_dotenv()

# Create a Flask application instance.
app = Flask( __name__ )

# Configure Flask-SQLAlchemy configuration keys.
# Set the database URI to specify the database with which to connect.
app.config[ 'SQLALCHEMY_DATABASE_URI'] = db_uri

# Disable tracking modifications of objects to use less memory.
app.config[ 'SQLALCHEMY_TRACK_MODIFICATIONS' ] = False

# Disable strict slashes.
app.url_map.strict_slashes = False

# Create a database object.
db.init_app( app )

# Create a Migrate object.
migrate.init_app( app, db )

# Define constants.
APP_VERSION = '1.1.3'
WEBHOOK_PUBLIC_KEY = os.getenv( "WEBHOOK_PUBLIC_KEY" )
APP_ID = os.getenv( "APP_ID" )
APP_SECRET = os.getenv( "APP_SECRET" )
AUTH_PROVIDER_BASE_URL = os.getenv( "AUTH_PROVIDER_BASE_URL" )
INSTANCE_API_URL = os.getenv( "INSTANCE_API_URL" )
TRIAL_DAYS = timedelta( days = 10 )
DEFAULT_EXTENSION_LIMIT = 999
BEFORE_PLACEHOLDER_THUMBNAIL = 'images/placeholder-12.svg'
AFTER_PLACEHOLDER_THUMBNAIL = 'images/placeholder-12.svg'

# Use a template context processor to pass the current date to every template
# Source: https://stackoverflow.com/a/41231621
@app.context_processor
def inject_now():

    """
    Pass the current date to every template.
    """
    return {'now': datetime.utcnow()}

# Define Flask routes.
# Homepage.
@app.route('/')
def root():

    """Return a friendly greeting."""

    # Log event.
    logic.log_call( "root" )

    # Initialize variables.
    message = "The app is running."

    return render_template('index.html',
        page_id = 'home',
        message=message
    )

# App URL (Installation) page.
@app.route( '/app-wix/', methods=[ 'POST', 'GET' ] )
def app_wix():

    """
    The program calls this route before Wix asks the user to provide consent.

    Configure the 'App URL' in the Wix Developers to point here
    This code was adapted from functions posted by SAMobileDev repository here: 
    https://github.com/wix-incubator/sample-wix-rest-app/blob/master/src/index.js
    Source: Wix Sample Rest App source code https://github.com/wix-incubator
    retrieved in June 2023.
    """

    # Log event.
    logic.log_call( "app-wix" )

    # Construct the app installation URL.
    permission_request_url = "https://www.wix.com/installer/install"
    app_id = APP_ID
    redirect_url = 'https://' + request.host + '/redirect-wix/'
    redirect_url = urllib.parse.quote( redirect_url, safe='~')
    token = request.args.get( 'token' )
    url = permission_request_url + '?token=' + token + '&state=start'
    url += '&appId=' + app_id + '&redirectUrl=' + redirect_url

    print( "redirecting to " + url )
    print( "=============================" )

    # Redirect to the app installation URL.
    return redirect( url )

# Redirect URL (App Authorized, Complete Installation).
@app.route( '/redirect-wix/', methods=[ 'POST', 'GET' ] )
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

    # Get the authorization code from Wix.
    instance_id = request.args.get( 'instanceId' )
    authorization_code = request.args.get( 'code' )

    # Log event.
    logic.log_call( "redirect-wix", instance_id )

    try:

        # Initialize variables.
        auth_provider_base_url = AUTH_PROVIDER_BASE_URL
        app_secret = APP_SECRET
        app_id = APP_ID
        site_url = 'Not published'
        site_id = ''

        # Prepare request.
        request_body_parameters = {
            'code': authorization_code,
            'client_secret': app_secret,
            'client_id': app_id,
            'grant_type': "authorization_code"
        }

        # Request an access token from Wix.
        token_request = requests.post( auth_provider_base_url + "/access",
                                      json = request_body_parameters, timeout=2.50 ).text

        # Parse response as JSON.
        tokens = json.loads( token_request )

        # Extract the access_token string from the response.
        access_token = tokens[ 'access_token' ]
        refresh_token = tokens[ 'refresh_token' ]

        # Check with Wix for the current instance data.
        # Get data about the installation of this app on the user's website.
        app_instance = logic.get_app_instance(
            refresh_token,
            INSTANCE_API_URL,
            AUTH_PROVIDER_BASE_URL,
            APP_SECRET,
            APP_ID
        )

        # If the app instance API call returned site info...
        if 'site' in app_instance :

            # Extract extra info about the site.
            site = app_instance['site']
            site_id = site['siteId']

            # Site URL (empty if site is not published).
            if 'url' in site :

                # Extract site url.
                site_url = app_instance['site']['url']
                print( "Site URL: " + site_url )

        # Construct the URL to Completes the OAuth flow.
        # https://dev.wix.com/api/rest/getting-started/authentication#getting-started_authentication_step-5a-app-completes-the-oauth-flow
        complete_oauth_redirect_url = "https://www.wix.com/installer/close-window?access_token="
        complete_oauth_redirect_url += access_token

        # Search the Instance table for the instance ID (primary key)
        instance_in_db = Instance.query.get( instance_id )

        # If the instance does not exist in the table...
        if instance_in_db is None:

            # Construct a new Instance record.
            instance = Instance(
                instance_id = instance_id,
                refresh_token = refresh_token,
                site_url = site_url,
                site_id = site_id
            )

            # Add the new instance record to the Instance table.
            db.session.add( instance )

        else:

            # Update the instance record to the Instance table.
            instance_in_db.refresh_token = refresh_token
            instance_in_db.site_url = site_url,
            instance_in_db.site_id = site_id

        # Add the new or updated instance record to the Instance table.
        db.session.commit()

        # Return feedback to the console.
        print( "Instance #" + instance_id + " installed." )

        # Mark the installation complete.
        logic.finish_app_installation( access_token )

        # Close the consent window by redirecting the user to the following URL
        # with the user's access token.
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.

        print( "redirecting to " + complete_oauth_redirect_url )
        print( "=============================" )

        return redirect( complete_oauth_redirect_url )

    except Exception as err:
        print( "Error getting token from Wix" )
        print( err )
        return Response("{'error':'wixError'}", status=500, mimetype='application/json')


# Remove application files and data for the instance (App Uninstalled)
@app.route( '/uninstall/', methods=[ 'POST' ] )
def uninstall():

    """
    Take action when the application recieves a POST request from the App Removed webhook.
    
    See documentation:
    https://dev.wix.com/docs/rest/api-reference/app-management/apps/app-instance/instance-app-installed
    """

    # Log event.
    logic.log_call( "uninstall" )

    # Initialize variables.
    instance_id = ''
    secret = WEBHOOK_PUBLIC_KEY

    # If the user submitted a POST request...
    if request.method == 'POST':

        # Get the encoded data received.
        encoded_jwt = request.data

        # Decode the data using our secret.
        data = jwt.decode( encoded_jwt, secret, algorithms=["RS256"] )

        # Load the JSON payload.
        request_data = json.loads( data['data'] )

        # Extract the instance ID
        instance_id = request_data[ 'instanceId' ]

        # Search the tables for records, filtering by instance ID.
        instance = Instance.query.filter_by( instance_id = instance_id ).first()
        extensions = Extension.query.filter_by( instance_id = instance_id )

        # Wix will repeatedly call this route if we return an error code.
        # Prevent that from happening by proceeding only if the instance exists.

        # If the instance exists...
        if instance is not None:

            # Iterate over extensions.
            for extension in extensions:

                # Delete the instance.
                db.session.delete( extension )

                # Return feedback to the console.
                print( "Deleted extension #" + extension.extension_id )

            # Reset the extension count.
            instance.extension_count = 0

            # Save changes.
            db.session.commit()

            # Return feedback to the console.
            print( "Instance #" + instance_id + " uninstalled." )

    # The app must return a 200 response upon successful receipt of a webhook.
    # Source: https://dev.wix.com/docs/rest/articles/getting-started/webhooks
    return "", 200

# Update the users isFree status (Paid Plan Purchased)
@app.route( '/upgrade/', methods=[ 'POST' ] )
def upgrade():

    """
    Take action when the application recieves a POST request from the Paid Plan Purchased webhook.
    
    See documentation:
    https://dev.wix.com/docs/rest/api-reference/app-management/apps/app-instance/paid-plan-purchased
    """

    # Log event.
    logic.log_call( "upgrade" )

    # Initialize variables.
    instance_id = ''
    secret = WEBHOOK_PUBLIC_KEY
    now = datetime.utcnow()
    one_month_from_now = now + timedelta( 1 * 30 )

    # If the user submitted a POST request...
    if request.method == 'POST':

        # Get the encoded data received.
        encoded_jwt = request.data

        # Decode the data using our secret.
        data = jwt.decode( encoded_jwt, secret, algorithms=["RS256"] )

        # Load the JSON payload.
        request_data = json.loads( data['data'] )
        product_data = json.loads( request_data['data'] )

        # Extract the instance ID
        instance_id = request_data[ 'instanceId' ]

        # Extract the product ID
        product_id = product_data[ 'vendorProductId' ]

        # Search the tables for records, filtering by instance ID.
        instance = Instance.query.filter_by( instance_id = instance_id ).first()

        # If the instance exists and the product_id is not null.
        if instance and product_id:

            # Change the user to a paid user.
            instance.is_free = False
            instance.did_cancel = False

            # Extract the expiration date
            if 'expiresOn' in product_data :

                instance.expires_on = datetime.strptime( product_data[ 'expiresOn' ],
                                                        '%Y-%m-%dT%H:%M:%SZ' )

            else :

                # Default to the shortest allowable paid interval.
                instance.expires_on = one_month_from_now

            # Add the new or updated instance record to the Instance table.
            db.session.commit()

            # Return feedback to the console.
            print( "Instance #" + instance_id + " upgraded.")

        else:

            # Return feedback to the console.
            print( "Instance #" + instance_id + " or vendorProductId not found.")

    # The app must return a 200 response upon successful receipt of a webhook.
    # Source: https://dev.wix.com/docs/rest/articles/getting-started/webhooks
    return "", 200

# Update the users isFree status (Paid Plan Cancelled)
@app.route( '/downgrade/', methods=[ 'POST' ] )
def downgrade():

    """
    Take action when the application recieves a POST request from 
    the Paid Plan Auto Renewal Cancelled webhook.
    
    See documentation:
    https://dev.wix.com/docs/rest/api-reference/app-management/apps/app-instance/instance-app-installed
    """

    # Log event.
    logic.log_call( "downgrade" )

    # Initialize variables.
    instance_id = ''
    secret = WEBHOOK_PUBLIC_KEY

    # If the user submitted a POST request...
    if request.method == 'POST':

        # Get the encoded data received.
        encoded_jwt = request.data

        # Decode the data using our secret.
        data = jwt.decode( encoded_jwt, secret, algorithms=["RS256"] )

        # Load the JSON payload.
        request_data = json.loads( data['data'] )
        product_data = json.loads( request_data['data'] )

        # Extract the instance ID
        instance_id = request_data[ 'instanceId' ]

        # Extract the product ID
        product_id = product_data[ 'vendorProductId' ]

        # Search the tables for records, filtering by instance ID.
        instance = Instance.query.filter_by( instance_id = instance_id ).first()

        # If the instance exists and the product_id is not null.
        if instance and product_id:

            # Flag the user cancellation.
            instance.did_cancel = True

            # Add the new or updated instance record to the Instance table.
            db.session.commit()

            # Return feedback to the console.
            print( "Instance #" + instance_id + " downgraded.")

    # The app must return a 200 response upon successful receipt of a webhook.
    # Source: https://dev.wix.com/docs/rest/articles/getting-started/webhooks
    return "", 200

# App Settings Panel
@app.route('/settings/', methods=['POST','GET'])
def settings():

    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements
    # Our variables are reasonable in this case.

    """
    Build the App Settings panel allowing users to customize the app iframe extension.
    
    Find recommended App Settings panel features here:
    https://devforum.wix.com/kb/en/article/build-an-app-settings-panel-for-website-iframe-components
    """

    # Log event.
    logic.log_call( "settings" )

    # Initialize variables.
    instance_id = None
    requested_extension_id = None
    extension_in_db = None
    is_free = True # Change to True for production.
    trial_days = TRIAL_DAYS
    before_image = url_for( 'static', filename = BEFORE_PLACEHOLDER_THUMBNAIL )
    before_image_thumbnail = url_for( 'static', filename = BEFORE_PLACEHOLDER_THUMBNAIL )
    before_label_text = 'Before'
    before_alt_text = ''
    after_image = url_for( 'static', filename = AFTER_PLACEHOLDER_THUMBNAIL )
    after_image_thumbnail = url_for( 'static', filename = AFTER_PLACEHOLDER_THUMBNAIL )
    after_label_text = 'After'
    after_alt_text = ''
    slider_offset = 50
    slider_offset_float = 0.5
    mouseover_action = 1
    handle_animation = 0
    handle_border_color = '#BBBBBB'
    is_move_on_click_enabled = False
    is_vertical = False
    is_dark = False

    # If the user submitted a GET request...
    if request.method == 'GET':

        # Assign the value of 'origCompId' from the GET request to the extension_id variable.
        requested_extension_id = request.args.get( 'origCompId' )

        # Search the Extension table for the extension by its extension ID (primary key).
        extension_in_db = Extension.query.get( requested_extension_id )

        # Load existing extension...
        if extension_in_db is not None:

            # Update the local variables with the requested_extension values.
            instance_id                 = extension_in_db.instance.instance_id
            is_free                     = extension_in_db.instance.is_free
            trial_days                  = logic.calculate_trial_days(
                                                trial_days,
                                                extension_in_db.instance.created_at
                                            )
            before_image                = extension_in_db.before_image
            before_image_thumbnail      = extension_in_db.before_image_thumbnail
            before_label_text           = extension_in_db.before_label_text
            before_alt_text             = extension_in_db.before_alt_text
            after_image                 = extension_in_db.after_image
            after_image_thumbnail       = extension_in_db.after_image_thumbnail
            after_label_text            = extension_in_db.after_label_text
            after_alt_text              = extension_in_db.after_alt_text
            slider_offset               = extension_in_db.offset
            slider_offset_float         = extension_in_db.offset_float
            mouseover_action            = extension_in_db.mouseover_action
            handle_animation            = extension_in_db.handle_animation
            handle_border_color         = extension_in_db.handle_border_color
            is_move_on_click_enabled    = extension_in_db.is_move_on_click_enabled
            is_vertical                 = extension_in_db.is_vertical
            is_dark                     = extension_in_db.is_dark

    # Pass local variables to Flask and render the template.
    return render_template('settings.html',
        page_id = 'settings',
        app_id = APP_ID,
        app_version = APP_VERSION,
        instance_id = instance_id,
        is_free = is_free,
        extension_id = requested_extension_id,
        before_image = before_image,
        before_image_thumbnail = before_image_thumbnail,
        before_label_text = before_label_text,
        before_alt_text = before_alt_text,
        after_image = after_image,
        after_image_thumbnail = after_image_thumbnail,
        after_label_text = after_label_text,
        after_alt_text = after_alt_text,
        slider_offset = slider_offset,
        slider_offset_float = slider_offset_float,
        is_vertical = is_vertical,
        is_dark = is_dark,
        mouseover_action = mouseover_action,
        handle_animation = handle_animation,
        handle_border_color = handle_border_color,
        is_move_on_click_enabled = is_move_on_click_enabled,
        trial_days = trial_days.days
    )

# Widget Slider
@app.route('/widget/', methods=['POST','GET'])
def widget():

    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements
    # Our variables are reasonable in this case.

    """
    Build the widget iframe extension containing a before-and-after slider.
    """

    # Initialize variables.
    requested_extension_id = None
    extension_in_db = None
    is_free = True # Change to True for production.
    did_cancel = False
    trial_days = TRIAL_DAYS
    extension_count = 0
    extension_limit = DEFAULT_EXTENSION_LIMIT
    before_image = url_for( 'static', filename = BEFORE_PLACEHOLDER_THUMBNAIL )
    before_image_thumbnail = url_for( 'static', filename = BEFORE_PLACEHOLDER_THUMBNAIL )
    before_label_text = 'Before'
    before_alt_text = ''
    after_image = url_for( 'static', filename = AFTER_PLACEHOLDER_THUMBNAIL )
    after_image_thumbnail = url_for( 'static', filename = AFTER_PLACEHOLDER_THUMBNAIL )
    after_label_text = 'After'
    after_alt_text = ''
    slider_offset = 50
    slider_offset_float = 0.5
    slider_orientation = 'horizontal'
    is_vertical = False
    slider_dark_mode = ''
    is_dark = False
    mouseover_action = 1
    handle_animation = 0
    handle_border_color = '#BBBBBB'
    encoded_handle_border_color = '%23BBBBBB'
    slider_no_overlay = False
    slider_move_slider_on_hover = False
    is_move_on_click_enabled = False
    expiration_date = datetime.utcnow()

    # If the user submitted a POST request...
    if request.method == 'POST':

        # Get the data received.
        request_data = json.loads( request.data )
        requested_extension_id = request_data[ "extensionId" ]

        # Search the Extension table for the extension by its extension ID (primary key).
        extension_in_db = Extension.query.get( requested_extension_id )

        # Edit existing extension.
        if extension_in_db is not None:

            # Delete existing extension.
            if request_data[ "action" ] == "delete" :

                # Delete the extension by its ID.
                db.session.delete( extension_in_db )

                # Decrement the user's extension count.
                extension_in_db.instance.extension_count -= 1

                # Save changes to the database.
                db.session.commit()

                # Log event.
                print( 'Instance #' + extension_in_db.instance.instance_id +
                      ' deleted extension #' + requested_extension_id )

            else:

                 # Update existing extension.

                # If the user selected the vertical orientation...
                if request_data[ 'sliderOrientation' ] == 'vertical' :

                    # Update the variable.
                    is_vertical = True

                # If the user selected dark mode...
                if request_data[ 'sliderDarkMode' ] == 'dark' :

                    # Update the variable.
                    is_dark = True

                # If the user selected the move on click option...
                if int( request_data[ 'sliderMoveOnClickToggle' ] ) == 1 :

                    # Update the variable.
                    is_move_on_click_enabled = True

                # Newly instantiated extensions may not yet have thumbnails.
                if 'beforeImageThumbnail' in request_data :

                    # Update the variable.
                    before_image_thumbnail = request_data[ 'beforeImageThumbnail' ]

                # Check if the request_data contains these properties.
                if 'afterImageThumbnail' in request_data :

                    # Update the variable.
                    after_image_thumbnail = request_data[ 'afterImageThumbnail' ]

                # Edit the extensionSlider record.
                extension_in_db.before_image = request_data[ 'beforeImage' ]
                extension_in_db.before_image_thumbnail = before_image_thumbnail
                extension_in_db.before_label_text = request_data[ 'beforeLabelText' ]
                extension_in_db.before_alt_text = request_data[ 'beforeAltText' ]
                extension_in_db.after_image = request_data[ 'afterImage' ]
                extension_in_db.after_image_thumbnail = after_image_thumbnail
                extension_in_db.after_label_text = request_data[ 'afterLabelText' ]
                extension_in_db.after_alt_text = request_data[ 'afterAltText' ]
                extension_in_db.offset = request_data[ 'sliderOffset' ]
                extension_in_db.offset_float = request_data[ 'sliderOffsetFloat' ]
                extension_in_db.is_vertical = is_vertical
                extension_in_db.is_dark = is_dark
                extension_in_db.mouseover_action = request_data[ 'sliderMouseoverAction' ]
                extension_in_db.handle_animation = request_data[ 'sliderHandleAnimation' ]
                extension_in_db.handle_border_color = request_data[ 'sliderHandleBorderColor' ]
                extension_in_db.is_move_on_click_enabled = is_move_on_click_enabled

                # Add a new extension to the Extension table.
                db.session.commit()

                # Log event.
                print( 'Instance #' + extension_in_db.instance.instance_id +
                      ' edited extension #' + requested_extension_id )

        else:

            # Extension not found. Create new extension.

            # Include the following 'action' conditional statement to prevent an
            # edge case where the user tries to *delete* a non-existant extension.
            #
            # The edge case can occur when a user exceeds the slider limit
            # and then attepts to delete extensions that the app never saved
            # due to the limit being reached.
            if request_data[ "action" ] == "save" :

                # Extract the instance ID
                instance_id = request_data[ 'instanceId' ]

                # If the request contains an instance ID...
                if instance_id:

                    # Get the associated Instance.
                    instance_in_db = Instance.query.get( instance_id )

                    # If the user selected the vertical orientation...
                    if request_data[ 'sliderOrientation' ] == 'vertical' :

                        # Update the variable.
                        is_vertical = True

                    # If the user selected dark mode...
                    if request_data[ 'sliderDarkMode' ] == 'dark' :

                        # Update the variable.
                        is_dark = True

                    # If the user selected the move on click option...
                    if int( request_data[ 'sliderMoveOnClickToggle' ] ) == 1 :

                        # Update the variable.
                        is_move_on_click_enabled = True

                    # Construct a new Extension record.
                    extension = Extension(
                        extension_id = requested_extension_id,
                        instance_id = instance_in_db.instance_id,
                        before_image = request_data[ 'beforeImage' ],
                        # New extensions will not have thumbnails, so use the default.
                        before_image_thumbnail = before_image_thumbnail,
                        before_label_text = request_data[ 'beforeLabelText' ],
                        before_alt_text = request_data[ 'beforeAltText' ],
                        after_image = request_data[ 'afterImage' ],
                        after_image_thumbnail = after_image_thumbnail,
                        after_label_text = request_data[ 'afterLabelText' ],
                        after_alt_text = request_data[ 'afterAltText' ],
                        offset = request_data[ 'sliderOffset' ],
                        offset_float = request_data[ 'sliderOffsetFloat' ],
                        is_vertical = is_vertical,
                        is_dark = is_dark,
                        mouseover_action = request_data[ 'sliderMouseoverAction' ],
                        handle_animation = request_data[ 'sliderHandleAnimation' ],
                        handle_border_color = request_data[ 'sliderHandleBorderColor' ],
                        is_move_on_click_enabled = is_move_on_click_enabled
                    )

                    # Check the extension count.
                    extension_count = instance_in_db.extension_count

                    # Check the extension limit.
                    extension_limit = instance_in_db.extension_limit

                    # If the extension count is within the allowable limit...
                    if extension_count <= extension_limit :

                        # Add a new extension to the extensionSlider table.
                        db.session.add( extension )

                        # Increment the user's extension count.
                        instance_in_db.extension_count += 1

                        # Log event.
                        print( 'Instance #' + instance_id +
                              ' created new extension #' + requested_extension_id )

                    # Save changes to the database.
                    db.session.commit()

        # Return a success message.
        return "", 201

    # If the user submitted a GET request...
    if request.method == 'GET':

        # If the GET request provided the 'origCompId'...
        if request.args.get( 'origCompId' ):

            # Assign its value to extension_id...
            requested_extension_id = request.args.get( 'origCompId' )

        # Otherwise, use the 'viewerCompId' (front-end) extension ID.
        elif request.args.get( 'viewerCompId' ) :

            # Assign its value to extension_id.
            requested_extension_id = request.args.get( 'viewerCompId' )

        # Search the database and get the extension by the requested extension ID (primary key).
        extension_in_db = Extension.query.get( requested_extension_id )

        # Extension found.
        if extension_in_db is not None:

            # Update the local variables with stored values from the database.
            is_free = extension_in_db.instance.is_free
            trial_days = logic.calculate_trial_days( trial_days,
                                                    extension_in_db.instance.created_at )
            did_cancel = extension_in_db.instance.did_cancel
            expiration_date = extension_in_db.instance.expires_on
            before_image = extension_in_db.before_image
            before_image_thumbnail = extension_in_db.before_image_thumbnail
            before_label_text = extension_in_db.before_label_text
            before_alt_text = extension_in_db.before_alt_text
            after_image = extension_in_db.after_image
            after_image_thumbnail = extension_in_db.after_image_thumbnail
            after_label_text = extension_in_db.after_label_text
            after_alt_text = extension_in_db.after_alt_text
            slider_offset = extension_in_db.offset
            slider_offset_float = extension_in_db.offset_float
            mouseover_action = extension_in_db.mouseover_action
            handle_animation = extension_in_db.handle_animation
            handle_border_color = extension_in_db.handle_border_color
            encoded_handle_border_color = handle_border_color.replace( "#", "%23" )
            is_move_on_click_enabled = extension_in_db.is_move_on_click_enabled

            # Mouseover action logic.
            # Move slider on mouseover.
            if mouseover_action == 2:
                slider_no_overlay = False
                slider_move_slider_on_hover = True

            # Do nothing on mouseover.
            if mouseover_action == 0:
                slider_no_overlay = True
                slider_move_slider_on_hover = False

            # If the user selected the vertical orientation...
            if extension_in_db.is_vertical is True :

                # Update the local variable for use in the widget template.
                slider_orientation  = 'vertical'

            # If the user selected dark mode...
            if extension_in_db.is_dark is True :

                # Update the local variable for use in the widget template.
                slider_dark_mode  = 'dark'

            # If the user cancelled auto-renew (did_cancel is True) and...
            # If the expiration date is in the past (expiration_date < datetime.utcnow()) and...
            # If the app counts the user as a paid user (is_free is False)...
            if did_cancel is True and expiration_date < datetime.utcnow() and is_free is False:

                try:

                    # Check with Wix for the current instance data.
                    # Get data about the installation of this app on the user's website.
                    app_instance = logic.get_app_instance(
                        extension_in_db.instance.refresh_token,
                        INSTANCE_API_URL,
                        AUTH_PROVIDER_BASE_URL,
                        APP_SECRET,
                        APP_ID
                    )

                    # Extract the isFree status.
                    is_free = app_instance['instance']['isFree']

                    # Update the record in the database.
                    extension_in_db.instance.is_free = is_free

                    # If the billing key is present...
                    if 'billing' in app_instance:

                        # Extract the billing data.
                        billing = app_instance['billing']

                        # If the 'expirationDate key is present...
                        if 'expirationDate' in billing:

                            # Get the new renewal date.
                            renewal_date = datetime.strptime( billing['expirationDate'],
                                                             '%Y-%m-%dT%H:%M:%SZ' )

                            # Update the record in the database.
                            extension_in_db.instance.expiration_date = renewal_date

                    # Save changes.
                    db.session.commit()

                except Exception as err :

                    # Provide feedback for the user.
                    print( 'Unable to resolve isFree status for Instance #' +
                          extension_in_db.instance.instance_id + '. Error:' )
                    print( err )

    # Pass local variables and render the template.
    return render_template( 'widget.html',
        page_id = "widget",
        app_version = APP_VERSION,
        is_free = is_free,
        trial_days = trial_days.days,
        extension_id = requested_extension_id,
        before_image = before_image,
        before_image_thumbnail = before_image_thumbnail,
        before_label_text = before_label_text,
        before_alt_text = before_alt_text,
        after_image = after_image,
        after_image_thumbnail = after_image_thumbnail,
        after_label_text = after_label_text,
        after_alt_text = after_alt_text,
        slider_offset = slider_offset,
        slider_offset_float = slider_offset_float,
        slider_orientation = slider_orientation,
        slider_mouseover_action = int( mouseover_action ),
        slider_handle_animation = int( handle_animation ),
        slider_handle_border_color = handle_border_color,
        slider_encoded_handle_border_color = encoded_handle_border_color,
        slider_no_overlay = int( slider_no_overlay ),
        slider_move_slider_on_hover = int( slider_move_slider_on_hover ),
        slider_move_on_click_toggle = int( is_move_on_click_enabled ),
        slider_dark_mode = slider_dark_mode
    )

# Dashboard
@app.route( '/dashboard/', methods=['GET'] )
@app.route( '/dashboard/<string:instance_id>/<int:page>', methods=['GET'] )
def dashboard( instance_id = '', page = 1 ):

    """Return database contents."""

    # Log event.
    logic.log_call( "dashboard" )

    # Initialize variables.
    admin = True
    is_free = True # Change to True for production.
    trial_days = TRIAL_DAYS
    instance = None
    extensions = None
    expiration_date = datetime.utcnow()
    extension_limit = DEFAULT_EXTENSION_LIMIT
    extension_limit_reached = False

    # If the user submitted a POST request...
    if request.method == 'GET':

        if instance_id == '' :

            if 'instance' in request.args :
                # Get app instance.
                # Extract signature and data.
                # https://dev.wix.com/docs/build-apps/build-your-app/app-instance/app-instance-client-side
                wix_signature, encoded_json = request.args.get( 'instance' ).split( '.', 1 )
                payload = encoded_json.encode( "UTF-8" )
                signature = wix_signature
                secret = APP_SECRET.encode( "UTF-8" )

                # Compare the signatures and verify a match.
                signatures_did_match = logic.verify_hmac_signature( payload, signature, secret )

                # If the signatures match...
                if signatures_did_match :

                    # Decode data from Wix.
                    # Wix says, "In Ruby or Python, you should add the padding to the
                    # Base64 encoded values that you get from Wix."
                    # Source: https://dev.wix.com/docs/build-apps/build-your-app/app-instance/app-instance-client-side
                    # Retrieved 12/31/2023
                    #
                    # The '=' below is sufficient padding.
                    # Source: https://stackoverflow.com/questions/2941995/python-ignore-incorrect-padding-error-when-base64-decoding
                    # Retrieved 12/31/2023
                    decoded_data = encoded_json + ( "=" * ((4 - len( encoded_json ) % 4) % 4) )

                    # Load data from Wix.
                    data = json.loads( base64.b64decode( decoded_data ) )

                    # Check if aid is returned in the instance parameter.
                    # Source: https://dev.wix.com/docs/build-apps/build-your-app/app-instance/app-instance-client-side
                    if 'aid' in data:

                        # Block user.
                        abort( 403 )

                    if 'instanceId' in data:

                        # Extract the instance ID
                        instance_id = data[ 'instanceId' ]

                        # Log event.
                        print( "Signatures match. Instance ID is " + instance_id )

                    else:

                        # Block user.
                        abort( 403 )

            else:

                # Block user.
                abort( 403 )

        # Update the local variables.
        instance = Instance.query.filter_by( instance_id = instance_id ).first()
        extensions = Extension.query.filter_by( instance_id = instance_id ).paginate( page = page,
                                                                                     per_page = 20 )

        # Instance found.
        if instance is not None:

            # Update the local variables with stored values from the database.
            is_free = instance.is_free
            trial_days = logic.calculate_trial_days( trial_days, instance.created_at )
            expiration_date = instance.expires_on
            extension_count = instance.extension_count
            extension_limit = instance.extension_limit

            # If the extension count exceeds the extension limit.
            if extension_count >= extension_limit :

                # Update the limit-reached flag.
                extension_limit_reached = True

    return render_template( 'dashboard.html',
        admin = admin,
        app_version = APP_VERSION,
        is_free = is_free,
        trial_days = trial_days.days,
        expiration_date = expiration_date,
        extension_count = extension_count,
        extension_limit = extension_limit,
        extension_limit_reached = extension_limit_reached,
        instance = instance,
        extensions = extensions
    )
