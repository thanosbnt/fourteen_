from flask import Flask, g, render_template, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api
from extensions import db
from settings.config import BaseConfig
from api.errors import InvalidUsage
from api.resources import StartStream

import logging


def create_before_request(app):
    def before_request():
        g.db = db
    return before_request


def create_app(**config_overrides):

    logger = logging.getLogger(__name__)
    logger.info('app starts...')


    app = Flask(__name__, static_folder="./static/dist",
                template_folder="./static/src")

    app.config.from_object(BaseConfig)

    if config_overrides:
        app.config.update(config_overrides)

    db.init_app(app)
    db.app = app

    migrate = Migrate(app, db)
    CORS(app)
    api = Api(app)
    # from backend.main import models

    # db.create_all()
    # app.before_request(create_before_request(app))

    # error handling
    @app.errorhandler(InvalidUsage)
    def handle_invalid_usage(error):
        """ 
        Handles invalid api use
        """
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response


    # template resources
    @app.route('/')
    def index():
        """ 
        Displays the index page accessible at '/'
        """
        return render_template('index.html')

    api.add_resource(StartStream, '/api/start')  # get

    return app
    