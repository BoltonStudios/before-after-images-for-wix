"""
Models for my Flask app for Wix.
"""
# Flask imports
from sqlalchemy.sql import func

# Local imports.
from database import db

# Define the user table class.
class Instance( db.Model ):

    # pylint: disable=too-many-instance-attributes
    # Eight is reasonable in this case.

    """
    Class to define the User table.
    """
    instance_id: db.Column              = db.Column( db.String( 255 ), primary_key = True, unique = True )
    site_id: db.Column                  = db.Column( db.String( 255 ), unique = True )
    extensions                          = db.relationship( 'Extension', backref = 'instance' )
    refresh_token: db.Column            = db.Column( db.String( 2000 ), unique = True )
    is_free: db.Column                  = db.Column( db.Boolean, default = True )
    did_cancel: db.Column               = db.Column( db.Boolean, default = False )
    expires_on: db.Column               = db.Column( db.DateTime )
    extension_count: db.Column          = db.Column( db.Integer )
    extension_count_limit: db.Column    = db.Column( db.Integer, default = 499 )
    created_at: db.Column               = db.Column( db.DateTime( timezone = True ),
                                        server_default = func.now() )

    def __repr__( self ):
        return f'<instance { self.instance_id }>'

# Define the slider extension table class.
class Extension( db.Model ):

    # pylint: disable=too-many-instance-attributes
    # Eight is reasonable in this case.

    """
    Class to define the Slider extension table.
    """
    extension_id: db.Column                 = db.Column( db.String( 255 ), primary_key = True, unique = True )
    instance_id: db.Column                  = db.Column( db.String( 255 ), db.ForeignKey( Instance.instance_id ) )
    before_image: db.Column                 = db.Column( db.String( 1000 ) )
    before_image_thumbnail: db.Column       = db.Column( db.String( 1000 ) )
    before_label_text: db.Column            = db.Column( db.String( 30 ) )
    before_alt_text: db.Column              = db.Column( db.String( 60 ) )
    after_image: db.Column                  = db.Column( db.String( 1000 ) )
    after_image_thumbnail: db.Column        = db.Column( db.String( 1000 ) )
    after_label_text: db.Column             = db.Column( db.String( 30 ) )
    after_alt_text: db.Column               = db.Column( db.String( 60 ) )
    offset: db.Column                       = db.Column( db.Integer )
    offset_float: db.Column                 = db.Column( db.Float )
    is_vertical: db.Column                  = db.Column( db.Boolean, default = False )
    is_dark: db.Column                      = db.Column( db.Boolean, default = False )
    mouseover_action: db.Column             = db.Column( db.Integer, default = 1 )
    handle_animation: db.Column             = db.Column( db.Integer, default = 0 )
    handle_border_color: db.Column          = db.Column( db.String( 20 ), default = '#BBBBBB' )
    is_move_on_click_enabled: db.Column     = db.Column( db.Boolean, default = False )
    created_at: db.Column                   = db.Column( db.DateTime( timezone = True ),
                                                server_default = func.now() )

    def __repr__( self ):
        return f'<slider { self.extension_id } in { self.instance_id }>'
