from flask import Flask, g, render_template, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api
from extensions import db
from settings.config import BaseConfig
from api.errors import InvalidUsage
from api.resources import StartStream, Test
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import time
import random
from flask import request, jsonify
from flask_restful import Resource, reqparse, inputs
import requests
from pydub import AudioSegment
import pyOSC3
import io
import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from shapely.geometry import Point


import logging
logger = logging.getLogger(__name__)


def create_before_request(app):
    def before_request():
        g.db = db
    return before_request


def create_app(**config_overrides):

    logger = logging.getLogger(__name__)
    logger.info('app starts...')

    app = Flask(__name__, static_folder="./static/dist",
                template_folder="./static/src")

    limiter = Limiter(key_func=get_remote_address)
    limiter.init_app(app)

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

    def ckdnearest(gdA, gdB):
        nA = np.array(list(gdA.geometry.apply(lambda x: (x.x, x.y))))
        nB = np.array(list(gdB.geometry.apply(lambda x: (x.x, x.y))))
        btree = cKDTree(nB)
        dist, idx = btree.query(nA, k=1)
        gdA['dist'] = dist
        return gdA[gdA.dist == gdA.dist.min()]

    def x(row):
        try:
            x = row[0]
            return x
        except Exception:
            pass

    def y(row):
        try:
            x = row[1]
            return x
        except Exception:
            pass

    # error handling
    @app.errorhandler(InvalidUsage)
    def handle_invalid_usage(error):
        """ 
        Handles invalid api use
        """
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    df = pd.read_csv('stations.csv')
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(
        df.place_geo_x, df.place_geo_y))

    @app.route('/api', methods=["GET"])
    @limiter.limit("1 per 20second")
    def send_station():

        logger.info(request.args['x'])

        gpd1 = gdf
        gpd2 = gpd.GeoDataFrame([['test', Point(float(request.args['x']), float(
            request.args['y']))]], columns=['Place', 'geometry'])

        radio_list = random.choice(ckdnearest(gpd1, gpd2)[
                                   ['mp3', 'country', 'place_name', 'name']].values)

        logger.info(radio_list[0])

        client = pyOSC3.OSCClient()
        client.connect(('10.5.0.11', 57120))

        radio = radio_list[0]
        msg = pyOSC3.OSCMessage()
        msg.setAddress("/start")
        msg.append(radio)
        client.send(msg)
        return np.array2string(radio_list[1:]).replace('[', '').replace(']', '').replace("'", '')

        # StartStream.method_decorators.append(limiter.limit('1 per 15second'))
        # Test.method_decorators.append(limiter.limit('1 per day'))

        # api.add_resource(StartStream, '/api/start')  # get
        # api.add_resource(Test, '/api/test')  # get

    return app
