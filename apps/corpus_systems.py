import os
from flask import Flask
from blueprints import dataApi
from flask_cors import CORS

# choose apps from blueprints to register
def register_blueprints(app: Flask):
    app.register_blueprint(dataApi.bp)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    app.config["JSON_AS_ASCII"] = False

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    register_blueprints(app)
    CORS(app, supports_credentials=True)
    return app