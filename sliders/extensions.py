# Python imports

# Flask imports
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Create a database object.
db = SQLAlchemy()

# Create a Migrate object.
migrate = Migrate()