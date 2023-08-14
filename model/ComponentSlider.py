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
class ComponentSlider( db.Model ):

    # pylint: disable=too-many-instance-attributes
    # Eight is reasonable in this case.

    """
    Class to define the Slider Component table.
    """
    component_id: db.Column = db.Column( db.String( 80 ), primary_key = True, unique = True )
    site_id: db.Column      = db.Column( db.String( 80 ), db.ForeignKey( User.site_id ) )
    before_image: db.Column = db.Column( db.String( 1000 ) )
    after_image: db.Column  = db.Column( db.String( 1000 ) )
    offset: db.Column       = db.Column( db.Integer )
    offset_float: db.Column = db.Column( db.Float )
    created_at: db.Column   = db.Column( db.DateTime( timezone = True ),
                                        server_default = func.now() )

    def __repr__( self ):
        return f'<slider { self.created_at }>'
