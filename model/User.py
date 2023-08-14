# pylint: disable=not-callable
# pylint: disable=invalid-name
"""
Define the class for a Slider Component.
"""
from dataclasses import dataclass
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

@dataclass
class User( db.Model ):

    # pylint: disable=too-many-instance-attributes
    # Eight is reasonable in this case.

    """
    Class to define the User table.
    """
    site_id: db.Column      = db.Column( db.String( 80 ), primary_key = True, unique = True )
    created_at: db.Column   = db.Column( db.DateTime( timezone = True ),
                                        server_default = func.now() )

    def __repr__( self ):
        return f'<slider { self.created_at }>'
