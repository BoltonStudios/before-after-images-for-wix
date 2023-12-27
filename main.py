"""
A Flask app for Wix.
"""
from flask import Flask, render_template

app = Flask(__name__)

#
from . import sliders
from sliders  import views

if __name__ == "__main__":
    
    app.run()