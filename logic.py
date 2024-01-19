'''
Helper functions mostly to handle Wix authorization.
'''
# pylint: disable=broad-exception-caught

# Import dependencies.
import requests
import hmac
import hashlib
import base64
from datetime import datetime, timedelta, timezone

# Dump variable values to the terminal.
def dump( item, name ):
    '''
    Print the item contents to the terminal.
    '''
    print( type( item ) )
    print( name + "=" )
    print( item )
    print( "===========================" )

def verify_hmac_signature( payload, signature, secret ):
    """Verify an HMAC signature.

    Args:
    payload: The payload of the webhook request.
    signature: The signature of the webhook request.
    secret: The secret key used to generate the signature.

    Returns:
    True if the signature is valid, False otherwise.
    """

    # Generate signature
    generated_signature = hmac.new( secret, payload, hashlib.sha256 ).digest()

    # Encode signature
    encoded_signature = base64.urlsafe_b64encode( generated_signature )

    # Format signature to remove padding (Wix encoding does not add the padding character)
    expected_signature = encoded_signature.decode().replace( "=", "" )

    # Compare signatures.
    return expected_signature == signature

# Calculate trial days
def calculate_trial_days( trial_days, start_date ):

    # Calculate the trial days elapsed by subtracting the instance creation date
    # from today's date.
    trial_days_elapsed = datetime.now( timezone.utc ) - start_date

    # Calculate the trial days remaining by subtracting trial days elapsed
    # from the trial days offered, i.e. 10 days.
    trial_days = trial_days - trial_days_elapsed

    # If the trial days remaining is negative...
    if trial_days < timedelta( days = 0 ) :

        # Set a floor of 0 days
        trial_days = timedelta( days = 0 )

    return trial_days

# Define functions.
def get_tokens_from_wix( auth_code, auth_provider_base_url, app_secret, app_id ):

    """
    Request an Access Token from Wix.
    
    This code was adapted from functions posted by SAMobileDev repository here: 
    https://github.com/wix-incubator/sample-wix-rest-app/blob/master/src/index.js
    Source: Wix Sample Rest App source code https://github.com/wix-incubator
    retrieved in June 2023.
    """

    # Initialize variables.
    url = auth_provider_base_url + "/access"
    body_parameters = {
        'code': auth_code,
        'client_secret': app_secret,
        'client_id': app_id,
        'grant_type': "authorization_code"
    }

    # Request an access token.
    token_request = requests.post( url, json = body_parameters, timeout=2.50 )
    dump( token_request.text, "token_request.text" )

    # Return the resposne with access and refresh tokens.
    return token_request.text

def get_access_token( refresh_token, auth_provider_base_url, app_secret, app_id ):

    """
    Get a new Wix Access Token using a Refresh Token.
    
    This code was adapted from functions posted by SAMobileDev repository here: 
    https://github.com/wix-incubator/sample-wix-rest-app/blob/master/src/index.js
    Source: Wix Sample Rest App source code https://github.com/wix-incubator
    retrieved in June 2023.
    """

    # Initialize variables.
    url = auth_provider_base_url + "/access"
    body_parameters = {
        'refresh_token': refresh_token,
        'client_secret': app_secret,
        'client_id': app_id,
        'grant_type': "refresh_token"
    }

    try:

        # Request an access token.
        token_request = requests.post( url, json = body_parameters, timeout = 2.50 ).json()

        # Extract the access token from response.
        access_token = token_request[ 'access_token' ]

        # Return the access token.
        return access_token
    
    except Exception as err :

        # Provide feedback for the user.
        print( 'error in get_access_token' )
        print( err )

        # Exit the function.
        return err

def get_app_instance( refresh_token, instance_api_url, auth_provider_base_url, app_secret, app_id ):

    """
    This is sample call to Wix instance API - you can find it here: 
    https://dev.wix.com/api/rest/app-management/apps/app-instance/get-app-instance
    """

    try:
        print( 'get_app_instance with refreshToken = ' + refresh_token )
        print( "==============================" )
        access_token = get_access_token( refresh_token, auth_provider_base_url, app_secret, app_id )

        headers = {
            'Authorization': access_token
        }
        instance = requests.get( instance_api_url, headers = headers, timeout = 2.50 ).json()

        return instance

    except Exception as err :

        # Provide feedback for the user.
        print( 'error in get_app_instance' )
        print( err )

        # Exit the function.
        return err

def finish_app_installation( access_token ):

    """
    Once your app requires no further setup steps, create the following request
    to mark the installation as finished:
    https://dev.wix.com/docs/rest/articles/getting-started/authentication#step-7-app-finishes-installation
    """
    print( 'Finish app installation.' )
    print( "==============================" )
    try:

        # Initialize variables.
        post_request_url = "https://www.wixapis.com/apps/v1/bi-event"
        headers = {
            'Authorization': access_token
        }
        body_parameters = {
            "eventName": "APP_FINISHED_CONFIGURATION"
        }

        # Mark the installation as finished
        response = requests.post(
            post_request_url,
            headers = headers,
            json = body_parameters,
            timeout = 2.50
        ).json()

        return response

    except Exception as err :

        # Provide feedback for the user.
        print( 'error in finish_app_installation' )
        print( err )

        # Exit the function.
        return err
