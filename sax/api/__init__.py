# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from __future__ import annotations

from flasgger import Swagger
from flask import Flask

from .exceptions.badrequest import BadRequestException
from .exceptions.notfound import NotFoundException
from .exceptions.validation import ValidationException
from .routes.sax_routes import sax_routes
from .state.state import State


def create_app():
    # Create and configure app 
    app = Flask(__name__)    
    app.state = State()

    # Register Routes    
    app.register_blueprint(sax_routes)
    
    @app.errorhandler(BadRequestException)
    def handle_bad_request(err):
        return {"message": str(err)}, 400

    @app.errorhandler(ValidationException)
    def handle_validation_exception(err):
        return {"message": str(err)}, 422

    @app.errorhandler(NotFoundException)
    def handle_not_found_exception(err):
        return {"message": str(err)}, 404
    
    Swagger(app)

    return app

 
 