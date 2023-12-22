"""
Models for my Flask app for Wix.
"""
# Flask imports
from sqlalchemy.sql import func

# Local imports.
from . import db

# Define the user table class.
class User( db.Model ):

    # pylint: disable=too-many-instance-attributes
    # Eight is reasonable in this case.

    """
    Class to define the User table.
    """
    instance_id: db.Column      = db.Column( db.String( 200 ), primary_key = True, unique = True )
    site_id: db.Column          = db.Column( db.String( 200 ), unique = True )
    extensions                  = db.relationship( 'Extension', backref = 'user' )
    refresh_token: db.Column    = db.Column( db.String( 200 ) ) # Not unique because...?
    is_free: db.Column          = db.Column( db.Boolean )
    created_at: db.Column       = db.Column( db.DateTime( timezone = True ),
                                        server_default = func.now() )

    def __repr__( self ):
        return f'<user { self.instance_id }>'

# Define the slider extension table class.
class Extension( db.Model ):

    # pylint: disable=too-many-instance-attributes
    # Eight is reasonable in this case.

    """
    Class to define the Slider extension table.
    """
    extension_id: db.Column                 = db.Column( db.String( 80 ), primary_key = True, unique = True )
    instance_id: db.Column                  = db.Column( db.String( 80 ), db.ForeignKey( User.instance_id ) )
    before_image: db.Column                 = db.Column( db.String( 1000 ) )
    before_label_text: db.Column            = db.Column( db.String( 1000 ) )
    before_alt_text: db.Column              = db.Column( db.String( 1000 ) )
    after_image: db.Column                  = db.Column( db.String( 1000 ) )
    after_label_text: db.Column             = db.Column( db.String( 1000 ) )
    after_alt_text: db.Column               = db.Column( db.String( 1000 ) )
    offset: db.Column                       = db.Column( db.Integer )
    offset_float: db.Column                 = db.Column( db.Float )
    is_vertical: db.Column                  = db.Column( db.Boolean )
    mouseover_action: db.Column             = db.Column( db.Integer, default = 1 )
    handle_animation: db.Column             = db.Column( db.Integer, default = 0 )
    is_move_on_click_enabled: db.Column     = db.Column( db.Boolean )
    created_at: db.Column                   = db.Column( db.DateTime( timezone = True ),
                                                server_default = func.now() )

    def __repr__( self ):
        return f'<slider { self.extension_id } in { self.instance_id }>'