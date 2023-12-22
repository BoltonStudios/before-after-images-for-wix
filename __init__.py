# Python imports
import os

# Flask imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_migrate import Migrate

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

# Import our models.
from .models import User, Extension

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