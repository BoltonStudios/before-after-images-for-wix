"""
Set up database for my Flask app for Wix.
"""
# Python imports
import os
import sys
from dotenv import load_dotenv

# Flask imports
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Create a database object.
db = SQLAlchemy()

# Create a Migrate object.
migrate = Migrate()

# Define a base directory as the current directory.
basedir = os.path.abspath( os.path.dirname( __file__ ) )

# Load environment variables from .env file
load_dotenv()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG               = os.getenv( "DEBUG", "False" ) == "True"
DEVELOPMENT_MODE    = os.getenv( "DEVELOPMENT_MODE", "False" ) == "True"
DATABASE_USERNAME   = os.getenv( "DATABASE_USERNAME" )
DATABASE_PASSWORD   = os.getenv( "DATABASE_PASSWORD" )
DATABASE_HOST       = os.getenv( "DATABASE_HOST" )
DATABASE_PORT       = os.getenv( "DATABASE_PORT" )
DATABASE_NAME       = os.getenv( "DATABASE_NAME" )

# Define the database URI to specify the database with which to connect.
if DEVELOPMENT_MODE is True:

    # SQL Lite for local development.
    db_uri = 'postgresql://' + DATABASE_USERNAME + ':' + DATABASE_PASSWORD + '@' + DATABASE_HOST + ':' + DATABASE_PORT + '/' + DATABASE_NAME
    
elif len( sys.argv ) > 0 and sys.argv[1] != 'static':

    if os.getenv( "DATABASE_URL", None ) is None:

        raise ValueError( "DATABASE_URL environment variable not defined" )
    
    # Defined in the cloud hosting production environment 
    db_uri = os.environ.get( "DATABASE_URL" )