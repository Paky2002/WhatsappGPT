from flask import Blueprint

# Import the blueprint for Waapi
from .waapi import waapi
from .gpt_assistant import gpt_assistant_bp
from .main import main_bp
from .test import test_bp

def register_routes(app):
    # Register the Waapi blueprint
    app.register_blueprint(main_bp, url_prefix="/main")
    app.register_blueprint(waapi, url_prefix="/waapi")
    app.register_blueprint(gpt_assistant_bp, url_prefix="/gpt_assistant")
    app.register_blueprint(test_bp, url_prefix="/test")
