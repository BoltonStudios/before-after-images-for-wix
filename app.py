"""
A Flask app for Wix.
"""
# pylint: disable=broad-exception-caught
# pylint: disable=line-too-long

# imports
import os
import json
import logging
import urllib.parse
import jwt
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

    """Return a friendly HTTP greeting."""
    message = "It's running! Another Test"

    # Get Cloud Run environment variables.
    service = os.environ.get('K_SERVICE', 'Unknown service')
    revision = os.environ.get('K_REVISION', 'Unknown revision')

    return render_template('index.html',
        message=message,
        Service=service,
        Revision=revision)

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

    """Return a friendly HTTP greeting."""

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

# Webhooks page.
@app.route('/widget-slider', methods=['POST','GET'])
def widget_slider():

    """Handle webhooks."""

    # Initialize variables.
    preview_text = "No preview text."
    component_id = 0
    text_variable = "Change this."
    secret = constants.WEBHOOK_PUBLIC_KEY
    encoded_jwt = "eyJraWQiOiI5NklwcXhGOSIsImFsZyI6IlJTMjU2In0.eyJkYXRhIjoie1wiZGF0YVwiOlwie1xcbiAgXFxcImlkXFxcIiA6IFxcXCI5NWMyZjg3ZC1hZTc4LTRkZjktYWEyMS05NTE4OTIzMWQ2ZjdcXFwiLFxcbiAgXFxcImVudGl0eUZxZG5cXFwiIDogXFxcIndpeC5jcm0uaW5ib3gudjIubWVzc2FnZVxcXCIsXFxuICBcXFwic2x1Z1xcXCIgOiBcXFwibWVzc2FnZV9zZW50X3RvX2J1c2luZXNzXFxcIixcXG4gIFxcXCJlbnRpdHlJZFxcXCIgOiBcXFwiMTY0MDc3MTY2NzA5MTIxM1xcXCIsXFxuICBcXFwiYWN0aW9uRXZlbnRcXFwiIDoge1xcbiAgICBcXFwiYm9keVxcXCIgOiB7XFxuICAgICAgXFxcImNvbnZlcnNhdGlvbklkXFxcIiA6IFxcXCI1ZjY1MTY0Zi1iMzczLTNjYjktYmUyZS1mMWZkYzAwYzg2YTlcXFwiLFxcbiAgICAgIFxcXCJtZXNzYWdlXFxcIiA6IHtcXG4gICAgICAgIFxcXCJ0YXJnZXRDaGFubmVsc1xcXCIgOiBbIF0sXFxuICAgICAgICBcXFwiZGlyZWN0aW9uXFxcIiA6IFxcXCJQQVJUSUNJUEFOVF9UT19CVVNJTkVTU1xcXCIsXFxuICAgICAgICBcXFwiaWRcXFwiIDogXFxcIjE2NDA3NzE2NjcwOTEyMTNcXFwiLFxcbiAgICAgICAgXFxcInNlcXVlbmNlXFxcIiA6IFxcXCIxNjQwNzcxNjY3MDkxMjEzXFxcIixcXG4gICAgICAgIFxcXCJjb250ZW50XFxcIiA6IHtcXG4gICAgICAgICAgXFxcInByZXZpZXdUZXh0XFxcIiA6IFxcXCJKb0pvIERvZSBtYWRlIGFuIGFwcG9pbnRtZW50XFxcIixcXG4gICAgICAgICAgXFxcImZvcm1cXFwiIDoge1xcbiAgICAgICAgICAgIFxcXCJ0aXRsZVxcXCIgOiBcXFwiTmV3IFNwYSBBcHBvaW50bWVudFxcXCIsXFxuICAgICAgICAgICAgXFxcImRlc2NyaXB0aW9uXFxcIiA6IFxcXCJKb0pvIERvZSBtYWRlIGFuIGFwcG9pbnRtZW50XFxcIixcXG4gICAgICAgICAgICBcXFwiZmllbGRzXFxcIiA6IFsge1xcbiAgICAgICAgICAgICAgXFxcIm5hbWVcXFwiIDogXFxcIkZpcnN0IE5hbWVcXFwiLFxcbiAgICAgICAgICAgICAgXFxcInZhbHVlXFxcIiA6IFxcXCJKb0pvXFxcIlxcbiAgICAgICAgICAgIH0sIHtcXG4gICAgICAgICAgICAgIFxcXCJuYW1lXFxcIiA6IFxcXCJMYXN0IE5hbWVcXFwiLFxcbiAgICAgICAgICAgICAgXFxcInZhbHVlXFxcIiA6IFxcXCJEb2VcXFwiXFxuICAgICAgICAgICAgfSwge1xcbiAgICAgICAgICAgICAgXFxcIm5hbWVcXFwiIDogXFxcIlRyZWF0bWVudHNcXFwiLFxcbiAgICAgICAgICAgICAgXFxcInZhbHVlXFxcIiA6IFxcXCJNYXNzYWdlLCBNdWQgQmF0aCwgRmFjaWFsXFxcIlxcbiAgICAgICAgICAgIH0sIHtcXG4gICAgICAgICAgICAgIFxcXCJuYW1lXFxcIiA6IFxcXCJBcHBvaW50bWVudCBEYXRlXFxcIixcXG4gICAgICAgICAgICAgIFxcXCJ2YWx1ZVxcXCIgOiBcXFwiTWF5IDksIDIwMjFcXFwiXFxuICAgICAgICAgICAgfSBdLFxcbiAgICAgICAgICAgIFxcXCJtZWRpYVxcXCIgOiBbIHtcXG4gICAgICAgICAgICAgIFxcXCJpbWFnZVxcXCIgOiB7XFxuICAgICAgICAgICAgICAgIFxcXCJ1cmxcXFwiIDogXFxcImh0dHBzOi8vc3RhdGljLndpeHN0YXRpYy5jb20vbWVkaWEvZjkzZTNkNjMzZTc5OTIxZjE0MzMwZjE5MTFmYzExMzkuanBnL3YxL2ZpbGwvd18xMjAwLGhfNzk4LGFsX2MscV84NSx1c21fMC42Nl8xLjAwXzAuMDEvZjkzZTNkNjMzZTc5OTIxZjE0MzMwZjE5MTFmYzExMzkud2VicFxcXCIsXFxuICAgICAgICAgICAgICAgIFxcXCJ3aWR0aFxcXCIgOiAxMjAwLjAsXFxuICAgICAgICAgICAgICAgIFxcXCJoZWlnaHRcXFwiIDogNzk4LjBcXG4gICAgICAgICAgICAgIH1cXG4gICAgICAgICAgICB9IF1cXG4gICAgICAgICAgfVxcbiAgICAgICAgfSxcXG4gICAgICAgIFxcXCJzZW5kZXJcXFwiIDoge1xcbiAgICAgICAgICBcXFwiY29udGFjdElkXFxcIiA6IFxcXCI4OTBhMzgxNi04NWI0LTQ0YWItOTA4NS01MjQ5NzJhODUwZWZcXFwiXFxuICAgICAgICB9LFxcbiAgICAgICAgXFxcImFwcElkXFxcIiA6IFxcXCJhMGMzODY3MC02ODQ1LTQxZTAtOGY0MS04NWE2MDU0Y2NkOThcXFwiLFxcbiAgICAgICAgXFxcInZpc2liaWxpdHlcXFwiIDogXFxcIkJVU0lORVNTXFxcIixcXG4gICAgICAgIFxcXCJzb3VyY2VDaGFubmVsXFxcIiA6IFxcXCJVTktOT1dOX0NIQU5ORUxfVFlQRVxcXCIsXFxuICAgICAgICBcXFwiYmFkZ2VzXFxcIiA6IFsgXSxcXG4gICAgICAgIFxcXCJjcmVhdGVkRGF0ZVxcXCIgOiBcXFwiMjAyMS0xMi0yOVQwOTo1NDoyNy4wOTFaXFxcIlxcbiAgICAgIH1cXG4gICAgfVxcbiAgfSxcXG4gIFxcXCJldmVudFRpbWVcXFwiIDogXFxcIjIwMjEtMTItMjlUMDk6NTQ6MjcuMjcyODIzWlxcXCIsXFxuICBcXFwidHJpZ2dlcmVkQnlBbm9ueW1pemVSZXF1ZXN0XFxcIiA6IGZhbHNlXFxufSBcIixcImluc3RhbmNlSWRcIjpcIjcxNTFhMDRkLWFkZGMtNDZiYi1hNTZkLTU5YzkxNjJiNTZjNlwiLFwiZXZlbnRUeXBlXCI6XCJ3aXguY3JtLmluYm94LnYyLm1lc3NhZ2VfbWVzc2FnZV9zZW50X3RvX2J1c2luZXNzXCJ9IiwiaWF0IjoxNjg1Mjg2NjIyLCJleHAiOjE2ODg4ODY2MjJ9.ngR_fgybMhg_u2FnAyEziHNVdtfEIl1SYKy1E2L1LGimDCgkRldHetvr9vbK16emIW1_M7lFMyDC6VMt-MWwn45VY2zipT22ueB_ZFZ3hvOa2dEgyLjzBwmBM837eInEiHzarsApiMpimxFEiq_xm14hWbkXZ6lEbnb_PzixYEGAVH4tLWDbWa8bXdhOW6fenhk1OR-lBMAcfDFY4adAT1ZxKLJY21H0WbJcFAD0pt1E4HMiCzcEaZ66WyeQQZcJxa9ch44665Bf4hkNrp44qopsF89cKDXDxPfZVMrcn9QRMsWRD4M8z2tXGYyAyKo6kgP_K4nAuN8rGcdn4DmoXA"

    widget_component_sliders = csv_controller.read_csv( 'components.csv' )
    found_component = False
    selected_widget_component = []

    # If the user submitted a POST request...
    if request.method == 'POST':

        print( request.data )
        data = json.loads( request.data )

        if data[ 'componentID' ] :

            # Edit existing componenents
            for component in widget_component_sliders :

                if component[0] == data[ 'componentID' ] :

                    found_component = True

                    component_id = data[ 'componentID' ]
                    component_text = data[ 'title' ]
                    component_slider_offset = data[ 'sliderOffset' ]
                    
                    component[0] = component_id
                    component[1] = component_text
                    component[2] = component_slider_offset

            csv_controller.write_csv( 'components.csv' , widget_component_sliders )

            # Handle new component.
            if not found_component :

                component_id = data[ 'componentID' ]
                component_text = data[ 'title' ]
                component_slider_offset = data[ 'sliderOffset' ]

                widget_component_sliders.append([component_id, component_text, component_slider_offset])

            csv_controller.write_csv( 'components.csv' , widget_component_sliders )

        # If the 'list_name' key is in the request...
        if 'button_pressed' in request.form :

            print( "Aaron - Button Pressed ...")
            encoded_jwt = "eyJraWQiOiI5NklwcXhGOSIsImFsZyI6IlJTMjU2In0.eyJkYXRhIjoie1wiZGF0YVwiOlwie1xcbiAgXFxcImlkXFxcIiA6IFxcXCI5NWMyZjg3ZC1hZTc4LTRkZjktYWEyMS05NTE4OTIzMWQ2ZjdcXFwiLFxcbiAgXFxcImVudGl0eUZxZG5cXFwiIDogXFxcIndpeC5jcm0uaW5ib3gudjIubWVzc2FnZVxcXCIsXFxuICBcXFwic2x1Z1xcXCIgOiBcXFwibWVzc2FnZV9zZW50X3RvX2J1c2luZXNzXFxcIixcXG4gIFxcXCJlbnRpdHlJZFxcXCIgOiBcXFwiMTY0MDc3MTY2NzA5MTIxM1xcXCIsXFxuICBcXFwiYWN0aW9uRXZlbnRcXFwiIDoge1xcbiAgICBcXFwiYm9keVxcXCIgOiB7XFxuICAgICAgXFxcImNvbnZlcnNhdGlvbklkXFxcIiA6IFxcXCI1ZjY1MTY0Zi1iMzczLTNjYjktYmUyZS1mMWZkYzAwYzg2YTlcXFwiLFxcbiAgICAgIFxcXCJtZXNzYWdlXFxcIiA6IHtcXG4gICAgICAgIFxcXCJ0YXJnZXRDaGFubmVsc1xcXCIgOiBbIF0sXFxuICAgICAgICBcXFwiZGlyZWN0aW9uXFxcIiA6IFxcXCJQQVJUSUNJUEFOVF9UT19CVVNJTkVTU1xcXCIsXFxuICAgICAgICBcXFwiaWRcXFwiIDogXFxcIjE2NDA3NzE2NjcwOTEyMTNcXFwiLFxcbiAgICAgICAgXFxcInNlcXVlbmNlXFxcIiA6IFxcXCIxNjQwNzcxNjY3MDkxMjEzXFxcIixcXG4gICAgICAgIFxcXCJjb250ZW50XFxcIiA6IHtcXG4gICAgICAgICAgXFxcInByZXZpZXdUZXh0XFxcIiA6IFxcXCJKb0pvIERvZSBtYWRlIGFuIGFwcG9pbnRtZW50XFxcIixcXG4gICAgICAgICAgXFxcImZvcm1cXFwiIDoge1xcbiAgICAgICAgICAgIFxcXCJ0aXRsZVxcXCIgOiBcXFwiTmV3IFNwYSBBcHBvaW50bWVudFxcXCIsXFxuICAgICAgICAgICAgXFxcImRlc2NyaXB0aW9uXFxcIiA6IFxcXCJKb0pvIERvZSBtYWRlIGFuIGFwcG9pbnRtZW50XFxcIixcXG4gICAgICAgICAgICBcXFwiZmllbGRzXFxcIiA6IFsge1xcbiAgICAgICAgICAgICAgXFxcIm5hbWVcXFwiIDogXFxcIkZpcnN0IE5hbWVcXFwiLFxcbiAgICAgICAgICAgICAgXFxcInZhbHVlXFxcIiA6IFxcXCJKb0pvXFxcIlxcbiAgICAgICAgICAgIH0sIHtcXG4gICAgICAgICAgICAgIFxcXCJuYW1lXFxcIiA6IFxcXCJMYXN0IE5hbWVcXFwiLFxcbiAgICAgICAgICAgICAgXFxcInZhbHVlXFxcIiA6IFxcXCJEb2VcXFwiXFxuICAgICAgICAgICAgfSwge1xcbiAgICAgICAgICAgICAgXFxcIm5hbWVcXFwiIDogXFxcIlRyZWF0bWVudHNcXFwiLFxcbiAgICAgICAgICAgICAgXFxcInZhbHVlXFxcIiA6IFxcXCJNYXNzYWdlLCBNdWQgQmF0aCwgRmFjaWFsXFxcIlxcbiAgICAgICAgICAgIH0sIHtcXG4gICAgICAgICAgICAgIFxcXCJuYW1lXFxcIiA6IFxcXCJBcHBvaW50bWVudCBEYXRlXFxcIixcXG4gICAgICAgICAgICAgIFxcXCJ2YWx1ZVxcXCIgOiBcXFwiTWF5IDksIDIwMjFcXFwiXFxuICAgICAgICAgICAgfSBdLFxcbiAgICAgICAgICAgIFxcXCJtZWRpYVxcXCIgOiBbIHtcXG4gICAgICAgICAgICAgIFxcXCJpbWFnZVxcXCIgOiB7XFxuICAgICAgICAgICAgICAgIFxcXCJ1cmxcXFwiIDogXFxcImh0dHBzOi8vc3RhdGljLndpeHN0YXRpYy5jb20vbWVkaWEvZjkzZTNkNjMzZTc5OTIxZjE0MzMwZjE5MTFmYzExMzkuanBnL3YxL2ZpbGwvd18xMjAwLGhfNzk4LGFsX2MscV84NSx1c21fMC42Nl8xLjAwXzAuMDEvZjkzZTNkNjMzZTc5OTIxZjE0MzMwZjE5MTFmYzExMzkud2VicFxcXCIsXFxuICAgICAgICAgICAgICAgIFxcXCJ3aWR0aFxcXCIgOiAxMjAwLjAsXFxuICAgICAgICAgICAgICAgIFxcXCJoZWlnaHRcXFwiIDogNzk4LjBcXG4gICAgICAgICAgICAgIH1cXG4gICAgICAgICAgICB9IF1cXG4gICAgICAgICAgfVxcbiAgICAgICAgfSxcXG4gICAgICAgIFxcXCJzZW5kZXJcXFwiIDoge1xcbiAgICAgICAgICBcXFwiY29udGFjdElkXFxcIiA6IFxcXCI4OTBhMzgxNi04NWI0LTQ0YWItOTA4NS01MjQ5NzJhODUwZWZcXFwiXFxuICAgICAgICB9LFxcbiAgICAgICAgXFxcImFwcElkXFxcIiA6IFxcXCJhMGMzODY3MC02ODQ1LTQxZTAtOGY0MS04NWE2MDU0Y2NkOThcXFwiLFxcbiAgICAgICAgXFxcInZpc2liaWxpdHlcXFwiIDogXFxcIkJVU0lORVNTXFxcIixcXG4gICAgICAgIFxcXCJzb3VyY2VDaGFubmVsXFxcIiA6IFxcXCJVTktOT1dOX0NIQU5ORUxfVFlQRVxcXCIsXFxuICAgICAgICBcXFwiYmFkZ2VzXFxcIiA6IFsgXSxcXG4gICAgICAgIFxcXCJjcmVhdGVkRGF0ZVxcXCIgOiBcXFwiMjAyMS0xMi0yOVQwOTo1NDoyNy4wOTFaXFxcIlxcbiAgICAgIH1cXG4gICAgfVxcbiAgfSxcXG4gIFxcXCJldmVudFRpbWVcXFwiIDogXFxcIjIwMjEtMTItMjlUMDk6NTQ6MjcuMjcyODIzWlxcXCIsXFxuICBcXFwidHJpZ2dlcmVkQnlBbm9ueW1pemVSZXF1ZXN0XFxcIiA6IGZhbHNlXFxufSBcIixcImluc3RhbmNlSWRcIjpcIjcxNTFhMDRkLWFkZGMtNDZiYi1hNTZkLTU5YzkxNjJiNTZjNlwiLFwiZXZlbnRUeXBlXCI6XCJ3aXguY3JtLmluYm94LnYyLm1lc3NhZ2VfbWVzc2FnZV9zZW50X3RvX2J1c2luZXNzXCJ9IiwiaWF0IjoxNjg1Mjg2NjIyLCJleHAiOjE2ODg4ODY2MjJ9.ngR_fgybMhg_u2FnAyEziHNVdtfEIl1SYKy1E2L1LGimDCgkRldHetvr9vbK16emIW1_M7lFMyDC6VMt-MWwn45VY2zipT22ueB_ZFZ3hvOa2dEgyLjzBwmBM837eInEiHzarsApiMpimxFEiq_xm14hWbkXZ6lEbnb_PzixYEGAVH4tLWDbWa8bXdhOW6fenhk1OR-lBMAcfDFY4adAT1ZxKLJY21H0WbJcFAD0pt1E4HMiCzcEaZ66WyeQQZcJxa9ch44665Bf4hkNrp44qopsF89cKDXDxPfZVMrcn9QRMsWRD4M8z2tXGYyAyKo6kgP_K4nAuN8rGcdn4DmoXA"

        #else :
            #
            print( "Aaron - Request Data is ...")
            print( request.data )

            encoded_jwt=request.data
            #encoded_jwt = "eyJraWQiOiI5NklwcXhGOSIsImFsZyI6IlJTMjU2In0.eyJkYXRhIjoie1wiZGF0YVwiOlwie1xcbiAgXFxcImlkXFxcIiA6IFxcXCI5NWMyZjg3ZC1hZTc4LTRkZjktYWEyMS05NTE4OTIzMWQ2ZjdcXFwiLFxcbiAgXFxcImVudGl0eUZxZG5cXFwiIDogXFxcIndpeC5jcm0uaW5ib3gudjIubWVzc2FnZVxcXCIsXFxuICBcXFwic2x1Z1xcXCIgOiBcXFwibWVzc2FnZV9zZW50X3RvX2J1c2luZXNzXFxcIixcXG4gIFxcXCJlbnRpdHlJZFxcXCIgOiBcXFwiMTY0MDc3MTY2NzA5MTIxM1xcXCIsXFxuICBcXFwiYWN0aW9uRXZlbnRcXFwiIDoge1xcbiAgICBcXFwiYm9keVxcXCIgOiB7XFxuICAgICAgXFxcImNvbnZlcnNhdGlvbklkXFxcIiA6IFxcXCI1ZjY1MTY0Zi1iMzczLTNjYjktYmUyZS1mMWZkYzAwYzg2YTlcXFwiLFxcbiAgICAgIFxcXCJtZXNzYWdlXFxcIiA6IHtcXG4gICAgICAgIFxcXCJ0YXJnZXRDaGFubmVsc1xcXCIgOiBbIF0sXFxuICAgICAgICBcXFwiZGlyZWN0aW9uXFxcIiA6IFxcXCJQQVJUSUNJUEFOVF9UT19CVVNJTkVTU1xcXCIsXFxuICAgICAgICBcXFwiaWRcXFwiIDogXFxcIjE2NDA3NzE2NjcwOTEyMTNcXFwiLFxcbiAgICAgICAgXFxcInNlcXVlbmNlXFxcIiA6IFxcXCIxNjQwNzcxNjY3MDkxMjEzXFxcIixcXG4gICAgICAgIFxcXCJjb250ZW50XFxcIiA6IHtcXG4gICAgICAgICAgXFxcInByZXZpZXdUZXh0XFxcIiA6IFxcXCJKb0pvIERvZSBtYWRlIGFuIGFwcG9pbnRtZW50XFxcIixcXG4gICAgICAgICAgXFxcImZvcm1cXFwiIDoge1xcbiAgICAgICAgICAgIFxcXCJ0aXRsZVxcXCIgOiBcXFwiTmV3IFNwYSBBcHBvaW50bWVudFxcXCIsXFxuICAgICAgICAgICAgXFxcImRlc2NyaXB0aW9uXFxcIiA6IFxcXCJKb0pvIERvZSBtYWRlIGFuIGFwcG9pbnRtZW50XFxcIixcXG4gICAgICAgICAgICBcXFwiZmllbGRzXFxcIiA6IFsge1xcbiAgICAgICAgICAgICAgXFxcIm5hbWVcXFwiIDogXFxcIkZpcnN0IE5hbWVcXFwiLFxcbiAgICAgICAgICAgICAgXFxcInZhbHVlXFxcIiA6IFxcXCJKb0pvXFxcIlxcbiAgICAgICAgICAgIH0sIHtcXG4gICAgICAgICAgICAgIFxcXCJuYW1lXFxcIiA6IFxcXCJMYXN0IE5hbWVcXFwiLFxcbiAgICAgICAgICAgICAgXFxcInZhbHVlXFxcIiA6IFxcXCJEb2VcXFwiXFxuICAgICAgICAgICAgfSwge1xcbiAgICAgICAgICAgICAgXFxcIm5hbWVcXFwiIDogXFxcIlRyZWF0bWVudHNcXFwiLFxcbiAgICAgICAgICAgICAgXFxcInZhbHVlXFxcIiA6IFxcXCJNYXNzYWdlLCBNdWQgQmF0aCwgRmFjaWFsXFxcIlxcbiAgICAgICAgICAgIH0sIHtcXG4gICAgICAgICAgICAgIFxcXCJuYW1lXFxcIiA6IFxcXCJBcHBvaW50bWVudCBEYXRlXFxcIixcXG4gICAgICAgICAgICAgIFxcXCJ2YWx1ZVxcXCIgOiBcXFwiTWF5IDksIDIwMjFcXFwiXFxuICAgICAgICAgICAgfSBdLFxcbiAgICAgICAgICAgIFxcXCJtZWRpYVxcXCIgOiBbIHtcXG4gICAgICAgICAgICAgIFxcXCJpbWFnZVxcXCIgOiB7XFxuICAgICAgICAgICAgICAgIFxcXCJ1cmxcXFwiIDogXFxcImh0dHBzOi8vc3RhdGljLndpeHN0YXRpYy5jb20vbWVkaWEvZjkzZTNkNjMzZTc5OTIxZjE0MzMwZjE5MTFmYzExMzkuanBnL3YxL2ZpbGwvd18xMjAwLGhfNzk4LGFsX2MscV84NSx1c21fMC42Nl8xLjAwXzAuMDEvZjkzZTNkNjMzZTc5OTIxZjE0MzMwZjE5MTFmYzExMzkud2VicFxcXCIsXFxuICAgICAgICAgICAgICAgIFxcXCJ3aWR0aFxcXCIgOiAxMjAwLjAsXFxuICAgICAgICAgICAgICAgIFxcXCJoZWlnaHRcXFwiIDogNzk4LjBcXG4gICAgICAgICAgICAgIH1cXG4gICAgICAgICAgICB9IF1cXG4gICAgICAgICAgfVxcbiAgICAgICAgfSxcXG4gICAgICAgIFxcXCJzZW5kZXJcXFwiIDoge1xcbiAgICAgICAgICBcXFwiY29udGFjdElkXFxcIiA6IFxcXCI4OTBhMzgxNi04NWI0LTQ0YWItOTA4NS01MjQ5NzJhODUwZWZcXFwiXFxuICAgICAgICB9LFxcbiAgICAgICAgXFxcImFwcElkXFxcIiA6IFxcXCJhMGMzODY3MC02ODQ1LTQxZTAtOGY0MS04NWE2MDU0Y2NkOThcXFwiLFxcbiAgICAgICAgXFxcInZpc2liaWxpdHlcXFwiIDogXFxcIkJVU0lORVNTXFxcIixcXG4gICAgICAgIFxcXCJzb3VyY2VDaGFubmVsXFxcIiA6IFxcXCJVTktOT1dOX0NIQU5ORUxfVFlQRVxcXCIsXFxuICAgICAgICBcXFwiYmFkZ2VzXFxcIiA6IFsgXSxcXG4gICAgICAgIFxcXCJjcmVhdGVkRGF0ZVxcXCIgOiBcXFwiMjAyMS0xMi0yOVQwOTo1NDoyNy4wOTFaXFxcIlxcbiAgICAgIH1cXG4gICAgfVxcbiAgfSxcXG4gIFxcXCJldmVudFRpbWVcXFwiIDogXFxcIjIwMjEtMTItMjlUMDk6NTQ6MjcuMjcyODIzWlxcXCIsXFxuICBcXFwidHJpZ2dlcmVkQnlBbm9ueW1pemVSZXF1ZXN0XFxcIiA6IGZhbHNlXFxufSBcIixcImluc3RhbmNlSWRcIjpcIjcxNTFhMDRkLWFkZGMtNDZiYi1hNTZkLTU5YzkxNjJiNTZjNlwiLFwiZXZlbnRUeXBlXCI6XCJ3aXguY3JtLmluYm94LnYyLm1lc3NhZ2VfbWVzc2FnZV9zZW50X3RvX2J1c2luZXNzXCJ9IiwiaWF0IjoxNjg1Mjg2NjIyLCJleHAiOjE2ODg4ODY2MjJ9.ngR_fgybMhg_u2FnAyEziHNVdtfEIl1SYKy1E2L1LGimDCgkRldHetvr9vbK16emIW1_M7lFMyDC6VMt-MWwn45VY2zipT22ueB_ZFZ3hvOa2dEgyLjzBwmBM837eInEiHzarsApiMpimxFEiq_xm14hWbkXZ6lEbnb_PzixYEGAVH4tLWDbWa8bXdhOW6fenhk1OR-lBMAcfDFY4adAT1ZxKLJY21H0WbJcFAD0pt1E4HMiCzcEaZ66WyeQQZcJxa9ch44665Bf4hkNrp44qopsF89cKDXDxPfZVMrcn9QRMsWRD4M8z2tXGYyAyKo6kgP_K4nAuN8rGcdn4DmoXA"

             #decoded_jwt = jwt.decode(encoded_jwt, secret, algorithms=["RS256"])
            #decoded_jwt.dump()


            # console.log('webhook event data after verification:', prettyData);
            #print( 'webhook event data after verification:' + prettyData )
            # incomingWebhooks.push({body: prettyData, headers: req.headers});
            # res.send(req.body);

            # console.log('got webhook event from Wix!', req.body);
            print( 'got webhook event from Wix!' )

            # console.log("===========================");
            print( '===========================' )

            # const data = jwt.verify(req.body, PUBLIC_KEY);
            data = jwt.decode(encoded_jwt, secret, algorithms=["RS256"])

            # const parsedData =  JSON.parse(data.data);
            parsed_data = json.loads( data['data'] )

            # const prettyData = {...data, data: {...parsedData, data: JSON.parse(parsedData.data)}};
            pretty_data = json.loads( parsed_data['data'] )

            print( pretty_data )

            if pretty_data[ 'actionEvent' ]['body']["message"]["content"]["previewText"] :

                preview_text = pretty_data[ 'actionEvent' ]['body']["message"]["content"]["previewText"]

                requests_list.append( preview_text )

                print( "preview_text is " + preview_text )
                # save_message( database, preview_text )

            # Update the lists CSV file.
            csv_controller.write_csv( 'requests.csv', requests_list )
            # requests_list = get_message( database )

    # If the user submitted a GET request...
    if request.method == 'GET':

        # Assign the value to the component_id variable if the GET request provided either the 'origCompId' (editor) or 
        # the 'viewerCompId' (front-end) component ID.
        component_id = request.args.get( 'origCompId' ) if request.args.get( 'origCompId' ) else request.args.get( 'viewerCompId' )

    # Edit existing componenents
    for component in widget_component_sliders :

        if component[0] == component_id :

            selected_widget_component = component


    slider_offset = int( selected_widget_component[2] )/100
    #
    return render_template( 'widget-slider.html',
        text_variable = text_variable,
        ejtext = preview_text,
        requests_list = requests_list,
        component_id = component_id,
        components = widget_component_sliders,
        component = selected_widget_component,
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
    